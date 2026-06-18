import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "provider": "openclaw", # openclaw, gemini, openai
    "openclaw_url": "http://127.0.0.1:18789/v1/chat/completions",
    "gemini_api_key": "",
    "openai_api_key": "",
    "voice": "es-ES-AlvaroNeural", # Edge TTS Voice
    "wake_word": "jarvis",
    "location": "Madrid"
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # Merge with defaults to ensure all keys exist
            for k, v in DEFAULT_CONFIG.items():
                if k not in config:
                    config[k] = v
            return config
    except Exception as e:
        print(f"Error loading config: {e}")
        return DEFAULT_CONFIG

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")
