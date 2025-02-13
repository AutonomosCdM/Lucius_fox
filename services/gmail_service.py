import os
import pickle
from typing import List, Dict, Any, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
import base64

class GmailService:
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify'
    ]

    def __init__(self):
        self.creds = None
        self.service = None
        self.token_path = 'credentials/token.pickle'
        self.credentials_path = 'credentials/gmail_credentials.json'

    def authenticate(self) -> None:
        """Authenticate with Gmail API"""
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                self.creds = flow.run_local_server(port=0)

            with open(self.token_path, 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('gmail', 'v1', credentials=self.creds)

    async def list_messages(self, query: str = None, max_results: int = 10) -> List[Dict[str, Any]]:
        """List messages matching the specified query"""
        try:
            if not self.service:
                self.authenticate()

            messages = []
            request = self.service.users().messages().list(
                userId='me', q=query, maxResults=max_results
            )
            response = request.execute()
            
            if 'messages' in response:
                for msg in response['messages']:
                    message = self.service.users().messages().get(
                        userId='me', id=msg['id'], format='full'
                    ).execute()
                    
                    headers = message['payload']['headers']
                    subject = next(
                        (h['value'] for h in headers if h['name'].lower() == 'subject'),
                        'No Subject'
                    )
                    sender = next(
                        (h['value'] for h in headers if h['name'].lower() == 'from'),
                        'Unknown'
                    )
                    
                    messages.append({
                        'id': msg['id'],
                        'subject': subject,
                        'sender': sender,
                        'snippet': message.get('snippet', ''),
                        'date': next(
                            (h['value'] for h in headers if h['name'].lower() == 'date'),
                            'Unknown'
                        )
                    })
            
            return messages

        except HttpError as error:
            print(f'An error occurred: {error}')
            return []

    async def send_message(self, to: str, subject: str, body: str) -> bool:
        """Send an email message"""
        try:
            if not self.service:
                self.authenticate()

            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()

            return True

        except HttpError as error:
            print(f'An error occurred: {error}')
            return False

    async def search_messages(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search for messages using Gmail's search syntax"""
        return await self.list_messages(query=query, max_results=max_results)

    async def get_unread_messages(self, max_results: int = 5) -> List[Dict[str, Any]]:
        """Get unread messages"""
        return await self.list_messages(query='is:unread', max_results=max_results)

    async def mark_as_read(self, message_id: str) -> bool:
        """Mark a message as read"""
        try:
            if not self.service:
                self.authenticate()

            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True

        except HttpError as error:
            print(f'An error occurred: {error}')
            return False
