import os
import customtkinter as ctk
from models.order_manager import OrderManager
from models.menu_translator import MenuTranslator
from models.history_manager import HistoryManager
from helpers.voice_assistant import VoiceAssistant
from views.main_screen import MainScreen
from views.brand_select_screen import BrandSelectScreen
from views.kiosk_simulator import KioskSimulator

class KioskHelperApp(ctk.CTk):
    """
    Main application controller (App class) following the MVC architecture.
    Manages global state, frames switching, and popup dialogs.
    """
    def __init__(self):
        super().__init__()

        # Configure window settings
        self.title("Kiosk Helper - 어르신을 위한 키오스크 학습 도우미")
        self.geometry("960x720")
        self.resizable(False, False)

        # Set default styling (Light Mode for better readability by seniors)
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")

        # Initialize Models & Helpers
        self.history_manager = HistoryManager()
        self.menu_translator = MenuTranslator()
        self.order_manager = OrderManager()
        self.voice_assistant = VoiceAssistant()

        # Master container for views
        self.container = ctk.CTkFrame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Initialize dictionary of frames
        self.frames = {}
        
        # Define available screens
        for F in (MainScreen, BrandSelectScreen, KioskSimulator):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            # put all screens in the same location;
            # the one on the top of the stacking order will be the visible one.
            frame.grid(row=0, column=0, sticky="nsew")

        # Show initial screen
        self.show_frame("MainScreen")

    def show_frame(self, page_name):
        """
        Bring the specified frame to the front.
        """
        frame = self.frames[page_name]
        frame.tkraise()

    def start_kiosk_simulation(self, brand_name):
        """
        Initialize order manager for the chosen brand and switch to simulator.
        """
        self.order_manager.brand = brand_name
        self.show_frame("KioskSimulator")
        # Trigger simulation setup
        sim_frame = self.frames["KioskSimulator"]
        sim_frame.start_practice()

    def refresh_main_screen_stats(self):
        """
        Trigger stats redraw on the landing screen.
        """
        main_screen = self.frames["MainScreen"]
        main_screen.update_stats()

    def show_guide_popup(self):
        """
        Shows a beautiful, high-contrast, scrollable guidance window explaining the features.
        """
        guide_window = ctk.CTkToplevel(self)
        guide_window.title(" 키오스크 도우미 사용 방법")
        guide_window.geometry("700x550")
        guide_window.resizable(False, False)
        guide_window.transient(self) # Keep on top of main window
        guide_window.grab_set()

        guide_window.grid_columnconfigure(0, weight=1)
        guide_window.grid_rowconfigure(0, weight=1)
        guide_window.grid_rowconfigure(1, weight=0)

        # Content Textbox
        guide_text = ctk.CTkTextbox(
            guide_window,
            font=ctk.CTkFont(family="Malgun Gothic", size=18),
            wrap="word",
            border_width=2,
            border_color="#2196F3"
        )
        guide_text.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        instructions = (
            " [사용 방법 안내]\n\n"
            "저희 '키오스크 도우미'는 키오스크 조작이 낯선 어르신들께서 실제 매장과 흡사한 화면으로 마음껏 연습하실 수 있도록 개발되었습니다.\n\n"
            "* 주요 기능 안내:\n\n"
            "1. - 반짝이는 빨간 테두리 가이드\n"
            "  - 화면 중간중간에 다음에 꼭 눌러야 할 단추를 빨간색(또는 노란색) 점선 테두리와 화살표로 짚어드립니다. 가이드를 따라 천천히 눌러보세요.\n\n"
            "2.  편리한 음성 주문\n"
            "  - 마이크가 연결되어 있다면, '마이크 켜고 말하기' 단추를 누르고 '아이스 아메리카노 주문해줘' 혹은 '포장해줘' 처럼 편리하게 음성으로 기계를 작동할 수 있습니다.\n"
            "  - 만약 마이크가 작동하지 않더라도 오른쪽에 있는 '말하기 예시' 단추들을 눌러서 음성 주문을 간편하게 테스트해보실 수 있습니다.\n\n"
            "3.  쉬운 한국어 메뉴 번역기\n"
            "  - 아인슈페너, 플랫화이트 등 낯선 외국어 메뉴 이름이 어렵다면 화면의 해당 메뉴 단추를 눌러보세요. 오른쪽에 쉬운 한글 설명이 나타납니다.\n\n"
            "4.  학습 통계 기록\n"
            "  - 연습이 끝나면 소요 시간과 버튼 조작 실수를 세어 영수증 형식으로 보여주고, 메인 화면에 평균 통계를 누적하여 기록해 줍니다. 반복해서 연습하며 실수를 줄여 보세요!\n\n"
            " 천천히 한 번씩 마우스로 누르고 안내 음성에 귀 기울여 보세요!"
        )

        guide_text.insert("1.0", instructions)
        guide_text.configure(state="disabled")

        # Close Button
        close_btn = ctk.CTkButton(
            guide_window,
            text="확인했습니다 (닫기)",
            font=ctk.CTkFont(family="Malgun Gothic", size=20, weight="bold"),
            height=50,
            fg_color="#2196F3",
            hover_color="#0b7dda",
            command=guide_window.destroy
        )
        close_btn.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

if __name__ == "__main__":
    app = KioskHelperApp()
    app.mainloop()
