import json
import os
from datetime import datetime

class HistoryManager:
    """
    Manages loading, updating, and saving user learning sessions (history)
    to a JSON file (history.json).
    """
    def __init__(self, filename="history.json"):
        self.filename = filename
        self.history = []
        self.load_history()

    def load_history(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except Exception as e:
                print(f"Error loading history file, starting fresh: {e}")
                self.history = []
        else:
            self.history = []

    def save_history(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving history file: {e}")

    def add_record(self, brand, ordered_menus, duration_seconds, mistake_count):
        """
        Adds a new training session record.
        ordered_menus: can be a list of strings or a single string of ordered items.
        """
        record = {
            "연습 날짜": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "브랜드": brand,
            "주문 메뉴": ordered_menus,
            "소요 시간": f"{duration_seconds}초",
            "실수 횟수": mistake_count
        }
        self.history.append(record)
        self.save_history()
        return record

    def get_all_records(self):
        return self.history

    def get_summary_statistics(self):
        """
        Computes simple aggregate statistics for presentation.
        """
        if not self.history:
            return {"total_sessions": 0, "avg_mistakes": 0.0, "avg_duration": 0.0}
        
        total_sessions = len(self.history)
        total_mistakes = sum(r["실수 횟수"] for r in self.history)
        
        total_duration = 0
        for r in self.history:
            dur_str = r["소요 시간"].replace("초", "")
            try:
                total_duration += int(dur_str)
            except ValueError:
                pass
                
        return {
            "total_sessions": total_sessions,
            "avg_mistakes": round(total_mistakes / total_sessions, 1),
            "avg_duration": round(total_duration / total_sessions, 1)
        }
