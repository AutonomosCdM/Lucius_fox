import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from services.google_calendar import GoogleCalendarService

@pytest.fixture
def calendar_service():
    with patch('services.google_calendar.Credentials.from_authorized_user_file') as mock_creds,\
         patch('services.google_calendar.build') as mock_build:
        # Mock de credenciales
        mock_creds.return_value = MagicMock()
        # Mock del servicio
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        service = GoogleCalendarService()
        service.service = mock_service
        yield service

@pytest.fixture
def mock_events():
    return {
        'items': [
            {
                'id': '1',
                'summary': 'Reunión de prueba',
                'start': {'dateTime': '2025-02-13T10:00:00-03:00'},
                'end': {'dateTime': '2025-02-13T11:00:00-03:00'},
                'attendees': [
                    {'email': 'test@example.com', 'responseStatus': 'accepted'}
                ],
                'location': 'Sala Virtual',
                'description': 'Descripción de prueba',
                'status': 'confirmed'
            }
        ]
    }

@pytest.mark.asyncio
async def test_get_events_for_date(calendar_service, mock_events):
    # Configurar el mock
    calendar_service.service.events().list().execute.return_value = mock_events
    
    # Ejecutar la prueba
    date = datetime.now()
    events = await calendar_service.get_events_for_date(date)
    
    # Verificar resultados
    assert len(events) == 1
    event = events[0]
    assert event['summary'] == 'Reunión de prueba'
    assert isinstance(event['start'], datetime)
    assert isinstance(event['end'], datetime)

@pytest.mark.asyncio
async def test_create_event(calendar_service):
    # Mock de datos de evento
    event_details = {
        'summary': 'Nueva reunión',
        'start': {
            'dateTime': '2025-02-13T14:00:00-03:00',
            'timeZone': 'America/Santiago',
        },
        'end': {
            'dateTime': '2025-02-13T15:00:00-03:00',
            'timeZone': 'America/Santiago',
        },
        'attendees': [
            {'email': 'invitado@example.com'}
        ],
        'conferenceData': {
            'createRequest': {
                'requestId': 'test-request',
                'conferenceSolutionKey': {'type': 'hangoutsMeet'}
            }
        }
    }
    
    # Mock de respuesta
    mock_response = {
        'id': 'event123',
        'summary': 'Nueva reunión',
        'start': event_details['start'],
        'end': event_details['end'],
        'attendees': event_details['attendees'],
        'conferenceData': {
            'entryPoints': [
                {'uri': 'https://meet.google.com/test-code'}
            ]
        },
        'status': 'confirmed'
    }
    
    calendar_service.service.events().insert().execute.return_value = mock_response
    
    # Ejecutar prueba
    result = await calendar_service.create_event(event_details)
    
    # Verificar resultado
    assert result['id'] == 'event123'
    assert result['summary'] == 'Nueva reunión'
    assert result['meet_link'] == 'https://meet.google.com/test-code'

@pytest.mark.asyncio
async def test_check_availability(calendar_service):
    # Mock de respuesta para freebusy
    mock_freebusy = {
        'calendars': {
            'test@example.com': {
                'busy': []
            }
        }
    }
    
    calendar_service.service.events().list().execute.return_value = {'items': []}
    calendar_service.service.freebusy().query().execute.return_value = mock_freebusy
    
    # Ejecutar prueba
    start_time = datetime.now()
    duration = 60
    participants = ['test@example.com']
    
    is_available = await calendar_service.check_availability(
        start_time,
        duration,
        participants
    )
    
    # Verificar resultado
    assert is_available == True

@pytest.mark.asyncio
async def test_update_event(calendar_service):
    # Mock de datos de actualización
    event_id = 'event123'
    event_updates = {
        'summary': 'Reunión actualizada',
        'start': {
            'dateTime': '2025-02-13T16:00:00-03:00',
            'timeZone': 'America/Santiago',
        },
        'end': {
            'dateTime': '2025-02-13T17:00:00-03:00',
            'timeZone': 'America/Santiago',
        }
    }
    
    # Mock de respuesta
    mock_response = {
        'id': event_id,
        'summary': 'Reunión actualizada',
        'start': event_updates['start'],
        'end': event_updates['end'],
        'status': 'confirmed'
    }
    
    calendar_service.service.events().update().execute.return_value = mock_response
    
    # Ejecutar prueba
    result = await calendar_service.update_event(event_id, event_updates)
    
    # Verificar resultado
    assert result['id'] == event_id
    assert result['summary'] == 'Reunión actualizada'
    assert result['status'] == 'confirmed'

@pytest.mark.asyncio
async def test_delete_event(calendar_service):
    event_id = 'event123'
    
    # Mock de respuesta exitosa (None para delete)
    events_mock = MagicMock()
    delete_mock = MagicMock()
    delete_mock.execute.return_value = None
    events_mock.delete.return_value = delete_mock
    calendar_service.service.events.return_value = events_mock
    
    # Ejecutar prueba
    result = await calendar_service.delete_event(event_id)
    
    # Verificar resultado
    assert result == True
    events_mock.delete.assert_called_once_with(
        calendarId='primary',
        eventId=event_id
    )

@pytest.mark.asyncio
async def test_get_calendar_list(calendar_service):
    # Mock de respuesta
    mock_calendars = {
        'items': [
            {
                'id': 'primary',
                'summary': 'Mi Calendario',
                'description': 'Calendario principal',
                'primary': True
            },
            {
                'id': 'secondary',
                'summary': 'Calendario Secundario',
                'description': 'Otro calendario'
            }
        ]
    }
    
    calendar_service.service.calendarList().list().execute.return_value = mock_calendars
    
    # Ejecutar prueba
    calendars = await calendar_service.get_calendar_list()
    
    # Verificar resultado
    assert len(calendars) == 2
    assert calendars[0]['id'] == 'primary'
    assert calendars[0]['primary'] == True
    assert calendars[1]['id'] == 'secondary'
