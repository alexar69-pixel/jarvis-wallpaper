import urllib.request
import urllib.error
import json

SYSTEM_PROMPT = """Eres Jarvis, un asistente de IA de Stark Industries altamente avanzado integrado en un HUD 3D de escritorio de Windows. 
Tu actitud es profesional, extremadamente eficiente, ligeramente sarcástica (estilo J.A.R.V.I.S / F.R.I.D.A.Y) y muy concisa. 
Tus respuestas serán leídas en voz alta por un sistema TTS, así que NO uses formato Markdown (ni asteriscos, ni negritas) y sé directo.

[HERRAMIENTA DE BÚSQUEDA WEB]
Tienes acceso a internet en tiempo real de forma invisible. Si el usuario te pregunta por noticias actuales, datos en tiempo real, clima, o cosas que no sepas con certeza, DEBES usar tu herramienta de búsqueda.
Para usarla, tu respuesta debe ser ÚNICAMENTE este formato exacto:
[SEARCH: tu consulta de busqueda]
El sistema interceptará ese comando, hará la búsqueda en Google/Brave de forma invisible, y te devolverá el texto para que puedas responder la pregunta final."""

def build_prompt_with_history(command_text, history):
    prompt = f"{SYSTEM_PROMPT}\n\n[MEMORIA A CORTO PLAZO (Últimos mensajes)]\n"
    for msg in history:
        prompt += f"{msg['role'].upper()}: {msg['content']}\n"
    prompt += f"\nUSER: {command_text}\nJARVIS: "
    return prompt

def call_openclaw(url, command_text, history=[]):
    print(f"[OpenClaw] Enviando comando...")
    full_prompt = build_prompt_with_history(command_text, history)
    
    data = json.dumps({
        "model": "openclaw/default",
        "user": "jarvis-wallpaper",
        "messages": [
            {"role": "system", "content": full_prompt}
        ]
    }).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            return response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
    except Exception as e:
        return f"Error OpenClaw: {e}"

def call_gemini(api_key, command_text, history=[]):
    print("[Gemini] Enviando comando...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    full_prompt = build_prompt_with_history(command_text, history)
    
    data = json.dumps({
        "contents": [{"parts": [{"text": full_prompt}]}]
    }).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print(f"Error Gemini: {e}")
        return "No pude conectarme al motor Gemini."

def call_openai(api_key, command_text, history=[]):
    print("[OpenAI] Enviando comando...")
    url = "https://api.openai.com/v1/chat/completions"
    
    # OpenAI soporta mensajes system directamente
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history:
        messages.append({"role": "user" if msg["role"] == "user" else "assistant", "content": msg["content"]})
    messages.append({"role": "user", "content": command_text})

    data = json.dumps({
        "model": "gpt-3.5-turbo",
        "messages": messages
    }).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {api_key}"
    }, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error OpenAI: {e}")
        return "No pude conectarme al motor de OpenAI."

def send_to_provider(config, command_text, history=[]):
    provider = config.get("provider", "openclaw")
    if provider == "openclaw":
        return call_openclaw(config.get("openclaw_url"), command_text, history)
    elif provider == "gemini":
        return call_gemini(config.get("gemini_api_key"), command_text, history)
    elif provider == "openai":
        return call_openai(config.get("openai_api_key"), command_text, history)
    return "Error: Proveedor no válido en la configuración."
