import asyncio
import websockets
import json
import threading
import speech_recognition as sr
import edge_tts
import pygame
import os
import tempfile
import psutil
import urllib.request
import webbrowser
import subprocess
import re

from config_manager import load_config
from providers import send_to_provider
from memory import add_message, get_recent_history
from web_search import invisible_search
from media import media_listener_loop
from vision import vision_listener_loop

connected_clients = set()
config = load_config()
pygame.mixer.init()

# Global state for weather so we don't spam the API
weather_data = {"temp": "--", "desc": "Offline"}

async def broadcast_state(state):
    if connected_clients:
        message = json.dumps({"type": "state", "value": state})
        await asyncio.gather(*[client.send(message) for client in connected_clients])

async def broadcast_custom(data_dict):
    if connected_clients:
        message = json.dumps(data_dict)
        await asyncio.gather(*[client.send(message) for client in connected_clients])

async def event_handler_callback(data):
    # Enviar al frontend
    await broadcast_custom(data)
    
    # Si detectamos que el usuario vuelve, saludamos
    if data.get("type") == "face_detected":
        print("[Jarvis]: Bienvenido de nuevo, señor.")
        asyncio.run_coroutine_threadsafe(broadcast_state("SPEAKING"), loop)
        future = asyncio.run_coroutine_threadsafe(speak_text_edge("Bienvenido de nuevo, señor. Sistemas en línea.", config.get("voice"), loop), loop)
        future.result()
        asyncio.run_coroutine_threadsafe(broadcast_state("IDLE"), loop)

def process_audio(text, loop):
    print(f"\n[Reconocido]: {text}")
    
    # 1. Añadir a memoria y buscar historial
    add_message("user", text)
    history = get_recent_history(limit=6)
    
    # 2. Llamada inicial al LLM
    response = send_to_provider(config, text, history)
    
    # 3. Interceptar Búsqueda Web
    search_match = re.search(r'\[SEARCH:\s*(.*?)\]', response, re.IGNORECASE)
    if search_match:
        query = search_match.group(1).strip()
        print(f"[Sistema] Interceptada petición de búsqueda web para: {query}")
        
        # Realizamos la búsqueda
        search_result = invisible_search(query)
        print(f"[Sistema] Resultado extraído: {search_result[:100]}...")
        
        # Añadimos el resultado a la memoria como sistema y pedimos respuesta final
        add_message("system", f"[RESULTADO BÚSQUEDA WEB PARA '{query}']: {search_result}")
        
        # Volvemos a pedirle al LLM que construya la respuesta
        history = get_recent_history(limit=8)
        response = send_to_provider(config, "Ya he realizado la búsqueda en internet. Usa la información de la memoria para responderme de forma natural.", history)

    # 4. Limpiar posibles restos de tags y guardar
    response = re.sub(r'\[SEARCH:.*?\]', '', response).strip()
    print(f"[Jarvis]: {response}")
    add_message("jarvis", response)
    
    # Reproducir audio
    asyncio.run_coroutine_threadsafe(broadcast_state("SPEAKING"), loop)
    # Reutilizamos lógica de voz existente
    future = asyncio.run_coroutine_threadsafe(speak_text_edge(response, config.get("voice"), loop), loop)
    future.result()
    asyncio.run_coroutine_threadsafe(broadcast_state("IDLE"), loop)

async def fetch_weather_loop():
    while True:
        config_data = load_config()
        loc = config_data.get("location", "Madrid")
        try:
            url = f"https://wttr.in/{urllib.parse.quote(loc)}?format=j1"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                current = data['current_condition'][0]
                weather_data['temp'] = current['temp_C']
                weather_data['desc'] = current['weatherDesc'][0]['value']
                weather_data['location'] = loc
        except Exception as e:
            print(f"Error fetching weather: {e}")
        # Update every 30 minutes
        await asyncio.sleep(1800)

async def telemetry_loop():
    while True:
        if connected_clients:
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage('C:\\').percent
            
            telemetry_msg = {
                "type": "telemetry",
                "cpu": cpu,
                "ram": ram,
                "disk": disk,
                "weather": weather_data
            }
            await send_to_clients(telemetry_msg)
            
        await asyncio.sleep(2)

async def send_to_clients(message_dict):
    if connected_clients:
        message_json = json.dumps(message_dict)
        await asyncio.gather(*[client.send(message_json) for client in connected_clients])

async def speak_text_edge(text, voice, loop):
    await send_to_clients({"type": "message", "text": text})
    try:
        communicate = edge_tts.Communicate(text, voice)
        temp_file = os.path.join(tempfile.gettempdir(), "jarvis_response.mp3")
        await communicate.save(temp_file)
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)
        pygame.mixer.music.unload()
    except Exception as e:
        print(f"Error reproduciendo TTS: {e}")

import sys

def handle_action(app_name, loop):
    print(f"Lanzando aplicación: {app_name}")
    try:
        if app_name == 'settings':
            gui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gui.py')
            os.startfile(gui_path)
        elif app_name == 'chrome':
            subprocess.Popen(['start', 'chrome'], shell=True)
        elif app_name == 'firefox':
            subprocess.Popen(['start', 'firefox'], shell=True)
        elif app_name == 'brave':
            subprocess.Popen(['start', 'brave'], shell=True)
        elif app_name == 'explorer':
            subprocess.Popen(['explorer', 'C:\\'], shell=True)
        elif app_name == 'discord':
            # Discord usually installs to LocalAppData
            discord_path = os.path.join(os.environ['LOCALAPPDATA'], 'Discord', 'Update.exe')
            if os.path.exists(discord_path):
                subprocess.Popen([discord_path, '--processStart', 'Discord.exe'])
            else:
                asyncio.run_coroutine_threadsafe(speak_text_edge("No pude encontrar Discord.", load_config().get("voice"), loop), loop)
        elif app_name == 'gemini':
            webbrowser.open('https://gemini.google.com')
        elif app_name == 'chatgpt':
            webbrowser.open('https://chatgpt.com')
        else:
            print("Aplicación no soportada.")
    except Exception as e:
        print(f"Error lanzando app: {e}")

def stt_loop(loop):
    config = load_config()
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    wake_word = config.get("wake_word", "jarvis").lower()
    
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
    print(f"Motor STT iniciado. Di '{wake_word}' para activar.")
    
    while True:
        try:
            with microphone as source:
                audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio, language="es-ES").lower()
            if wake_word in text:
                asyncio.run_coroutine_threadsafe(send_to_clients({"type": "state", "state": "LISTENING"}), loop)
                asyncio.run_coroutine_threadsafe(send_to_clients({"type": "message", "text": "Escuchando comando..."}), loop)
                config = load_config()
                with microphone as source:
                    audio_command = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                command_text = recognizer.recognize_google(audio_command, language="es-ES").lower()
                
                # Zero-config interceptors
                if "alerta roja" in command_text or "código rojo" in command_text:
                    asyncio.run_coroutine_threadsafe(send_to_clients({"type": "action", "value": "red_alert"}), loop)
                    future = asyncio.run_coroutine_threadsafe(speak_text_edge("Sistemas de defensa activados. Alerta Roja iniciada.", config.get("voice"), loop), loop)
                    future.result()
                    continue
                elif "desactiva la alerta" in command_text or "cancela la alerta" in command_text:
                    asyncio.run_coroutine_threadsafe(send_to_clients({"type": "action", "value": "red_alert_off"}), loop)
                    future = asyncio.run_coroutine_threadsafe(speak_text_edge("Alerta cancelada. Volviendo a parámetros normales.", config.get("voice"), loop), loop)
                    future.result()
                    continue
                
                open_match = re.search(r'^(abre|inicia|arranca) (.*)', command_text)
                if open_match:
                    app_to_open = open_match.group(2).strip()
                    asyncio.run_coroutine_threadsafe(speak_text_edge(f"Iniciando {app_to_open}, señor.", config.get("voice"), loop), loop)
                    try:
                        subprocess.Popen(f'start {app_to_open}', shell=True)
                    except Exception as e:
                        print(f"Error abriendo app: {e}")
                    asyncio.run_coroutine_threadsafe(send_to_clients({"type": "state", "state": "IDLE"}), loop)
                    continue
                
                asyncio.run_coroutine_threadsafe(send_to_clients({"type": "state", "state": "PROCESSING"}), loop)
                asyncio.run_coroutine_threadsafe(send_to_clients({"type": "message", "text": f"Procesando en {config.get('provider')}..."}), loop)
                respuesta = send_to_provider(config, command_text)
                
                # Cambiar UI a SPEAKING mientras habla
                asyncio.run_coroutine_threadsafe(send_to_clients({"type": "state", "state": "SPEAKING"}), loop)
                
                future = asyncio.run_coroutine_threadsafe(speak_text_edge(respuesta, config.get("voice"), loop), loop)
                future.result()
                
                asyncio.run_coroutine_threadsafe(send_to_clients({"type": "state", "state": "IDLE"}), loop)
                asyncio.run_coroutine_threadsafe(send_to_clients({"type": "message", "text": "Sistemas en espera."}), loop)
        except sr.UnknownValueError:
            asyncio.run_coroutine_threadsafe(send_to_clients({"type": "state", "state": "IDLE"}), loop)
        except sr.WaitTimeoutError:
            asyncio.run_coroutine_threadsafe(send_to_clients({"type": "state", "state": "IDLE"}), loop)
        except Exception:
            asyncio.run_coroutine_threadsafe(send_to_clients({"type": "state", "state": "IDLE"}), loop)

async def handler(websocket):
    print("Frontend conectado!")
    connected_clients.add(websocket)
    try:
        config = load_config()
        await websocket.send(json.dumps({"type": "state", "state": "IDLE"}))
        await websocket.send(json.dumps({"type": "message", "text": f"Motor HUD activo."}))
        
        async for message in websocket:
            try:
                data = json.loads(message)
                if data.get('type') == 'action' and data.get('action') == 'launch_app':
                    loop = asyncio.get_running_loop()
                    handle_action(data.get('app'), loop)
            except Exception as e:
                print(f"Error processing client message: {e}")
                
    except websockets.exceptions.ConnectionClosed:
        print("Frontend desconectado.")
    finally:
        connected_clients.remove(websocket)

async def main():
    loop = asyncio.get_running_loop()
    config = load_config()
    
    # Start background threads & loops
    stt_thread = threading.Thread(target=stt_loop, args=(loop,), daemon=True)
    stt_thread.start()
    
    asyncio.create_task(telemetry_loop())
    asyncio.create_task(fetch_weather_loop())
    asyncio.create_task(media_listener_loop(event_handler_callback))
    asyncio.create_task(vision_listener_loop(event_handler_callback))
    
    print("Servidor WebSocket iniciado en ws://127.0.0.1:8765...")
    async with websockets.serve(handler, "127.0.0.1", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
