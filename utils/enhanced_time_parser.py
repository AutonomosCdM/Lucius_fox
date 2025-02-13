from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from zoneinfo import ZoneInfo
import re

class EnhancedTimeParser:
    """Versión mejorada del parser de tiempo con soporte para zonas horarias"""
    
    def __init__(self, timezone: str = 'America/Santiago'):
        self.timezone = ZoneInfo(timezone)
        
        self.time_patterns = {
            'morning': (9, 12),    # 9 AM - 12 PM
            'afternoon': (13, 17), # 1 PM - 5 PM
            'evening': (17, 19),   # 5 PM - 7 PM,
            'mañana': (9, 12),
            'tarde': (13, 17),
            'noche': (17, 19)
        }
        
        self.day_aliases = {
            'hoy': 0,
            'mañana': 1,
            'pasado': 2,
            'próximo': 7,
            'today': 0,
            'tomorrow': 1,
            'next': 7
        }
        
        self.duration_patterns = {
            'minutos?': 1,
            'minutes?': 1,
            'horas?': 60,
            'hours?': 60
        }
    
    def extract_datetime(self, text: str) -> Optional[datetime]:
        """Extrae fecha y hora de un texto"""
        text = text.lower()
        now = datetime.now(self.timezone)
        
        # Buscar referencias a días
        date = now.date()
        for alias, days in self.day_aliases.items():
            if alias in text:
                date = (now + timedelta(days=days)).date()
                break
        
        # Buscar referencias a momentos del día
        for moment, (start_hour, end_hour) in self.time_patterns.items():
            if moment in text or f'por la {moment}' in text:
                return datetime.combine(date, datetime.strptime(f"{start_hour}:00", "%H:%M").time()).replace(tzinfo=self.timezone)
        
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
                time = datetime.strptime(f"{hour}:{minutes}", "%H:%M").time()
                return datetime.combine(date, time).replace(tzinfo=self.timezone)
            except ValueError:
                return None
        
        # Si no se encontró hora específica pero sí fecha, usar hora por defecto (9 AM)
        if date != now.date():
            return datetime.combine(date, datetime.strptime("9:00", "%H:%M").time()).replace(tzinfo=self.timezone)
        
        return None
    
    def extract_duration(self, text: str) -> Optional[int]:
        """Extrae duración en minutos de un texto"""
        text = text.lower()
        
        # Buscar patrones de duración
        for pattern, multiplier in self.duration_patterns.items():
            matches = re.finditer(f'(\\d+)\\s*{pattern}', text)
            for match in matches:
                return int(match.group(1)) * multiplier
        
        # Buscar duración en horas
        hour_match = re.search(r'(\d+)\s*h', text)
        if hour_match:
            return int(hour_match.group(1)) * 60
        
        # Buscar duración en minutos
        min_match = re.search(r'(\d+)\s*min', text)
        if min_match:
            return int(min_match.group(1))
        
        # Duración por defecto si se menciona reunión
        if any(word in text for word in ['reunión', 'meeting', 'call']):
            return 60
        
        return None
    
    def extract_emails(self, text: str) -> List[str]:
        """Extrae direcciones de email del texto"""
        return re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
