import json
import os

SAVE_PATH = "saves\game0.json"

def load_save(filepath: str) -> dict:
    """從 JSON 檔案載入儲存的遊戲資料"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        print(f"Error: Save file not found at {filepath}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {filepath}")
        return {}