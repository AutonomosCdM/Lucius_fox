from datetime import datetime, timedelta
from typing import Optional
import re

class TimeParser:
    """Utilidad para parsear fechas y horas de mensajes en lenguaje natural"""
    
    def __init__(self):
        self.time_patterns = {
            'morning': (9, 12),    # 9 AM - 12 PM
            'afternoon': (13, 17), # 1 PM - 5 PM
            'evening': (17, 19),   # 5 PM - 7 PM
        }
        
        self.day_aliases = {
            'hoy': 0,
            'mañana': 1,
            'pasado': 2,
            'próximo': 7
        }
    
    def extract_datetime(self, text: str) -> Optional[datetime]:
        """Extrae fecha y hora de un texto"""
        text = text.lower()
        now = datetime.now()
        
        # Buscar referencias a días
        date = now.date()
        for alias, days in self.day_aliases.items():
            if alias in text:
                date = (now + timedelta(days=days)).date()
                break
        
        # Buscar hora específica (formato 24h o 12h)
        time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm|hrs)?', text)
        if time_match:
            hour = int(time_match.group(1))
            minutes = int(time_match.group(2)) if time_match.group(2) else 0
            meridiem = time_match.group(3)
            
            # Ajustar hora según AM/PM
            if meridiem:
                if meridiem.lower() == 'pm' and hour < 12:
                    hour += 12
                elif meridiem.lower() == 'am' and hour == 12:
                    hour = 0
            
            try:
                return datetime.combine(date, datetime.strptime(f"{hour}:{minutes}", "%H:%M").time())
            except ValueError:
                return None
        
        # Buscar referencias a momentos del día
        for moment, (start_hour, _) in self.time_patterns.items():
            if moment in text:
                return datetime.combine(date, datetime.strptime(f"{start_hour}:00", "%H:%M").time())
        
        return None
    
    def extract_duration(self, text: str) -> Optional[int]:
        """Extrae la duración en minutos de un texto"""
        text = text.lower()
        
        # Buscar patrones de duración
        hour_match = re.search(r'(\d+)\s*hora', text)
        minute_match = re.search(r'(\d+)\s*min', text)
        
        duration = 0
        
        if hour_match:
            duration += int(hour_match.group(1)) * 60
        if minute_match:
            duration += int(minute_match.group(1))
        
        # Si no se especifica duración, usar valores por defecto según el tipo
        if duration == 0:
            if any(word in text for word in ['quick', 'rápida', 'corta']):
                duration = 30
            elif any(word in text for word in ['long', 'larga', 'extensa']):
                duration = 90
            else:
                duration = 60  # duración por defecto
        
        return duration
    
    def is_business_hours(self, dt: datetime) -> bool:
        """Verifica si una fecha/hora está dentro del horario laboral"""
        if dt.weekday() >= 5:  # Sábado o domingo
            return False
        
        return 9 <= dt.hour < 18  # 9 AM - 6 PM
