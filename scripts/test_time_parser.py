import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo
from utils.enhanced_time_parser import EnhancedTimeParser

def test_time_parser():
    print("🕒 Probando EnhancedTimeParser...")
    parser = EnhancedTimeParser()
    
    test_cases = [
        # Fechas relativas
        "necesito una reunión mañana",
        "agenda para hoy en la tarde",
        "reunión para pasado mañana",
        
        # Horas específicas
        "reunión a las 3 pm",
        "llamada a las 15:30",
        "meeting at 9:00 am",
        
        # Momentos del día
        "reunión por la mañana",
        "meeting in the afternoon",
        "llamada en la tarde",
        
        # Duraciones
        "reunión de 30 minutos",
        "llamada de 1 hora",
        "meeting for 2 hours",
        
        # Participantes
        "reunión con juan@example.com y maria@example.com",
        "call with tech@company.com",
        
        # Casos complejos
        "reunión mañana a las 10 am por 2 horas con juan@example.com",
        "llamada en la tarde de 30 minutos con el equipo tech@company.com"
    ]
    
    for text in test_cases:
        print(f"\n📝 Texto: {text}")
        
        # Extraer fecha y hora
        dt = parser.extract_datetime(text)
        if dt:
            print(f"   📅 Fecha/Hora: {dt.strftime('%Y-%m-%d %H:%M %Z')}")
        else:
            print("   ❌ No se pudo extraer fecha/hora")
        
        # Extraer duración
        duration = parser.extract_duration(text)
        if duration:
            print(f"   ⏱️  Duración: {duration} minutos")
        else:
            print("   ❌ No se pudo extraer duración")
        
        # Extraer emails
        emails = parser.extract_emails(text)
        if emails:
            print(f"   📧 Emails: {', '.join(emails)}")
        else:
            print("   ❌ No se encontraron emails")

if __name__ == "__main__":
    test_time_parser()
