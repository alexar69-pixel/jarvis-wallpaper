import urllib.request
import urllib.error
import json

def call_openclaw(url, command_text):
    print(f"[OpenClaw] Enviando comando: {command_text}")
    data = json.dumps({
        "model": "openclaw/default",
        "user": "jarvis-wallpaper-app",
        "messages": [{"role": "user", "content": command_text}]
    }).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            return response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
    except Exception as e:
        return f"Error OpenClaw: {e}"

def call_gemini(api_key, command_text):
    print(f"[Gemini] Enviando comando: {command_text}")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    data = json.dumps({
        "contents": [{"parts":[{"text": command_text}]}]
    }).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            parts = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [])
            return parts[0].get('text', '') if parts else ''
    except Exception as e:
        return f"Error Gemini: {e}"

def call_openai(api_key, command_text):
    print(f"[OpenAI] Enviando comando: {command_text}")
    url = "https://api.openai.com/v1/chat/completions"
    data = json.dumps({
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": command_text}]
    }).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {api_key}"
    }, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            return response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
    except Exception as e:
        return f"Error OpenAI: {e}"

def send_to_provider(config, command_text):
    provider = config.get("provider", "openclaw")
    if provider == "openclaw":
        return call_openclaw(config.get("openclaw_url"), command_text)
    elif provider == "gemini":
        return call_gemini(config.get("gemini_api_key"), command_text)
    elif provider == "openai":
        return call_openai(config.get("openai_api_key"), command_text)
    return "Error: Proveedor no válido en la configuración."
