import json
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Si modificas estos scopes, elimina el archivo de token
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]

def get_calendar_credentials():
    """Obtiene y guarda las credenciales de acceso para Google Calendar."""
    creds = None
    token_path = 'credentials/calendar_credentials.json'
    config_path = 'credentials/calendar_config.json'
    
    # Primero movemos el archivo actual a config
    if os.path.exists(token_path) and not os.path.exists(config_path):
        print("Moviendo configuración actual a calendar_config.json...")
        with open(token_path, 'r') as f:
            config = json.load(f)
            if 'installed' in config:
                with open(config_path, 'w') as f2:
                    json.dump(config, f2, indent=2)
    
    # Intentar cargar credenciales existentes
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception as e:
            print(f"Error cargando credenciales existentes: {e}")
    
    # Si no hay credenciales válidas, iniciamos el flujo de autorización
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refrescando token expirado...")
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refrescando token: {e}")
                creds = None
        
        if not creds:
            print("Iniciando flujo de autorización...")
            try:
                # Cargar configuración de la aplicación
                flow = InstalledAppFlow.from_client_secrets_file(
                    config_path, SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print(f"Error en flujo de autorización: {e}")
                return
        
        # Guardar las credenciales para la próxima ejecución
        try:
            print("Guardando credenciales...")
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
            print("✅ Credenciales guardadas exitosamente")
        except Exception as e:
            print(f"Error guardando credenciales: {e}")
            return
    
    return creds

if __name__ == '__main__':
    print("🔐 Iniciando proceso de autenticación para Google Calendar...")
    creds = get_calendar_credentials()
    if creds:
        print("✅ Autenticación completada exitosamente")
        print(f"Token válido hasta: {creds.expiry}")
    else:
        print("❌ Error obteniendo credenciales")
