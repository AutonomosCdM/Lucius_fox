from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dateutil import parser as date_parser

class GoogleCalendarService:
    """Servicio para interactuar con Google Calendar API"""
    
    def __init__(self, timezone: str = 'America/Santiago'):
        """Inicializa el servicio de Google Calendar
        
        Args:
            timezone: Zona horaria para todas las operaciones del calendario
        """
        self.service = None
        self.timezone = ZoneInfo(timezone)
        self.initialize_service()
    
    def initialize_service(self):
        """Inicializa la conexión con Google Calendar API"""
        try:
            # Obtener ruta base del proyecto
            base_path = Path('/Users/autonomos_dev/Projects/autonomos/lucius_fox')
            creds_path = base_path / 'credentials' / 'calendar_credentials.json'
            
            # Cargar credenciales desde el archivo
            creds = Credentials.from_authorized_user_file(
                str(creds_path),
                ['https://www.googleapis.com/auth/calendar']
            )
            
            # Construir el servicio
            self.service = build('calendar', 'v3', credentials=creds)
        except Exception as e:
            print(f"Error initializing calendar service: {e}")
            raise
    
    def _parse_datetime(self, dt_str: str) -> datetime:
        """Parsea una fecha/hora de la API a datetime con zona horaria"""
        if 'T' not in dt_str:  # Es solo fecha
            return datetime.strptime(dt_str, '%Y-%m-%d').replace(tzinfo=self.timezone)
        
        # Usar dateutil.parser para manejar cualquier formato de fecha/hora
        dt = date_parser.parse(dt_str)
        
        # Asegurar que tiene zona horaria
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo('UTC'))
        
        # Convertir a la zona horaria local
        return dt.astimezone(self.timezone)
    
    def _format_datetime(self, dt: datetime) -> Dict[str, str]:
        """Formatea un datetime para la API de Google Calendar"""
        # Asegurar que tiene zona horaria
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=self.timezone)
        
        return {
            'dateTime': dt.isoformat(),
            'timeZone': str(self.timezone)
        }

    async def get_events_for_date(
        self,
        date: datetime,
        calendar_id: str = 'primary'
    ) -> List[Dict[str, Any]]:
        """Obtiene eventos para una fecha específica"""
        try:
            # Asegurar que la fecha está en la zona horaria correcta
            if date.tzinfo is None:
                date = date.replace(tzinfo=self.timezone)
            local_date = date.astimezone(self.timezone)
            
            # Configurar rango de tiempo (día completo en hora local)
            time_min = datetime.combine(local_date.date(), datetime.min.time())
            time_min = time_min.replace(tzinfo=self.timezone)
            
            time_max = datetime.combine(local_date.date(), datetime.max.time())
            time_max = time_max.replace(tzinfo=self.timezone)
            
            # Llamar a la API
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min.isoformat(),
                timeMax=time_max.isoformat(),
                singleEvents=True,
                orderBy='startTime',
                timeZone=str(self.timezone)
            ).execute()
            
            # Procesar eventos
            events = []
            for event in events_result.get('items', []):
                # Detectar si es un evento de todo el día
                is_all_day = 'date' in event['start']
                
                # Obtener inicio y fin del evento
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                # Parsear fechas asegurando zona horaria correcta
                start_dt = self._parse_datetime(start)
                end_dt = self._parse_datetime(end)
                
                events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'Sin título'),
                    'start': start_dt,
                    'end': end_dt,
                    'attendees': event.get('attendees', []),
                    'location': event.get('location'),
                    'description': event.get('description'),
                    'status': event.get('status'),
                    'all_day': is_all_day,
                    'recurring': bool(event.get('recurrence')),
                    'video_call': bool(event.get('hangoutLink') or event.get('conferenceData'))
                })
            
            return events
            
        except HttpError as error:
            print(f"Error getting events: {error}")
            return []
    
    async def create_event(self, event_details: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo evento en el calendario"""
        try:
            event = self.service.events().insert(
                calendarId='primary',
                body=event_details,
                conferenceDataVersion=1 if event_details.get('conferenceData') else 0
            ).execute()
            
            return {
                'id': event['id'],
                'summary': event.get('summary', 'Sin título'),
                'start': event['start'],
                'end': event['end'],
                'attendees': event.get('attendees', []),
                'location': event.get('location'),
                'meet_link': event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri'),
                'status': event.get('status')
            }
            
        except HttpError as error:
            print(f"Error creating event: {error}")
            raise
    
    async def update_event(
        self,
        event_id: str,
        event_details: Dict[str, Any],
        calendar_id: str = 'primary'
    ) -> Dict[str, Any]:
        """Actualiza un evento existente"""
        try:
            event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event_details
            ).execute()
            
            return {
                'id': event['id'],
                'summary': event.get('summary', 'Sin título'),
                'start': event['start'],
                'end': event['end'],
                'attendees': event.get('attendees', []),
                'status': event.get('status')
            }
            
        except HttpError as error:
            print(f"Error updating event: {error}")
            raise
    
    async def delete_event(
        self,
        event_id: str,
        calendar_id: str = 'primary'
    ) -> bool:
        """Elimina un evento del calendario"""
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            return True
            
        except HttpError as error:
            print(f"Error deleting event: {error}")
            return False
    
    async def check_availability(
        self,
        start_time: datetime,
        duration: int,
        participants: List[str],
        calendar_id: str = 'primary'
    ) -> bool:
        """Verifica disponibilidad para un horario específico"""
        try:
            # Asegurar zona horaria
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=self.timezone)
            
            # Configurar rango de tiempo
            end_time = start_time + timedelta(minutes=duration)
            
            # Formatear fechas para la API
            time_min_dict = self._format_datetime(start_time)
            time_max_dict = self._format_datetime(end_time)
            
            # Verificar calendario principal
            events = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min_dict['dateTime'],
                timeMax=time_max_dict['dateTime'],
                singleEvents=True,
                timeZone=time_min_dict['timeZone']
            ).execute()
            
            if events.get('items', []):
                return False
            
            # Verificar disponibilidad de participantes
            if participants:
                freebusy_query = {
                    'timeMin': time_min_dict['dateTime'],
                    'timeMax': time_max_dict['dateTime'],
                    'timeZone': time_min_dict['timeZone'],
                    'items': [{'id': email} for email in participants]
                }
                
                freebusy = self.service.freebusy().query(body=freebusy_query).execute()
                calendars = freebusy.get('calendars', {})
                
                # Verificar si algún participante está ocupado
                for calendar in calendars.values():
                    if calendar.get('busy', []):
                        return False
            
            return True
            
        except HttpError as error:
            print(f"Error checking availability: {error}")
            return False
    
    async def get_calendar_list(self) -> List[Dict[str, Any]]:
        """Obtiene la lista de calendarios disponibles"""
        try:
            calendars_result = self.service.calendarList().list().execute()
            
            return [{
                'id': calendar['id'],
                'summary': calendar.get('summary', 'Sin título'),
                'description': calendar.get('description'),
                'primary': calendar.get('primary', False)
            } for calendar in calendars_result.get('items', [])]
            
        except HttpError as error:
            print(f"Error getting calendar list: {error}")
            return []
