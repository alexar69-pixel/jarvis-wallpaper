import cv2
import asyncio
import time

async def vision_listener_loop(broadcast_callback):
    """
    Inicia la webcam en segundo plano. Escanea frames cada pocos segundos para 
    no saturar la CPU y busca rostros.
    Si detecta un rostro tras un tiempo sin ver a nadie, dispara el callback.
    """
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # 0 es la camara principal de Windows. Usamos DSHOW para evitar errores MSMF
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    # Flags de estado
    is_user_present = False
    last_seen_time = time.time()
    
    # Tiempo de ausencia (en segundos) para considerar que el usuario se fue
    # y así volver a saludarle al volver.
    ABSENCE_THRESHOLD = 60 

    while True:
        try:
            # Para no bloquear el loop de asyncio, cedemos control con un sleep
            await asyncio.sleep(1.0)
            
            # Solo leemos la cámara si está abierta
            if not cap.isOpened():
                continue
                
            ret, frame = cap.read()
            if not ret:
                continue
                
            # Convertimos a escala de grises para que el detector sea más rápido
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detectamos rostros
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(100, 100) # Rostros grandes (alguien sentado cerca)
            )
            
            if len(faces) > 0:
                # Vemos un rostro
                current_time = time.time()
                
                if not is_user_present:
                    # El usuario acaba de sentarse (o llevaba más de ABSENCE_THRESHOLD sin ser visto)
                    is_user_present = True
                    print("[Sistema] Rostro detectado en la Webcam. Usuario ha vuelto.")
                    await broadcast_callback({"type": "face_detected"})
                
                last_seen_time = current_time
            else:
                # No vemos rostro
                current_time = time.time()
                if is_user_present and (current_time - last_seen_time > ABSENCE_THRESHOLD):
                    is_user_present = False
                    print("[Sistema] Usuario se ha ido de la Webcam. Entrando en Modo Reposo.")
                    await broadcast_callback({"type": "action", "value": "sleep_mode"})
                    await broadcast_callback({"type": "face_lost"})
                    
        except Exception as e:
            print(f"[Vision] Error en loop de webcam: {e}")
            await asyncio.sleep(5)
            
    cap.release()
