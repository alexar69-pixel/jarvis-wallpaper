import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Los permisos que pedimos a Google (solo lectura de calendario)
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_calendar_service():
    """Autentica al usuario usando OAuth2 y devuelve el servicio de Google Calendar."""
    creds = None
    # El archivo token.json almacena los tokens de acceso y actualización del usuario, y se crea
    # automáticamente la primera vez que completamos la autorización.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # Si no hay credenciales válidas, dejamos que el usuario inicie sesión.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('backend/credentials.json'):
                print("[Calendar] No se encuentra backend/credentials.json. Omitiendo calendario.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file('backend/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Guardamos el token para la próxima vez
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"[Calendar] Error construyendo el servicio: {e}")
        return None

def get_todays_agenda():
    """Obtiene los eventos del día de hoy y los devuelve como un string en lenguaje natural."""
    service = get_calendar_service()
    if not service:
        return "No tengo acceso al calendario porque faltan las credenciales."
        
    now = datetime.datetime.utcnow()
    # Empezar hoy a las 00:00
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
    # Terminar hoy a las 23:59
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat() + 'Z'

    try:
        events_result = service.events().list(
            calendarId='primary', timeMin=start_of_day, timeMax=end_of_day,
            maxResults=10, singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            return "No tienes ningún evento programado para hoy."

        agenda_text = f"Tienes {len(events)} eventos hoy: "
        event_descriptions = []
        
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            # Convertir formato ISO a hora legible (asumiendo zona horaria local devuelta por google)
            if 'T' in start:
                time_str = start.split('T')[1][:5]
                event_descriptions.append(f"A las {time_str}, {event['summary']}")
            else:
                event_descriptions.append(f"Todo el día: {event['summary']}")
                
        agenda_text += ". ".join(event_descriptions) + "."
        return agenda_text
        
    except Exception as e:
        print(f"[Calendar] Error obteniendo eventos: {e}")
        return "Hubo un error al intentar leer los eventos del calendario."
