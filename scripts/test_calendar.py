import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo
from services.google_calendar import GoogleCalendarService

async def test_calendar_service():
    try:
        # Inicializar servicio
        service = GoogleCalendarService()
        print("✅ Servicio inicializado correctamente")
        
        # Obtener lista de calendarios
        calendars = await service.get_calendar_list()
        print("\n📅 Calendarios disponibles:")
        for calendar in calendars:
            print(f"- {calendar['summary']} ({'Principal' if calendar.get('primary') else 'Secundario'})")
        
        # Obtener eventos de hoy en zona horaria de Santiago
        today = datetime.now(ZoneInfo('America/Santiago'))
        events = await service.get_events_for_date(today)
        print(f"\n📋 Eventos para hoy ({today.strftime('%Y-%m-%d')}):")
        if events:
            for event in events:
                print(f"- {event['summary']}")
                # Detectar si es un evento de todo el día
                is_all_day = event.get('all_day', False)
                if is_all_day:
                    print("  📅 Evento de todo el día")
                else:
                    # Formatear hora en zona horaria local
                    start_time = event['start'].astimezone(ZoneInfo('America/Santiago'))
                    end_time = event['end'].astimezone(ZoneInfo('America/Santiago'))
                    print(f"  ⏰ {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')} ({start_time.strftime('%Z')})")
                if event.get('attendees'):
                    print("  Participantes:", ", ".join(a['email'] for a in event['attendees']))
        else:
            print("No hay eventos programados para hoy")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_calendar_service())
