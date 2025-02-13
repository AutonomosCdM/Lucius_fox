import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from agents.calendar_agent import CalendarAgent

async def test_sarah():
    print("🤖 Iniciando prueba de Sarah (Calendar Agent)...")
    sarah = CalendarAgent()
    
    # Test 1: Buscar slots en horario laboral
    print("\n📝 Test 1: Buscar slots disponibles en horario laboral")
    message = "Necesito una reunión mañana a las 10 AM de 1 hora"
    result = await sarah.process(message, {'timezone': 'America/Santiago'})
    print(f"Respuesta: {result}")
    
    # Test 2: Reunión con participantes y duración específica
    print("\n📝 Test 2: Reunión con participantes")
    message = "Agenda una llamada mañana por la tarde de 30 minutos con juan@example.com y maria@example.com"
    result = await sarah.process(message, {'timezone': 'America/Santiago'})
    print(f"Respuesta: {result}")
    
    # Test 3: Evento fuera de horario laboral
    print("\n📝 Test 3: Reunión fuera de horario laboral")
    message = "Necesito una reunión mañana a las 7 AM"
    result = await sarah.process(message, {'timezone': 'America/Santiago'})
    print(f"Respuesta: {result}")
    
    # Test 4: Evento de todo el día
    print("\n📝 Test 4: Evento de todo el día")
    message = "Mañana estaré en la oficina todo el día"
    result = await sarah.process(message, {'timezone': 'America/Santiago'})
    print(f"Respuesta: {result}")
    
    # Test 5: Reunión virtual
    print("\n📝 Test 5: Reunión virtual")
    message = "Agenda una videollamada mañana a las 11 AM con el equipo tech@company.com"
    result = await sarah.process(message, {'timezone': 'America/Santiago'})
    print(f"Respuesta: {result}")

if __name__ == "__main__":
    asyncio.run(test_sarah())
