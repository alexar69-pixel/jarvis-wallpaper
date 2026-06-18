import asyncio
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager

async def get_current_media_info():
    """
    Recupera el título y artista de la música que está sonando actualmente en Windows
    usando la API asíncrona de Winsdk.
    """
    try:
        manager = await GlobalSystemMediaTransportControlsSessionManager.request_async()
        session = manager.get_current_session()
        
        if session:
            media_properties = await session.try_get_media_properties_async()
            if media_properties:
                title = media_properties.title
                artist = media_properties.artist
                
                # Devolvemos un diccionario con los datos
                if title:
                    return {"title": title, "artist": artist}
    except Exception as e:
        print(f"[Media] Error leyendo metadata: {e}")
        
    return None

async def media_listener_loop(broadcast_callback):
    """
    Loop asíncrono que comprueba la canción cada 2 segundos y si cambia,
    lanza el callback para enviarlo por WebSocket al frontend.
    """
    current_title = None
    
    while True:
        try:
            media_info = await get_current_media_info()
            if media_info:
                new_title = media_info.get("title")
                new_artist = media_info.get("artist")
                
                # Si la canción ha cambiado, lo notificamos
                if new_title != current_title:
                    current_title = new_title
                    print(f"[Sistema] Nueva canción detectada: {new_title} - {new_artist}")
                    await broadcast_callback({"type": "media", "title": new_title, "artist": new_artist})
            else:
                # Si no hay música o se detuvo
                if current_title is not None:
                    current_title = None
                    await broadcast_callback({"type": "media", "title": "", "artist": ""})
                    
        except Exception as e:
            pass
            
        await asyncio.sleep(2)
