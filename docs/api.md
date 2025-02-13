# API Documentation

## Overview

### Authentication
```python
# Example authentication
from lucius_fox import authenticate

client = authenticate(api_key='your_api_key')
```

### Agent Endpoints
1. **Sarah (Calendar Agent)**
```python
# Schedule a meeting
response = client.sarah.schedule_meeting(
    title='Project Review',
    participants=['user1@example.com', 'user2@example.com'],
    duration=60
)
```

2. **Tom (Project Manager Agent)**
```python
# Get project status
project_status = client.tom.get_project_status('Quantum')
```

3. **Mike (Data Agent)**
```python
# Get project metrics
metrics = client.mike.get_project_metrics('Quantum')
```

4. **Emma (Email Agent)**
```python
# Send email update
client.emma.send_email(
    recipients=['team@example.com'],
    subject='Project Update',
    body='Latest project status...'
)
```

## Error Handling
```python
try:
    response = client.sarah.schedule_meeting(...)
except APIError as e:
    print(f'Error: {e.message}')
    print(f'Status Code: {e.status_code}')
```

## Rate Limiting
- Max 100 requests/minute
- Exponential backoff on failures

## Versioning
- Current version: v1
- Use header: `Accept: application/vnd.luciusfox.v1+json`
