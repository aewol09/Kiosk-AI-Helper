import os
import sys
from flask import Flask, render_template, jsonify, request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.history_manager import HistoryManager
from models.menu_translator import MenuTranslator

app = Flask(__name__)

# Initialize python managers
history_manager = HistoryManager()
menu_translator = MenuTranslator()

@app.route('/')
def index():
    """
    Renders the single-page application.
    """
    return render_template('index.html')

@app.route('/api/menu', methods=['GET'])
def get_menu():
    """
    Returns the brand menus from mega_menu.json.
    """
    import json
    menu_file = os.path.join(os.path.dirname(__file__), 'mega_menu.json')
    if os.path.exists(menu_file):
        try:
            with open(menu_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": f"Failed to read menu file: {str(e)}"}), 500
    return jsonify({"error": "Menu file not found"}), 404

@app.route('/api/history', methods=['GET'])
def get_history():
    """
    Returns all learning sessions and summary statistics.
    """
    records = history_manager.get_all_records()
    stats = history_manager.get_summary_statistics()
    return jsonify({
        "records": records,
        "stats": stats
    })

@app.route('/api/history', methods=['POST'])
def add_history():
    """
    Logs a new learning session.
    """
    data = request.json or {}
    brand = data.get("brand", "메가커피")
    ordered_menus = data.get("ordered_menus", "")
    duration_seconds = data.get("duration_seconds", 0)
    mistake_count = data.get("mistake_count", 0)

    record = history_manager.add_record(
        brand=brand,
        ordered_menus=ordered_menus,
        duration_seconds=duration_seconds,
        mistake_count=mistake_count
    )
    return jsonify({"success": True, "record": record})

@app.route('/api/translate', methods=['POST'])
def translate_menu():
    """
    Translates difficult menus to simple Korean.
    """
    data = request.json or {}
    menu_name = data.get("menu_name", "")
    if not menu_name:
        return jsonify({"error": "Missing menu_name"}), 400

    explanation = menu_translator.translate(menu_name)
    return jsonify({
        "menu_name": menu_name,
        "explanation": explanation
    })

if __name__ == '__main__':
    # Run the server locally on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
