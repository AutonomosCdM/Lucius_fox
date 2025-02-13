from datetime import datetime, timedelta
from typing import List, Dict, Any

class DateUtils:
    """Utilidad para operaciones con fechas y slots de tiempo"""
    
    def __init__(self):
        self.min_slot_duration = 15  # minutos mínimos por slot
        self.buffer_time = 15       # tiempo de buffer entre reuniones
    
    def find_free_slots(
        self,
        start_time: datetime,
        end_time: datetime,
        existing_events: List[Dict[str, Any]],
        duration_minutes: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Encuentra slots libres entre dos tiempos dados, considerando eventos existentes
        
        Args:
            start_time: Inicio del período a buscar
            end_time: Fin del período a buscar
            existing_events: Lista de eventos existentes con 'start' y 'end'
            duration_minutes: Duración deseada del slot en minutos
            
        Returns:
            Lista de slots disponibles con 'start' y 'end'
        """
        # Ordenar eventos existentes
        events = sorted(existing_events, key=lambda x: x['start'])
        
        # Inicializar lista de slots disponibles
        free_slots = []
        current_time = start_time
        
        # Iterar sobre eventos existentes
        for event in events:
            event_start = event['start']
            event_end = event['end']
            
            # Si hay suficiente tiempo antes del evento
            if (event_start - current_time).total_seconds() / 60 >= (duration_minutes + self.buffer_time):
                free_slots.append({
                    'start': current_time,
                    'end': event_start - timedelta(minutes=self.buffer_time)
                })
            
            current_time = event_end + timedelta(minutes=self.buffer_time)
        
        # Verificar el último período
        if (end_time - current_time).total_seconds() / 60 >= duration_minutes:
            free_slots.append({
                'start': current_time,
                'end': end_time
            })
        
        # Dividir slots largos en slots más pequeños
        return self._divide_slots(free_slots, duration_minutes)
    
    def _divide_slots(
        self,
        slots: List[Dict[str, Any]],
        duration_minutes: int
    ) -> List[Dict[str, Any]]:
        """Divide slots largos en slots más pequeños de la duración especificada"""
        divided_slots = []
        
        for slot in slots:
            current = slot['start']
            while current + timedelta(minutes=duration_minutes) <= slot['end']:
                divided_slots.append({
                    'start': current,
                    'end': current + timedelta(minutes=duration_minutes)
                })
                current += timedelta(minutes=duration_minutes + self.buffer_time)
        
        return divided_slots
    
    def merge_availability(
        self,
        availabilities: List[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Combina múltiples listas de disponibilidad para encontrar slots comunes
        
        Args:
            availabilities: Lista de listas de slots disponibles
            
        Returns:
            Lista de slots disponibles comunes
        """
        if not availabilities:
            return []
        
        # Comenzar con el primer conjunto de slots
        common_slots = availabilities[0]
        
        # Intersectar con cada conjunto adicional
        for availability in availabilities[1:]:
            common_slots = self._find_overlapping_slots(common_slots, availability)
        
        return common_slots
    
    def _find_overlapping_slots(
        self,
        slots1: List[Dict[str, Any]],
        slots2: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Encuentra la intersección de dos conjuntos de slots"""
        overlapping = []
        
        for slot1 in slots1:
            for slot2 in slots2:
                # Encontrar solapamiento
                start = max(slot1['start'], slot2['start'])
                end = min(slot1['end'], slot2['end'])
                
                # Si hay solapamiento válido
                if start < end:
                    overlapping.append({
                        'start': start,
                        'end': end
                    })
        
        return overlapping
    
    def get_next_business_day(self, date: datetime = None) -> datetime:
        """Obtiene el siguiente día hábil"""
        if date is None:
            date = datetime.now()
        
        # Avanzar un día
        next_day = date + timedelta(days=1)
        
        # Si cae en fin de semana, avanzar al lunes
        while next_day.weekday() >= 5:  # 5 = Sábado, 6 = Domingo
            next_day += timedelta(days=1)
        
        return next_day
    
    def format_time_range(self, start: datetime, end: datetime) -> str:
        """Formatea un rango de tiempo de manera amigable"""
        if start.date() == end.date():
            return f"{start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}"
        return f"{start.strftime('%b %d, %I:%M %p')} - {end.strftime('%b %d, %I:%M %p')}"
