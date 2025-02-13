from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from .base_agent import BaseAgent
from .personalities.traits.organized import OrganizedPersonality
from services.google_calendar import GoogleCalendarService
from utils.enhanced_time_parser import EnhancedTimeParser
from utils.date_utils import DateUtils

class CalendarAgent(BaseAgent):
    def __init__(self):
        # Inicializar con personalidad organizada
        personality = OrganizedPersonality(
            name="Sarah",
            role="Calendar Manager",
            description="Eficiente, organizada y proactiva en la gestión del calendario"
        )
        
        super().__init__(
            name="Sarah",
            role="Calendar Manager",
            personality=personality
        )
        
        self.timezone = ZoneInfo('America/Santiago')
        self.calendar_service = GoogleCalendarService()
        self.time_parser = EnhancedTimeParser(timezone='America/Santiago')
        self.date_utils = DateUtils()
        
        # Estado interno
        self.pending_events: List[Dict[str, Any]] = []
        self.last_suggested_times: List[str] = []
        self.current_context: Dict[str, Any] = {}
        
        # Configuración de horario laboral
        self.work_hours = {
            'start': 9,  # 9 AM
            'end': 18    # 6 PM
        }

    async def get_available_slots(
        self,
        date: datetime,
        duration: int = 60,
        participants: List[str] = None,
        work_hours: Dict[str, int] = None
    ) -> List[Dict[str, Any]]:
        """Obtiene slots disponibles para una fecha específica
        
        Args:
            date: Fecha para buscar slots
            duration: Duración en minutos
            participants: Lista de emails de participantes
            work_hours: Dict con 'start' y 'end' en formato 24h (ej: {'start': 9, 'end': 18})
        """
        try:
            # Asegurar que la fecha tiene zona horaria
            if date.tzinfo is None:
                date = date.replace(tzinfo=self.timezone)
            
            # Usar horario laboral por defecto si no se especifica
            if not work_hours:
                work_hours = self.work_hours
            
            # Definir horario laboral
            work_start = date.replace(hour=work_hours['start'], minute=0)
            work_end = date.replace(hour=work_hours['end'], minute=0)
            
            # Verificar si el horario está dentro del horario laboral
            if date.hour < work_hours['start'] or date.hour >= work_hours['end']:
                return []
            
            # Verificar disponibilidad de participantes
            if participants:
                is_available = await self.calendar_service.check_availability(
                    start_time=work_start,
                    duration=duration,
                    participants=participants
                )
                if not is_available:
                    return []
            
            # Obtener eventos del día
            events = await self.calendar_service.get_events_for_date(date)
            
            # Encontrar slots disponibles
            available_slots = self.date_utils.find_free_slots(
                start_time=work_start,
                end_time=work_end,
                existing_events=events,
                duration_minutes=duration
            )
            
            # Asegurar que todos los slots tienen zona horaria
            for slot in available_slots:
                if slot['start'].tzinfo is None:
                    slot['start'] = slot['start'].replace(tzinfo=self.timezone)
                if slot['end'].tzinfo is None:
                    slot['end'] = slot['end'].replace(tzinfo=self.timezone)
            
            return available_slots
        except Exception as e:
            print(f"Error getting available slots: {e}")
            return []

    def extract_meeting_details(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae detalles de la reunión del mensaje y contexto"""
        details = {
            'date': None,
            'time': None,
            'duration': 60,  # default 60 minutes
            'participants': [],
            'title': None,
            'location': None,
            'type': 'meeting'
        }
        
        msg = message.lower()
        
        # Extraer fecha y hora
        date_time = self.time_parser.extract_datetime(msg)
        if date_time:
            details['date'] = date_time.date()
            details['time'] = date_time.time()
        
        # Extraer duración
        duration = self.time_parser.extract_duration(msg)
        if duration:
            details['duration'] = duration
        
        # Extraer participantes (emails)
        details['participants'].extend(
            word for word in msg.split() if '@' in word
        )
        
        # Extraer tipo de reunión
        if any(word in msg for word in ['1:1', 'one-on-one', 'individual']):
            details['type'] = '1on1'
        elif any(word in msg for word in ['team', 'equipo']):
            details['type'] = 'team'
        
        # Extraer ubicación
        if 'sala' in msg or 'room' in msg:
            details['location'] = 'meeting_room'
        elif any(word in msg for word in ['zoom', 'meet', 'teams', 'virtual']):
            details['location'] = 'virtual'
            
        return details

    async def schedule_meeting(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Programa una reunión con los detalles proporcionados"""
        try:
            # Verificar disponibilidad
            if details['date'] and details['time']:
                start_time = datetime.combine(details['date'], details['time'])
                is_available = await self.calendar_service.check_availability(
                    start_time=start_time,
                    duration=details['duration'],
                    participants=details['participants']
                )
                
                if not is_available:
                    return {
                        'success': False,
                        'message': 'El horario seleccionado no está disponible'
                    }
            
            # Crear evento
            event = {
                'summary': details.get('title', 'Nueva Reunión'),
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'America/Santiago'
                },
                'end': {
                    'dateTime': (start_time + timedelta(minutes=details['duration'])).isoformat(),
                    'timeZone': 'America/Santiago'
                },
                'attendees': [{'email': p} for p in details['participants']],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 15},
                    ],
                }
            }
            
            # Agregar ubicación si es necesario
            if details['location'] == 'virtual':
                event['conferenceData'] = {
                    'createRequest': {'requestId': f"meeting_{start_time.timestamp()}"}
                }
            elif details['location'] == 'meeting_room':
                # Aquí se podría integrar con un sistema de reserva de salas
                pass
            
            # Crear el evento en el calendario
            created_event = await self.calendar_service.create_event(event)
            
            return {
                'success': True,
                'event': created_event,
                'message': 'Reunión programada exitosamente'
            }
            
        except Exception as e:
            print(f"Error scheduling meeting: {e}")
            return {
                'success': False,
                'message': f"Error al programar la reunión: {str(e)}"
            }

    async def process(self, message: str, context: Dict[str, Any]) -> str:
        """Process calendar-related requests"""
        try:
            msg = message.lower()
            history = context.get('conversation_history', [])
            
            # Actualizar contexto
            self.current_context.update(context)
            
            # Extraer fecha y hora
            dt = self.time_parser.extract_datetime(msg)
            if not dt:
                return self.format_response(
                    "Estoy aquí para ayudarte con la gestión del calendario. "
                    "Puedo programar reuniones, verificar disponibilidad, "
                    "reservar salas y coordinar con los participantes. "
                    "¿Qué necesitas específicamente?"
                )
            
            # Asegurar zona horaria
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=self.timezone)
            
            # Verificar si está dentro del horario laboral
            if dt.hour < self.work_hours['start'] or dt.hour >= self.work_hours['end']:
                return self.format_response(
                    f"Lo siento, solo puedo agendar reuniones dentro del horario laboral "
                    f"({self.work_hours['start']}:00 - {self.work_hours['end']}:00)."
                )
            
            # Detectar tipo de evento
            is_all_day = 'todo el día' in msg
            is_video_call = any(word in msg for word in ['video', 'virtual', 'videollamada', 'zoom', 'meet'])
            
            # Extraer duración
            duration = self.time_parser.extract_duration(msg) or 60  # Default 1 hora
            
            # Extraer participantes
            participants = self.time_parser.extract_emails(msg)
            
            # Verificar disponibilidad si hay participantes
            if participants:
                available_slots = await self.get_available_slots(
                    date=dt,
                    duration=duration,
                    participants=participants
                )
                
                if not available_slots:
                    return self.format_response(
                        "Lo siento, no hay slots disponibles para esa fecha y hora "
                        "con los participantes indicados. ¿Quieres que busque otro horario?"
                    )
                
                # Guardar slots sugeridos en el contexto
                self.last_suggested_times = [slot['start'].strftime('%H:%M') for slot in available_slots]
                
                # Formatear respuesta con slots disponibles
                slots_str = '\n'.join([f"- {slot['start'].strftime('%H:%M')} - {slot['end'].strftime('%H:%M')}" 
                                      for slot in available_slots[:3]])
                
                video_str = " con link de videollamada" if is_video_call else ""
                return self.format_response(
                    f"He encontrado los siguientes horarios disponibles{video_str}:\n"
                    f"{slots_str}\n\n"
                    f"¿Te gustaría que agende alguno de estos horarios?"
                )
            
            # Si no hay participantes pero la fecha/hora es válida
            event_type = "videollamada" if is_video_call else "reunión"
            if is_all_day:
                return self.format_response(
                    f"¿Te gustaría que agende un evento de todo el día para el {dt.strftime('%Y-%m-%d')}? "
                    "Por favor, indícame los participantes."
                )
            else:
                return self.format_response(
                    f"¿Te gustaría que agende una {event_type} para el {dt.strftime('%Y-%m-%d')} "
                    f"a las {dt.strftime('%H:%M')}? Por favor, indícame los participantes."
                )
            
        except Exception as e:
            print(f"Error processing message: {e}")
            return self.format_response(
                "Lo siento, hubo un error procesando tu solicitud. "
                "¿Podrías reformularla de otra manera?"
            )
