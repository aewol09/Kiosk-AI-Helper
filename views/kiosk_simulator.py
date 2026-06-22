import os
import time
import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import messagebox

class KioskSimulator(ctk.CTkFrame):
    """
    Main simulator screen. Splits into:
    - Left side: Interactive Kiosk Canvas (displays mega-kiosk images and overlays)
    - Right side: AI Character Guidance & Voice Assistant Panel
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Grid configuration
        self.grid_columnconfigure(0, weight=3) # Kiosk Canvas (540px wide)
        self.grid_columnconfigure(1, weight=1) # AI Character panel
        self.grid_rowconfigure(0, weight=1)

        # Initialize attributes
        self.flash_state = True
        self.flash_job = None
        self.voice_listening = False
        
        # Load and resize images (Original: 1080x1350, Resized to: 540x675)
        self.kiosk_width = 540
        self.kiosk_height = 675
        self.scale_factor = 0.5

        self.kiosk_images = {}
        for i in range(1, 6):
            path = f"images/mega-kiosk-{i}.png"
            if os.path.exists(path):
                img = Image.open(path)
                img_res = img.resize((self.kiosk_width, self.kiosk_height), Image.Resampling.LANCZOS)
                self.kiosk_images[i] = ImageTk.PhotoImage(img_res)
            else:
                print(f"Warning: {path} not found.")

        # --- LEFT SIDE: KIOSK DISPLAY PANEL ---
        self.kiosk_frame = ctk.CTkFrame(self, width=self.kiosk_width, height=self.kiosk_height, fg_color="black")
        self.kiosk_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.kiosk_frame.grid_propagate(False)

        # Canvas to display background image and draw overlays/highlights
        self.canvas = ctk.CTkCanvas(self.kiosk_frame, width=self.kiosk_width, height=self.kiosk_height, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # --- RIGHT SIDE: AI HELPER & ASSISTANT PANEL ---
        self.helper_frame = ctk.CTkFrame(self, fg_color="#F9F9F9", border_width=1, border_color="#DDDDDD")
        self.helper_frame.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
        self.helper_frame.grid_columnconfigure(0, weight=1)
        self.helper_frame.grid_rowconfigure(0, weight=0) # Title
        self.helper_frame.grid_rowconfigure(1, weight=1) # AI Character & Speech Bubble
        self.helper_frame.grid_rowconfigure(2, weight=0) # Menu Translator Panel
        self.helper_frame.grid_rowconfigure(3, weight=0) # Voice Assistant Panel

        # Title
        panel_title = ctk.CTkLabel(
            self.helper_frame,
            text="[ AI 도우미 선생님 ]",
            font=ctk.CTkFont(family="Malgun Gothic", size=24, weight="bold"),
            text_color="#FFA500"
        )
        panel_title.grid(row=0, column=0, pady=15)

        # AI Character & Speech Bubble
        char_frame = ctk.CTkFrame(self.helper_frame, fg_color="transparent")
        char_frame.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")
        char_frame.grid_columnconfigure(0, weight=1)
        char_frame.grid_rowconfigure(0, weight=1) # Bubble
        char_frame.grid_rowconfigure(1, weight=0) # Avatar

        # Bubble
        self.bubble_text = ctk.CTkTextbox(
            char_frame,
            font=ctk.CTkFont(family="Malgun Gothic", size=20, weight="bold"),
            text_color="#000000",
            fg_color="#FFF8DC", # Soft corn silk color
            border_width=2,
            border_color="#FFA500",
            wrap="word"
        )
        self.bubble_text.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        self.bubble_text.configure(state="disabled")

        # Character Avatar
        self.avatar_label = ctk.CTkLabel(
            char_frame,
            text="[도우미 바리스타]\n\"반짝이는 테두리를 천천히 눌러보세요!\"",
            font=ctk.CTkFont(family="Malgun Gothic", size=18, weight="bold"),
            text_color="#333333"
        )
        self.avatar_label.grid(row=1, column=0, pady=5)

        # Menu Translator Panel
        translator_frame = ctk.CTkFrame(self.helper_frame, fg_color="#F0F8FF", border_width=1, border_color="#ADD8E6", corner_radius=10)
        translator_frame.grid(row=2, column=0, padx=15, pady=10, sticky="ew")
        translator_frame.grid_columnconfigure(0, weight=1)

        trans_title = ctk.CTkLabel(
            translator_frame,
            text="[ 쉬운 한국어 번역기 (어려운 메뉴 번역) ]",
            font=ctk.CTkFont(family="Malgun Gothic", size=16, weight="bold"),
            text_color="#0066CC"
        )
        trans_title.grid(row=0, column=0, pady=(5, 2))

        self.trans_desc_label = ctk.CTkLabel(
            translator_frame,
            text="키오스크에서 생소한 메뉴 이름을 더블 클릭 하거나,\n음성으로 설명해달라고 하면 쉬운 말로 번역해 드려요.",
            font=ctk.CTkFont(family="Malgun Gothic", size=14),
            text_color="#555555",
            justify="center",
            wraplength=230
        )
        self.trans_desc_label.grid(row=1, column=0, pady=(2, 10))

        # Voice Assistant Panel
        voice_frame = ctk.CTkFrame(self.helper_frame, fg_color="#F5F5F5", border_width=1, border_color="#DDDDDD", corner_radius=10)
        voice_frame.grid(row=3, column=0, padx=15, pady=(5, 15), sticky="ew")
        voice_frame.grid_columnconfigure(0, weight=1)

        voice_title = ctk.CTkLabel(
            voice_frame,
            text="[ 말로 주문하기 (음성 인식) ]",
            font=ctk.CTkFont(family="Malgun Gothic", size=16, weight="bold"),
            text_color="#333333"
        )
        voice_title.grid(row=0, column=0, pady=(5, 2))

        self.mic_btn = ctk.CTkButton(
            voice_frame,
            text="마이크 켜고 말하기",
            font=ctk.CTkFont(family="Malgun Gothic", size=16, weight="bold"),
            fg_color="#9C27B0",
            hover_color="#7B1FA2",
            height=40,
            command=self.toggle_mic
        )
        self.mic_btn.grid(row=1, column=0, padx=15, pady=5, sticky="ew")


        # Voice Input Simulator (Typing fallback)
        sim_title = ctk.CTkLabel(
            voice_frame,
            text="또는 아래의 말하기 예시를 선택하세요:",
            font=ctk.CTkFont(family="Malgun Gothic", size=13),
            text_color="#666666"
        )
        sim_title.grid(row=2, column=0, pady=(5, 2))

        self.voice_entry = ctk.CTkEntry(
            voice_frame,
            placeholder_text="예: 아이스 아메리카노 주문해줘",
            font=ctk.CTkFont(family="Malgun Gothic", size=14)
        )
        self.voice_entry.grid(row=3, column=0, padx=15, pady=5, sticky="ew")
        self.voice_entry.bind("<Return>", lambda event: self.process_simulated_voice())

        # Suggested Speech phrases buttons
        phrase_frame = ctk.CTkFrame(voice_frame, fg_color="transparent")
        phrase_frame.grid(row=4, column=0, padx=15, pady=(5, 10), sticky="ew")
        phrase_frame.grid_columnconfigure((0, 1), weight=1)

        p1_btn = ctk.CTkButton(
            phrase_frame,
            text="아이스 아메리카노 주문해줘",
            font=ctk.CTkFont(family="Malgun Gothic", size=12),
            fg_color="#E0E0E0",
            text_color="#333333",
            hover_color="#CCCCCC",
            height=25,
            command=lambda: self.voice_entry_fill("아이스 아메리카노 주문해줘")
        )
        p1_btn.grid(row=0, column=0, padx=2, pady=2, sticky="ew")

        p2_btn = ctk.CTkButton(
            phrase_frame,
            text="샷 추가하고 주문담기 해줘",
            font=ctk.CTkFont(family="Malgun Gothic", size=12),
            fg_color="#E0E0E0",
            text_color="#333333",
            hover_color="#CCCCCC",
            height=25,
            command=lambda: self.voice_entry_fill("샷 추가하고 주문담기 해줘")
        )
        p2_btn.grid(row=0, column=1, padx=2, pady=2, sticky="ew")

        p3_btn = ctk.CTkButton(
            phrase_frame,
            text="포장하기로 선택해줘",
            font=ctk.CTkFont(family="Malgun Gothic", size=12),
            fg_color="#E0E0E0",
            text_color="#333333",
            hover_color="#CCCCCC",
            height=25,
            command=lambda: self.voice_entry_fill("포장하기로 선택해줘")
        )
        p3_btn.grid(row=1, column=0, padx=2, pady=2, sticky="ew")

        p4_btn = ctk.CTkButton(
            phrase_frame,
            text="신용카드로 결제할래",
            font=ctk.CTkFont(family="Malgun Gothic", size=12),
            fg_color="#E0E0E0",
            text_color="#333333",
            hover_color="#CCCCCC",
            height=25,
            command=lambda: self.voice_entry_fill("신용카드로 결제할래")
        )
        p4_btn.grid(row=1, column=1, padx=2, pady=2, sticky="ew")

    def voice_entry_fill(self, text):
        self.voice_entry.delete(0, "end")
        self.voice_entry.insert(0, text)
        self.process_simulated_voice()

    # --- SIMULATOR FLOW LOGIC ---

    def start_practice(self):
        self.controller.order_manager.start_session()
        self.update_screen()
        self.start_flashing()

    def set_guide_text(self, text):
        self.bubble_text.configure(state="normal")
        self.bubble_text.delete("1.0", "end")
        self.bubble_text.insert("1.0", text)
        self.bubble_text.configure(state="disabled")
        # Read guide text via TTS
        self.controller.voice_assistant.speak(text)

    def update_screen(self):
        self.canvas.delete("all")
        step = self.controller.order_manager.current_step

        # Step 4 is Eat-in / Take-out selection which is a custom screen
        if step == 4:
            self.draw_custom_step4_screen()
            self.update_guide()
            return

        # Load image for steps 1, 2, 3, 5, 6
        img_idx = step
        if step == 5:
            img_idx = 4
        elif step == 6:
            img_idx = 5

        bg_img = self.kiosk_images.get(img_idx)
        if bg_img:
            self.canvas.create_image(0, 0, image=bg_img, anchor="nw")

        # Step-specific dynamic text rendering (overlays)
        if step == 1:
            self.draw_step1_overlays()
        elif step == 2:
            self.draw_step2_overlays()
        elif step == 3:
            self.draw_step3_overlays()
        elif step == 6:
            self.draw_step6_overlays()

        self.update_guide()

    def update_guide(self):
        # Clear existing guide overlays
        self.canvas.delete("guide")
        
        step = self.controller.order_manager.current_step
        target = self.controller.order_manager.guide_target

        if step == 1:
            if not self.controller.order_manager.cart:
                # Guide to click (ICE) 아메리카노 menu
                # Col 2, Row 1 in scaled coordinates
                # Col 2: x=270 to 354, Row 1: y=225 to 340
                self.set_guide_text("1단계: 메뉴를 선택할 차례입니다.\n시원한 커피인 '(ICE) 아메리카노' 메뉴를 손가락으로 가볍게 눌러보세요.")
                self.draw_guide_rect(270, 225, 354, 340)
            else:
                # Guide to click '결제하기' at bottom right
                # Scaled x=350 to 430, y=590 to 635
                self.set_guide_text("장바구니에 음료가 담겼습니다.\n주문 확인을 위해 오른쪽 아래의 주황색 '결제하기' 버튼을 눌러보세요.")
                self.draw_guide_rect(350, 590, 430, 635)

        elif step == 2:
            # Options popup. Guide to click '주문담기' (scaled x=340 to 430, y=590 to 635)
            # User can optionally choose options first. Let's guide to add to cart.
            self.set_guide_text(f"2단계: '{target}'의 세부 옵션(샷 추가, 텀블러 사용 등)을 선택한 다음, 오른쪽 아래의 '주문담기' 버튼을 눌러보세요.")
            self.draw_guide_rect(340, 590, 430, 635)

        elif step == 3:
            # Confirmation popup. Guide to click '결제하기' (scaled x=280 to 420, y=590 to 635)
            self.set_guide_text("3단계: 주문하신 세부 내역이 맞는지 다시 확인하시고, 화면 아래의 오른쪽 '결제하기' 버튼을 눌러보세요.")
            self.draw_guide_rect(280, 590, 420, 635)

        elif step == 4:
            # Custom Eat-in / Take-out screen. Guide to click '포장하기' (scaled x=275 to 455, y=200 to 450)
            self.set_guide_text("4단계: 매장에서 식사하실지 포장해가실지 고르는 단계입니다. 여기서는 '포장하기' 버튼을 눌러보세요.")
            self.draw_guide_rect(275, 200, 455, 450)

        elif step == 5:
            # Payment selection. Guide to click '카드결제' (scaled x=130 to 250, y=350 to 430)
            self.set_guide_text("5단계: 결제 수단을 고르는 화면입니다.\n가장 많이 사용하는 신용카드 결제를 위해 '카드결제' 버튼을 눌러보세요.")
            self.draw_guide_rect(130, 350, 250, 430)

        elif step == 6:
            # Insert Card simulator. Guide to click '카드 넣기' (scaled x=150 to 390, y=450 to 520)
            self.set_guide_text("6단계: 이제 신용카드를 카드 투입구에 넣는 연습입니다.\n가상 카드를 넣으려면 화면의 '카드 넣기' 버튼을 눌러보세요.")
            self.draw_guide_rect(150, 450, 390, 520)

    # --- CANVAS OVERLAYS ---

    def draw_guide_rect(self, x1, y1, x2, y2):
        # Create guide border
        color = "red" if self.flash_state else "yellow"
        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline=color, width=5, dash=(4, 4), tags="guide"
        )
        # Create pointing arrow on top of the button
        self.canvas.create_polygon(
            (x1+x2)//2, y1-30,
            (x1+x2)//2-15, y1-50,
            (x1+x2)//2+15, y1-50,
            fill=color, outline="black", tags="guide"
        )

    def draw_step1_overlays(self):
        # Draw dynamic cart items at the bottom of the screen
        # Cart boundary in scaled coords: x=102 to 340, y=510 to 675
        self.canvas.create_rectangle(120, 515, 340, 580, fill="#FFFFFF", outline="#DDDDDD", tags="overlay")
        
        cart = self.controller.order_manager.cart
        if not cart:
            self.canvas.create_text(
                230, 545, 
                text="선택한 메뉴가 없습니다.", 
                font=("Malgun Gothic", 12), fill="#888888", tags="overlay"
            )
        else:
            y = 525
            for item in cart[:2]: # Show max 2 items in cart overlay
                opt_str = ", ".join([v for k, v in item['options'].items() if v != '사용 안함' and v != '기본' and v != '없음'])
                disp = f"{item['name']} ({item['quantity']}개)"
                if opt_str:
                    disp += f" [{opt_str}]"
                self.canvas.create_text(
                    125, y, 
                    text=disp, anchor="nw", 
                    font=("Malgun Gothic", 11, "bold"), fill="#000000", tags="overlay"
                )
                self.canvas.create_text(
                    335, y, 
                    text=f"{item['price'] * item['quantity']}원", anchor="ne", 
                    font=("Malgun Gothic", 11), fill="#000000", tags="overlay"
                )
                y += 20
            
            # Show total price
            total = self.controller.order_manager.get_cart_total()
            self.canvas.create_text(
                335, 565,
                text=f"합계: {total}원", anchor="ne",
                font=("Malgun Gothic", 12, "bold"), fill="#d32f2f", tags="overlay"
            )

    def draw_step2_overlays(self):
        # Options screen. Show pending item name at top
        item = self.controller.order_manager.pending_item
        if item:
            self.canvas.create_rectangle(170, 160, 370, 200, fill="#FFF3CD", outline="#FFEBAA", tags="overlay")
            self.canvas.create_text(
                270, 180,
                text=f"{item['name']}",
                font=("Malgun Gothic", 14, "bold"), fill="#856404", tags="overlay"
            )

            # Draw selected options statuses
            y = 230
            for k, v in item['options'].items():
                self.canvas.create_rectangle(140, y-10, 400, y+15, fill="#F8F9FA", outline="#E2E3E5", tags="overlay")
                self.canvas.create_text(
                    150, y,
                    text=f"{k}: {v}", anchor="nw",
                    font=("Malgun Gothic", 12, "bold"), fill="#333333", tags="overlay"
                )
                y += 30

    def draw_step3_overlays(self):
        # Confirmation list
        cart = self.controller.order_manager.cart
        y = 240
        self.canvas.create_rectangle(130, 200, 410, 480, fill="#FFFFFF", outline="#CCCCCC", tags="overlay")
        self.canvas.create_text(
            270, 215,
            text="🛒 주문 상세 확인 🛒",
            font=("Malgun Gothic", 14, "bold"), fill="#333333", tags="overlay"
        )
        
        for item in cart:
            # Show item name, quantity, price
            self.canvas.create_text(
                140, y,
                text=f"{item['name']} x {item['quantity']}", anchor="nw",
                font=("Malgun Gothic", 13, "bold"), fill="#333333", tags="overlay"
            )
            self.canvas.create_text(
                400, y,
                text=f"{item['price'] * item['quantity']}원", anchor="ne",
                font=("Malgun Gothic", 13), fill="#333333", tags="overlay"
            )
            # Show options underneath
            opts = ", ".join([v for k, v in item['options'].items() if v != '사용 안함' and v != '기본' and v != '없음'])
            if opts:
                y += 18
                self.canvas.create_text(
                    150, y,
                    text=f"ㄴ 옵션: {opts}", anchor="nw",
                    font=("Malgun Gothic", 11), fill="#666666", tags="overlay"
                )
            y += 28

        # Draw total summary at bottom of confirmation box
        total = self.controller.order_manager.get_cart_total()
        self.canvas.create_text(
            400, 455,
            text=f"최종 결제 금액: {total}원", anchor="ne",
            font=("Malgun Gothic", 14, "bold"), fill="#D32F2F", tags="overlay"
        )

    def draw_custom_step4_screen(self):
        # Custom screen for Eat-in vs Take-out
        # background color: Megacoffee Dark Grey
        self.canvas.create_rectangle(0, 0, self.kiosk_width, self.kiosk_height, fill="#2C2C2C", tags="overlay")
        
        # Title banner
        self.canvas.create_rectangle(0, 40, self.kiosk_width, 100, fill="#FFCC00", outline="", tags="overlay")
        self.canvas.create_text(
            self.kiosk_width//2, 70,
            text="식사 장소를 선택해주세요",
            font=("Malgun Gothic", 24, "bold"), fill="#000000", tags="overlay"
        )

        # 1. Eat-In button (Left)
        # Coordinates: x1=85, y1=200, x2=255, y2=450
        self.canvas.create_rectangle(85, 200, 255, 450, fill="#FFFFFF", outline="#FFCC00", width=3, tags="overlay")
        self.canvas.create_text(
            170, 260,
            text="",
            font=("Segoe UI Emoji", 70), tags="overlay"
        )
        self.canvas.create_text(
            170, 360,
            text="매장 이용\n(먹고 가기)",
            font=("Malgun Gothic", 20, "bold"), fill="#333333", justify="center", tags="overlay"
        )
        self.canvas.create_text(
            170, 420,
            text="매장 내 일회용컵 불가",
            font=("Malgun Gothic", 11), fill="#E65100", tags="overlay"
        )

        # 2. Take-Out button (Right)
        # Coordinates: x1=275, y1=200, x2=445, y2=450
        self.canvas.create_rectangle(275, 200, 445, 450, fill="#FFFFFF", outline="#FFCC00", width=3, tags="overlay")
        self.canvas.create_text(
            360, 260,
            text="",
            font=("Segoe UI Emoji", 70), tags="overlay"
        )
        self.canvas.create_text(
            360, 360,
            text="포장하기\n(가져가기)",
            font=("Malgun Gothic", 20, "bold"), fill="#333333", justify="center", tags="overlay"
        )
        self.canvas.create_text(
            360, 420,
            text="일회용컵 포장 가능",
            font=("Malgun Gothic", 11), fill="#1B5E20", tags="overlay"
        )

    def draw_step6_overlays(self):
        # Insert Card screen
        # Place virtual card insertion button in middle
        self.canvas.create_rectangle(150, 450, 390, 520, fill="#4CAF50", outline="#388E3C", width=2, tags="overlay")
        self.canvas.create_text(
            270, 485,
            text=" 카드 투입구에 카드 넣기",
            font=("Malgun Gothic", 18, "bold"), fill="#FFFFFF", tags="overlay"
        )

    # --- INTERACTION CONTROLLERS ---

    def start_flashing(self):
        self.flash_state = not self.flash_state
        self.update_guide()
        self.flash_job = self.after(500, self.start_flashing)

    def stop_flashing(self):
        if self.flash_job:
            self.after_cancel(self.flash_job)
            self.flash_job = None

    def handle_correct_action(self):
        # Flash visual feedback (green check)
        self.canvas.create_text(
            self.kiosk_width//2, self.kiosk_height//2,
            text=" 성공!", font=("Segoe UI Emoji", 80), fill="#4CAF50", tags="feedback"
        )
        self.controller.voice_assistant.speak("참 잘하셨어요!")
        self.after(600, self.clear_feedback_and_next)

    def handle_mistake(self):
        self.controller.order_manager.add_mistake()
        
        # Red X visual feedback
        self.canvas.create_text(
            self.kiosk_width//2, self.kiosk_height//2,
            text=" 다시 시도해보세요", font=("Segoe UI Emoji", 50), fill="#f44336", tags="feedback"
        )
        self.controller.voice_assistant.speak("그 버튼이 아니에요. 반짝이는 부분을 다시 한번 천천히 눌러보세요.")
        self.after(1000, lambda: self.canvas.delete("feedback"))

    def clear_feedback_and_next(self):
        self.canvas.delete("feedback")
        self.update_screen()

    def on_canvas_click(self, event):
        x, y = event.x, event.y
        step = self.controller.order_manager.current_step
        target = self.controller.order_manager.guide_target

        print(f"Canvas click at: x={x}, y={y} (Step={step})")

        # Handle Menu Translation triggered by Double Click or normal click with modifier
        # Or let's handle if they click menus in Step 1 to show the translation!
        # This acts as a translator popup: if they double click a menu card
        
        if step == 1:
            # Menu Selection Screen
            # Determine if click is inside grid items
            # Grid Col 2, Row 1 is "(ICE)아메리카노": x=270~354, y=225~340
            # Let's check other menus:
            # Col 1, Row 1 is "메가리카노": x=186~270, y=225~340
            # Col 0, Row 2 is "꿀아메리카노": x=102~186, y=350~465
            # Col 1, Row 2 is "바닐라아메리카노": x=186~270, y=350~465

            # Double click check (simulated via rapid click or let's use coordinate checks for translation)
            # Let's say if they click on a menu, it shows the translation first or opens the options dialog.
            # To allow translations: if they double-click, we translate. If single-click, we select.
            # Let's make it single click handles menu select, but we can also display translation text in the sidebar!
            
            # Check (ICE) 아메리카노 click
            if 270 <= x <= 354 and 225 <= y <= 340:
                self.show_translation("(ICE)아메리카노")
                if not self.controller.order_manager.cart:
                    # Correct action
                    self.controller.order_manager.select_menu_to_configure("(ICE)아메리카노", 2000)
                    self.handle_correct_action()
                else:
                    # Cart is full, guiding to click checkout. Clicking menu is a mistake or we can allow it
                    self.handle_mistake()
            
            # Check 메가리카노 click
            elif 186 <= x <= 270 and 225 <= y <= 340:
                self.show_translation("메가리카노")
                self.controller.order_manager.select_menu_to_configure("메가리카노", 3000)
                self.controller.order_manager.guide_target = "메가리카노"
                self.handle_correct_action()

            # Check 꿀아메리카노 click
            elif 102 <= x <= 186 and 350 <= y <= 465:
                self.show_translation("꿀아메리카노")
                self.controller.order_manager.select_menu_to_configure("꿀아메리카노", 2700)
                self.controller.order_manager.guide_target = "꿀아메리카노"
                self.handle_correct_action()

            # Check 바닐라아메리카노 click
            elif 186 <= x <= 270 and 350 <= y <= 465:
                self.show_translation("바닐라아메리카노")
                self.controller.order_manager.select_menu_to_configure("바닐라아메리카노", 2700)
                self.controller.order_manager.guide_target = "바닐라아메리카노"
                self.handle_correct_action()

            # Check '결제하기' at bottom right: x=350~430, y=590~635
            elif 350 <= x <= 430 and 590 <= y <= 635:
                if self.controller.order_manager.cart:
                    # Correct action, proceed to Step 3
                    self.controller.order_manager.current_step = 3
                    self.handle_correct_action()
                else:
                    # No items in cart, clicking pay is mistake
                    self.handle_mistake()
            else:
                # Clicked elsewhere
                self.handle_mistake()

        elif step == 2:
            # Options Screen
            # Options: '샷 추가' at x=219~275, y=356
            # In options, clicking option triggers text updates.
            # '주문담기' button at x=340~430, y=590~635
            if 340 <= x <= 430 and 590 <= y <= 635:
                # Correct action: commit item
                self.controller.order_manager.commit_pending_item()
                self.handle_correct_action()
            elif 210 <= x <= 280 and 340 <= y <= 375:
                # Clicked shot-add option! Toggle option
                item = self.controller.order_manager.pending_item
                if item:
                    current_shot = item['options'].get('샷 추가', '기본(2샷)')
                    new_shot = '1샷 추가(+500원)' if current_shot == '기본(2샷)' else '기본(2샷)'
                    self.controller.order_manager.update_pending_option('샷 추가', new_shot, 500 if new_shot != '기본(2샷)' else -500)
                    self.controller.voice_assistant.speak("에스프레소 샷을 추가했습니다.")
                    self.update_screen()
            else:
                self.handle_mistake()

        elif step == 3:
            # Order details confirmation screen
            # Buttons: 취소 (scaled x=120 to 260, y=590 to 635) and 결제하기 (scaled x=280 to 420, y=590 to 635)
            if 280 <= x <= 420 and 590 <= y <= 635:
                # Correct action: go to Step 4 (Eat-in / Take-out selection)
                self.controller.order_manager.current_step = 4
                self.handle_correct_action()
            elif 120 <= x <= 260 and 590 <= y <= 635:
                # Cancel order
                self.controller.order_manager.start_session()
                self.controller.voice_assistant.speak("주문을 취소하고 처음으로 돌아갑니다.")
                self.update_screen()
            else:
                self.handle_mistake()

        elif step == 4:
            # Eat-in / Take-out screen (Custom)
            # Eat-in: x1=85, y1=200, x2=255, y2=450
            # Take-out: x1=275, y1=200, x2=445, y2=450
            if 275 <= x <= 445 and 200 <= y <= 450:
                # Correct action: Takeout selected
                self.controller.order_manager.set_eat_in("포장")
                self.handle_correct_action()
            elif 85 <= x <= 255 and 200 <= y <= 450:
                # Allow eat-in too, but warn them since we guided takeout
                self.controller.order_manager.set_eat_in("매장")
                self.handle_correct_action()
            else:
                self.handle_mistake()

        elif step == 5:
            # Payment selection screen
            # '카드결제' button: scaled x=130 to 250, y=350 to 430
            if 130 <= x <= 250 and 350 <= y <= 430:
                self.controller.order_manager.set_payment_method("카드결제")
                self.handle_correct_action()
            else:
                self.handle_mistake()

        elif step == 6:
            # Insert Card simulator
            # '카드 넣기' button: scaled x=150 to 390, y=450 to 520
            if 150 <= x <= 390 and 450 <= y <= 520:
                self.stop_flashing()
                self.controller.order_manager.end_session()
                
                # Save learning history record
                ordered_menus_str = ", ".join([f"{item['name']} {item['quantity']}개" for item in self.controller.order_manager.cart])
                duration = self.controller.order_manager.get_duration()
                mistakes = self.controller.order_manager.mistake_count
                
                self.controller.history_manager.add_record(
                    brand=self.controller.order_manager.brand,
                    ordered_menus=ordered_menus_str,
                    duration_seconds=duration,
                    mistake_count=mistakes
                )

                # Show Success receipt and pop up
                self.show_completion_screen(ordered_menus_str, duration, mistakes)
            else:
                self.handle_mistake()

    def show_translation(self, menu_name):
        # Update translator panel in sidebar
        desc = self.controller.menu_translator.translate(menu_name)
        self.trans_desc_label.configure(
            text=f" [{menu_name}]\n{desc}",
            text_color="#004D40",
            font=ctk.CTkFont(family="Malgun Gothic", size=15, weight="bold")
        )

    def show_completion_screen(self, ordered_menus, duration, mistakes):
        self.canvas.delete("all")
        # Draw green background for completion
        self.canvas.create_rectangle(0, 0, self.kiosk_width, self.kiosk_height, fill="#E8F5E9", tags="overlay")
        
        self.canvas.create_text(
            self.kiosk_width//2, 80,
            text=" 결제 및 학습 완료! ",
            font=("Malgun Gothic", 26, "bold"), fill="#2E7D32", tags="overlay"
        )

        self.canvas.create_text(
            self.kiosk_width//2, 140,
            text="축하합니다! 연습 결제를 마쳤습니다.",
            font=("Malgun Gothic", 16), fill="#333333", tags="overlay"
        )

        # Draw a cute cartoon receipt
        self.canvas.create_rectangle(100, 180, 440, 520, fill="#FFFFFF", outline="#DDDDDD", width=2, tags="overlay")
        self.canvas.create_text(
            self.kiosk_width//2, 210,
            text="[ 연습 영수증 ]",
            font=("Malgun Gothic", 16, "bold"), fill="#555555", tags="overlay"
        )
        
        self.canvas.create_line(120, 235, 420, 235, dash=(4, 2), fill="#888888", tags="overlay")
        
        details = [
            f"연습 브랜드:  {self.controller.order_manager.brand}",
            f"주문한 메뉴:  {ordered_menus}",
            f"실제 결제액:  0원 (모의 연습)",
            f"연습 소요 시간: {duration}초",
            f"조작 실수 횟수: {mistakes}회"
        ]
        
        y = 260
        for detail in details:
            self.canvas.create_text(
                130, y,
                text=detail, anchor="nw",
                font=("Malgun Gothic", 13, "bold" if "실수" in detail or "시간" in detail else "normal"), 
                fill="#333333", 
                width=280,
                tags="overlay"
            )
            y += 40

        self.canvas.create_line(120, 470, 420, 470, dash=(4, 2), fill="#888888", tags="overlay")
        self.canvas.create_text(
            self.kiosk_width//2, 495,
            text="참 잘하셨어요! 다음엔 진짜 매장에서도\n자신 있게 결제해 보세요! ",
            font=("Malgun Gothic", 13, "bold"), fill="#2E7D32", justify="center", tags="overlay"
        )

        # Big Button: Return to main menu
        # Create a custom Tkinter button on canvas
        return_btn = ctk.CTkButton(
            self.kiosk_frame,
            text=" 첫 화면으로 나가기",
            font=ctk.CTkFont(family="Malgun Gothic", size=20, weight="bold"),
            fg_color="#4CAF50",
            hover_color="#45a049",
            height=50,
            command=self.return_to_main
        )
        self.canvas.create_window(self.kiosk_width//2, 580, window=return_btn, tags="overlay")

        # Set final TTS voice guidance
        congratulations_text = f"결제가 완료되었습니다! {duration}초 동안 연습하셨고, 실수는 {mistakes}회 하셨습니다. 참 잘하셨어요! 이제 첫 화면으로 나가기 버튼을 눌러주세요."
        self.set_guide_text(congratulations_text)

    def return_to_main(self):
        # Refresh statistics on main screen
        self.controller.refresh_main_screen_stats()
        self.controller.show_frame("MainScreen")

    # --- VOICE ASSISTANT STT INTEGRATION ---

    def toggle_mic(self):
        if self.voice_listening:
            return
        
        self.voice_listening = True
        self.mic_btn.configure(text=" 말씀하세요... (듣는 중)", fg_color="#E91E63")
        self.controller.voice_assistant.listen_from_mic(self.on_voice_heard)

    def on_voice_heard(self, text, error):
        self.voice_listening = False
        self.mic_btn.configure(text=" 마이크 켜고 말하기", fg_color="#9C27B0")
        
        if error:
            messagebox.showwarning("음성 입력 안내", f"{error}\n\n장치 또는 오디오 드라이버 상태로 인해 마이크 입력을 받지 못했습니다. 아래의 말하기 예시나 텍스트창을 통해 말하는 것을 간편하게 시험해 볼 수 있습니다.")
            return

        if text:
            self.voice_entry.delete(0, "end")
            self.voice_entry.insert(0, text)
            self.process_voice_command(text)

    def process_simulated_voice(self):
        text = self.voice_entry.get().strip()
        if text:
            self.process_voice_command(text)

    def process_voice_command(self, text):
        """
        Interprets the user's spoken words and maps them to simulation actions (Scenario generation).
        """
        step = self.controller.order_manager.current_step
        print(f"Processing voice command: '{text}' (Step={step})")

        # Simple semantic matching
        if "종료" in text or "나가기" in text:
            self.return_to_main()
            return

        if "설명" in text or "번역" in text:
            # Try to extract menu name and explain it
            for menu in ["아인슈페너", "플랫화이트", "아메리카노", "라떼", "에이드", "티", "주스"]:
                if menu in text:
                    self.show_translation(menu)
                    self.controller.voice_assistant.speak(f"{menu}에 대해 설명해 드릴게요.")
                    return

        if step == 1:
            # Menu selection step
            if "아이스 아메리카노" in text or "아메리카노" in text or "커피" in text:
                # Select "(ICE) 아메리카노"
                self.show_translation("(ICE)아메리카노")
                self.controller.order_manager.select_menu_to_configure("(ICE)아메리카노", 2000)
                self.handle_correct_action()
            elif "메가리카노" in text:
                self.show_translation("메가리카노")
                self.controller.order_manager.select_menu_to_configure("메가리카노", 3000)
                self.controller.order_manager.guide_target = "메가리카노"
                self.handle_correct_action()
            elif "꿀아메리카노" in text:
                self.show_translation("꿀아메리카노")
                self.controller.order_manager.select_menu_to_configure("꿀아메리카노", 2700)
                self.controller.order_manager.guide_target = "꿀아메리카노"
                self.handle_correct_action()
            elif "결제" in text or "주문완료" in text or "선택완료" in text:
                if self.controller.order_manager.cart:
                    self.controller.order_manager.current_step = 3
                    self.handle_correct_action()
                else:
                    self.controller.voice_assistant.speak("장바구니에 담긴 메뉴가 없습니다. 먼저 커피를 주문해보세요.")
            else:
                self.handle_mistake()

        elif step == 2:
            # Options selection step
            if "샷 추가" in text or "샷추가" in text:
                item = self.controller.order_manager.pending_item
                if item:
                    self.controller.order_manager.update_pending_option('샷 추가', '1샷 추가(+500원)', 500)
                    self.controller.voice_assistant.speak("에스프레소 샷을 추가했습니다.")
                    self.update_screen()
            elif "담기" in text or "완료" in text or "선택완료" in text or "확인" in text:
                self.controller.order_manager.commit_pending_item()
                self.handle_correct_action()
            else:
                self.handle_mistake()

        elif step == 3:
            # Order confirmation step
            if "결제" in text or "확인" in text or "예" in text:
                self.controller.order_manager.current_step = 4
                self.handle_correct_action()
            elif "취소" in text or "아니오" in text:
                self.controller.order_manager.start_session()
                self.controller.voice_assistant.speak("주문을 취소하고 처음으로 돌아갑니다.")
                self.update_screen()
            else:
                self.handle_mistake()

        elif step == 4:
            # Eat-in / Takeout step
            if "포장" in text or "가져" in text:
                self.controller.order_manager.set_eat_in("포장")
                self.handle_correct_action()
            elif "매장" in text or "먹고" in text:
                self.controller.order_manager.set_eat_in("매장")
                self.handle_correct_action()
            else:
                self.handle_mistake()

        elif step == 5:
            # Payment selection step
            if "카드" in text or "신용카드" in text:
                self.controller.order_manager.set_payment_method("카드결제")
                self.handle_correct_action()
            else:
                self.handle_mistake()

        elif step == 6:
            # Card insertion step
            if "카드" in text or "결제" in text or "넣기" in text or "완료" in text:
                # Simulate card insertion click
                self.stop_flashing()
                self.controller.order_manager.end_session()
                ordered_menus_str = ", ".join([f"{item['name']} {item['quantity']}개" for item in self.controller.order_manager.cart])
                duration = self.controller.order_manager.get_duration()
                mistakes = self.controller.order_manager.mistake_count
                
                self.controller.history_manager.add_record(
                    brand=self.controller.order_manager.brand,
                    ordered_menus=ordered_menus_str,
                    duration_seconds=duration,
                    mistake_count=mistakes
                )
                self.show_completion_screen(ordered_menus_str, duration, mistakes)
            else:
                self.handle_mistake()
