import customtkinter as ctk

class BrandSelectScreen(ctk.CTkFrame):
    """
    Screen to select a brand to simulate.
    Extensible structure, currently featuring Megacoffee.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=3)
        self.grid_rowconfigure(2, weight=1)

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, pady=30, sticky="nsew")
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            header_frame, 
            text="연습할 브랜드를 선택하세요", 
            font=ctk.CTkFont(family="Malgun Gothic", size=36, weight="bold"),
            text_color="#333333"
        )
        title_label.grid(row=0, column=0, pady=10)

        subtitle_label = ctk.CTkLabel(
            header_frame, 
            text="원하시는 카페 간판을 누르면 주문 연습이 시작됩니다.", 
            font=ctk.CTkFont(family="Malgun Gothic", size=20),
            text_color="#666666"
        )
        subtitle_label.grid(row=1, column=0)

        # Brand grid selection
        brand_frame = ctk.CTkFrame(self, fg_color="transparent")
        brand_frame.grid(row=1, column=0, padx=40, pady=10, sticky="nsew")
        brand_frame.grid_columnconfigure(0, weight=1)
        brand_frame.grid_columnconfigure(1, weight=1) # Prepared for a second brand in the future
        
        # Mega Coffee Button
        # Mega Coffee signature color: Yellow/Black
        mega_btn = ctk.CTkButton(
            brand_frame,
            text="[ 메가커피 (MEGA COFFEE) ]\n\n[커피 연습 가능]",
            font=ctk.CTkFont(family="Malgun Gothic", size=28, weight="bold"),
            height=150,
            fg_color="#FFCC00",       # Megacoffee Yellow
            text_color="#000000",     # Black text for high contrast
            hover_color="#E6B800",
            border_width=2,
            border_color="#000000",
            command=lambda: self.select_brand("메가커피")
        )
        mega_btn.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Future Brand Placeholder (greyed out or coming soon)
        other_btn = ctk.CTkButton(
            brand_frame,
            text="다른 브랜드\n\n[준비 중]",
            font=ctk.CTkFont(family="Malgun Gothic", size=24, weight="bold"),
            height=150,
            fg_color="#E0E0E0",
            text_color="#888888",
            state="disabled",
            command=None
        )
        other_btn.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Bottom navigation
        back_btn = ctk.CTkButton(
            self,
            text="◀ 처음 화면으로 돌아가기 (이전)",
            font=ctk.CTkFont(family="Malgun Gothic", size=22, weight="bold"),
            height=60,
            fg_color="#757575",
            hover_color="#616161",
            command=self.go_back
        )
        back_btn.grid(row=2, column=0, padx=40, pady=30, sticky="ew")

    def select_brand(self, brand_name):
        self.controller.start_kiosk_simulation(brand_name)

    def go_back(self):
        self.controller.show_frame("MainScreen")
