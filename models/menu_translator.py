import os

class MenuTranslator:
    """
    Translates difficult or foreign menu names (e.g., Einspanner, Espresso, Flat White)
    into simple, senior-friendly Korean explanations.
    Uses Gemini or OpenAI APIs if credentials exist; otherwise falls back to a dictionary.
    """
    def __init__(self):
        # Senior-friendly fallback dictionary
        self.fallback_dict = {
            "아메리카노": "원두커피에 물을 타서 연하고 깔끔하게 마시는 가장 기본 커피입니다.",
            "(ICE)아메리카노": "얼음을 넣어 시원하게 마시는 깔끔한 기본 커피입니다.",
            "(HOT)아메리카노": "따뜻하게 마시는 깔끔하고 고소한 기본 커피입니다.",
            "메가리카노": "일반 아메리카노보다 양이 두 배 많은 대용량 아메리카노입니다.",
            "꿀아메리카노": "아메리카노에 달콤한 꿀을 섞어 달달하게 만든 커피입니다.",
            "바닐라아메리카노": "아메리카노에 향긋하고 달달한 바닐라 향 시럽을 넣은 커피입니다.",
            "헤이즐넛아메리카노": "아메리카노에 고소한 헤이즐넛 향 시럽을 더한 커피입니다.",
            "카페라떼": "진한 에스프레소 커피에 부드러운 우유를 섞어 고소하게 만든 음료입니다.",
            "바닐라라떼": "부드러운 우유 커피에 달달한 바닐라 향 시럽을 섞은 달콤한 음료입니다.",
            "카라멜마끼아또": "우유 커피 위에 달콤하고 진한 카라멜 시럽을 얹어 매우 달달한 커피입니다.",
            "아인슈페너": "진하고 씁쓸한 커피 위에 달콤하고 부드러운 하얀 생크림을 듬뿍 올린 음료입니다.",
            "플랫화이트": "라떼보다 우유를 적게 넣어, 우유 맛보다 커피의 진한 맛이 더 잘 느껴지는 음료입니다.",
            "에스프레소": "원두에서 아주 진하게 짜낸 소량의 쓴 커피 원액입니다. 보통 설탕을 타 마십니다.",
            "콜드브루": "찬물로 오랫동안 천천히 우려내어 일반 커피보다 쓴맛이 적고 뒷맛이 깔끔한 커피입니다.",
            "아포가토": "달콤한 바닐라 아이스크림 위에 진한 커피 원액을 끼얹어 떠먹는 디저트입니다.",
            "자몽에이드": "쌉싸름하고 상큼한 자몽 청에 톡 쏘는 탄산수를 섞어 시원하게 마시는 음료입니다.",
            "청포도에이드": "달콤하고 청량한 청포도 청에 탄산수를 섞어 시원하게 마시는 주스입니다.",
            "딸기주스": "새콤달콤한 생딸기를 갈아서 만든 시원하고 건강한 과일 주스입니다.",
            "허니자몽블랙티": "달콤한 자몽과 꿀, 그리고 향긋한 홍차를 우려내어 섞은 달콤 쌉싸름한 차입니다.",
            "캐모마일": "향긋한 국화 꽃잎을 우려내어 마음을 편안하게 해주는 은은한 허브차입니다. 카페인이 없습니다.",
            "페퍼민트": "입안을 화하고 시원하게 해주는 민트 잎을 우려내어 깔끔하고 개운한 허브차입니다.",
            "감자빵": "겉은 쫄깃하고 속은 부드럽고 든든한 감자 앙금으로 가득 찬 감자 모양 빵입니다.",
            "크로플": "크루아상 빵 반죽을 와플 기계에 구워 겉은 바삭하고 속은 촉촉한 인기 디저트입니다.",
            "핫도그": "쫄깃한 빵 속에 맛있는 소시지가 통째로 들어간 든든한 간식입니다."
        }

    def translate(self, menu_name):
        """
        Main entry point for translation.
        First tries Gemini or OpenAI API, and falls back to dictionary on failure or absence of keys.
        """
        # Try APIs first if keys are available
        gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        openai_key = os.environ.get("OPENAI_API_KEY")

        if gemini_key:
            try:
                return self._translate_gemini(menu_name, gemini_key)
            except Exception as e:
                print(f"Gemini translation failed, using dictionary: {e}")

        if openai_key:
            try:
                return self._translate_openai(menu_name, openai_key)
            except Exception as e:
                print(f"OpenAI translation failed, using dictionary: {e}")

        # Dictionary Fallback
        # Exact match or substring match
        for key, desc in self.fallback_dict.items():
            if key in menu_name or menu_name in key:
                return desc
                
        # Default description if not found
        return f"'{menu_name}'은(는) 맛있는 카페 메뉴입니다. 종업원이나 도우미에게 문의해보세요."

    def _translate_gemini(self, menu_name, api_key):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = (
            f"당신은 실버 세대(어르신들)를 위한 키오스크 번역가입니다. "
            f"외래어나 낯선 메뉴인 '{menu_name}'을 70대 어르신이 아주 쉽게 이해할 수 있도록 "
            f"주요 재료와 맛을 기반으로 쉬운 한국어 1문장(25자 내외)으로 설명해주세요. "
            f"예시: 아인슈페너 -> '커피 위에 달콤한 크림을 올린 음료'. "
            f"존댓말 표현을 사용하되 군더더기 없이 설명만 출력하세요."
        )
        response = model.generate_content(prompt)
        return response.text.strip().replace('"', '').replace("'", "")

    def _translate_openai(self, menu_name, api_key):
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        prompt = (
            f"당신은 실버 세대를 위한 키오스크 번역가입니다. "
            f"외래어나 낯선 메뉴인 '{menu_name}'을 70대 어르신이 아주 쉽게 이해할 수 있도록 "
            f"주요 재료와 맛을 기반으로 쉬운 한국어 1문장(25자 내외)으로 설명해주세요. "
            f"예시: 아인슈페너 -> '커피 위에 달콤한 크림을 올린 음료'."
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You explain menus to seniors in one simple sentence in Korean."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.3
        )
        return response.choices[0].message.content.strip().replace('"', '').replace("'", "")
