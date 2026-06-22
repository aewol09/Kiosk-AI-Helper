import customtkinter as ctk
import sys

class MainScreen(ctk.CTkFrame):
    """
    Landing screen of the Kiosk Helper application.
    Provides start, guide, exit buttons, and shows summary learning statistics.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=2)
        self.grid_rowconfigure(2, weight=1)

        # 1. Header (Title/Logo)
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, pady=40, sticky="nsew")
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            header_frame, 
            text="[ 키오스크 도우미 ]", 
            font=ctk.CTkFont(family="Malgun Gothic", size=48, weight="bold"),
            text_color="#FFA500" # High contrast warm orange
        )
        title_label.grid(row=0, column=0, pady=(10, 5))

        subtitle_label = ctk.CTkLabel(
            header_frame, 
            text="천천히 배우고 쉽게 결제하는 연습 프로그램", 
            font=ctk.CTkFont(family="Malgun Gothic", size=24),
            text_color="#555555"
        )
        subtitle_label.grid(row=1, column=0)

        # 2. Main buttons (Large and high-contrast)
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=1, column=0, padx=40, pady=10, sticky="nsew")
        button_frame.grid_columnconfigure(0, weight=1)
        
        # Start button
        start_btn = ctk.CTkButton(
            button_frame,
            text="▶ 연습 시작하기",
            font=ctk.CTkFont(family="Malgun Gothic", size=32, weight="bold"),
            height=80,
            fg_color="#4CAF50",       # Green color
            hover_color="#45a049",
            command=self.start_practice
        )
        start_btn.grid(row=0, column=0, pady=15, sticky="ew")

        # Instruction button
        guide_btn = ctk.CTkButton(
            button_frame,
            text="? 사용 방법 배우기",
            font=ctk.CTkFont(family="Malgun Gothic", size=28, weight="bold"),
            height=70,
            fg_color="#2196F3",       # Blue color
            hover_color="#0b7dda",
            command=self.show_how_to_use
        )
        guide_btn.grid(row=1, column=0, pady=15, sticky="ew")

        # Exit button
        exit_btn = ctk.CTkButton(
            button_frame,
            text="X 프로그램 종료",
            font=ctk.CTkFont(family="Malgun Gothic", size=24),
            height=60,
            fg_color="#f44336",       # Red color
            hover_color="#da190b",
            command=self.exit_app
        )
        exit_btn.grid(row=2, column=0, pady=15, sticky="ew")

        # 3. Footer / Stats Dashboard
        self.stats_frame = ctk.CTkFrame(self, fg_color="#F5F5F5", corner_radius=15, border_width=1, border_color="#DDDDDD")
        self.stats_frame.grid(row=2, column=0, padx=40, pady=(10, 30), sticky="nsew")
        self.stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.stats_frame.grid_rowconfigure(0, weight=1)

        self.update_stats()

    def update_stats(self):
        # Clear stats frame contents first (except configuration)
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        stats = self.controller.history_manager.get_summary_statistics()

        # Labels for Statistics dashboard
        total_lbl = ctk.CTkLabel(
            self.stats_frame,
            text=f"누적 연습 횟수\n{stats['total_sessions']}회",
            font=ctk.CTkFont(family="Malgun Gothic", size=18, weight="bold"),
            text_color="#333333"
        )
        total_lbl.grid(row=0, column=0, padx=10, pady=15)

        avg_mistake_lbl = ctk.CTkLabel(
            self.stats_frame,
            text=f"평균 실수 횟수\n{stats['avg_mistakes']}회",
            font=ctk.CTkFont(family="Malgun Gothic", size=18, weight="bold"),
            text_color="#d32f2f"
        )
        avg_mistake_lbl.grid(row=0, column=1, padx=10, pady=15)

        avg_time_lbl = ctk.CTkLabel(
            self.stats_frame,
            text=f"평균 소요 시간\n{stats['avg_duration']}초",
            font=ctk.CTkFont(family="Malgun Gothic", size=18, weight="bold"),
            text_color="#1976D2"
        )
        avg_time_lbl.grid(row=0, column=2, padx=10, pady=15)

    def start_practice(self):
        self.controller.show_frame("BrandSelectScreen")

    def show_how_to_use(self):
        self.controller.show_guide_popup()

    def exit_app(self):
        sys.exit()
