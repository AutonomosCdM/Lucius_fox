from typing import Dict, Any, List, Optional
from datetime import datetime
import re
import asyncio
import logging
import json
import os
from slack_sdk import WebClient as SlackClient
from slack_sdk.errors import SlackApiError

from .base_agent import BaseAgent
from services.gmail_service import GmailService

class EmailAgent(BaseAgent):
    def __init__(self, slack_config_path: Optional[str] = 'credentials/slack_config.json'):
        super().__init__(
            name="Karla",
            role="Email Manager",
            personality="Comunicativa, detallista y eficiente"
        )
        self.current_task: Optional[str] = None
        self.email_context: Dict[str, Any] = {}
        self.gmail_service = GmailService()
        self.last_emails: List[Dict[str, Any]] = []
        
        # Slack integration
        self._slack_client = None
        self._slack_config = self._load_slack_config(slack_config_path)
        
        # Initialize Slack client if configuration is enabled
        if self._slack_config and self._slack_config.get('enabled', False):
            try:
                self._slack_client = SlackClient(token=self._slack_config['bot_oauth_token'])
                logging.info("Slack client initialized successfully")
            except Exception as e:
                logging.error(f"Failed to initialize Slack client: {e}")
        
        # Advanced NLP setup
        self._sensitive_keywords = [
            'confidencial', 'urgente', 'crítico', 'importante', 
            'legal', 'financiero', 'despido', 'contrato'
        ]

    def _load_slack_config(self, config_path: str) -> Optional[Dict[str, Any]]:
        """
        Load Slack configuration from JSON file
        """
        try:
            with open(config_path, 'r') as config_file:
                return json.load(config_file)
        except FileNotFoundError:
            logging.error(f"Slack configuration file not found: {config_path}")
            return None
        except json.JSONDecodeError:
            logging.error(f"Invalid JSON in Slack configuration file: {config_path}")
            return None

    def _is_sensitive_email(self, email: Dict[str, Any]) -> bool:
        """
        Determine if an email is sensitive and requires human confirmation
        """
        # Check subject and body for sensitive keywords
        subject = email.get('subject', '').lower()
        body = email.get('body', '').lower()
        
        # Sentiment analysis
        try:
            sentiment = self._sentiment_analyzer(subject + " " + body)[0]
            is_negative = sentiment['label'] == 'NEGATIVE' and sentiment['score'] > 0.7
        except Exception:
            is_negative = False
        
        # Keyword and sentiment-based sensitivity check
        return (
            any(keyword in subject or keyword in body for keyword in self._sensitive_keywords) or
            is_negative
        )

    async def _request_human_confirmation(self, email: Dict[str, Any]) -> bool:
        """
        Request human confirmation for sensitive emails
        """
        confirmation_message = (
            f"⚠️ Sensitive Email Detected\n"
            f"From: {email.get('sender', 'Unknown')}\n"
            f"Subject: {email.get('subject', 'No Subject')}\n"
            f"Do you want to proceed? (yes/no)"
        )
        
        # If Slack is configured, send confirmation request
        if self._slack_client:
            try:
                response = self._slack_client.chat_postMessage(
                    channel='#email-confirmations',  # Configure this channel
                    text=confirmation_message
                )
                # TODO: Implement a way to capture user response
                return True  # Placeholder
            except SlackApiError as e:
                logging.error(f"Slack confirmation failed: {e}")
                return False
        
        return False  # Fallback if no confirmation method available

    def extract_email_intent(self, message: str) -> str:
        """Extract the main intent from an email-related message"""
        msg = message.lower()
        
        if any(word in msg for word in ["revisar", "check", "leer", "ver", "nuevos"]):
            return "check_emails"
        elif any(word in msg for word in ["enviar", "mandar", "escribir", "redactar"]):
            return "send_email"
        elif any(word in msg for word in ["buscar", "encontrar", "search"]):
            return "search_emails"
        elif any(word in msg for word in ["archivar", "organizar", "mover"]):
            return "organize_emails"
        return "general_inquiry"

    def get_task_context(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract relevant context from conversation history"""
        context = {
            'recipients': [],
            'subject': None,
            'urgency': 'normal',
            'attachments': [],
            'mentioned_dates': [],
            'search_terms': []
        }
        
        # Analyze recent history
        for entry in history[-3:]:  # Look at last 3 messages
            msg = entry.get('message', '').lower()
            
            # Extract potential email addresses
            if '@' in msg:
                context['recipients'].extend(
                    word for word in msg.split() if '@' in word
                )
            
            # Check urgency
            if any(word in msg for word in ['urgente', 'urgent', 'asap', 'importante']):
                context['urgency'] = 'high'
            
            # Look for potential subject indicators
            if 'asunto' in msg or 'subject' in msg or 'sobre' in msg:
                # Extract the phrase after these words
                pass  # TODO: Implement subject extraction
                
        return context

    async def process(self, message: str, context: Dict[str, Any]) -> str:
        """Process email-related requests"""
        msg = message.lower()
        history = context.get('conversation_history', [])
        intent = self.extract_email_intent(msg)
        task_context = self.get_task_context(history)

        # Handle different intents
        if intent == "check_emails":
            try:
                # Get unread messages
                unread = await self.gmail_service.get_unread_messages(max_results=5)
                if not unread:
                    return self.format_response(
                        "He revisado tu bandeja de entrada y no tienes emails sin leer. "
                        "¿Quieres que busque algo específico?"
                    )
                
                # Store emails in context
                self.last_emails = unread
                
                # Format the response
                response = "He encontrado los siguientes emails sin leer:\n\n"
                for email in unread:
                    # Check if email is sensitive
                    if self._is_sensitive_email(email):
                        # Request human confirmation for sensitive emails
                        await self._request_human_confirmation(email)
                    
                    response += f"- De: {email['sender']}\n"
                    response += f"  Asunto: {email['subject']}\n"
                    response += f"  Vista previa: {email['snippet']}\n\n"
                
                response += "¿Quieres que marque alguno como leído o que te muestre más detalles?"
                return self.format_response(response)

            except Exception as e:
                return self.format_response(
                    "Lo siento, tuve un problema al acceder a tus emails. "
                    "Por favor, verifica que tengo los permisos necesarios."
                )

        elif intent == "send_email":
            if not task_context['recipients']:
                return self.format_response(
                    "Por supuesto, te ayudo a enviar el email. "
                    "¿A quién debería enviarlo? Necesito el correo del destinatario."
                )

            # If we have recipients but no subject
            if not task_context.get('subject'):
                recipients = ', '.join(task_context['recipients'])
                return self.format_response(
                    f"Bien, enviaré un email a {recipients}. "
                    "¿Cuál es el asunto del correo?"
                )

            # If we have both recipient and subject, ask for content
            return self.format_response(
                "Perfecto, ya tengo el destinatario y el asunto. "
                "¿Qué contenido debería incluir en el email?"
            )

        elif intent == "search_emails":
            # Extract search terms from the message
            search_terms = ' '.join(task_context['search_terms'])
            if not search_terms:
                return self.format_response(
                    "Puedo ayudarte a buscar emails. "
                    "¿Qué criterios de búsqueda quieres que use? "
                    "Puedo buscar por remitente, asunto, fecha o contenido."
                )

            try:
                results = await self.gmail_service.search_messages(search_terms)
                if not results:
                    return self.format_response(
                        f"No encontré emails que coincidan con '{search_terms}'. "
                        "¿Quieres que pruebe con otros términos?"
                    )

                response = f"He encontrado los siguientes emails relacionados con '{search_terms}':\n\n"
                for email in results:
                    # Check if email is sensitive
                    if self._is_sensitive_email(email):
                        # Request human confirmation for sensitive emails
                        await self._request_human_confirmation(email)
                    
                    response += f"- De: {email['sender']}\n"
                    response += f"  Asunto: {email['subject']}\n"
                    response += f"  Fecha: {email['date']}\n\n"

                return self.format_response(response)

            except Exception as e:
                return self.format_response(
                    "Lo siento, tuve un problema al buscar los emails. "
                    "Por favor, verifica que tengo los permisos necesarios."
                )

        # Handle marking emails as read
        if "marcar" in msg and "leidos" in msg:
            if not self.last_emails:
                return self.format_response(
                    "No tengo emails en contexto para marcar como leídos. "
                    "¿Podrías mostrarme primero los emails que quieres marcar?"
                )
            
            try:
                for email in self.last_emails:
                    await self.gmail_service.mark_as_read(email['id'])
                
                self.last_emails = []  # Clear context after marking as read
                return self.format_response(
                    "He marcado todos los emails como leídos. "
                    "¿Necesitas algo más?"
                )
            except Exception as e:
                return self.format_response(
                    "Lo siento, tuve un problema al marcar los emails como leídos. "
                    "Por favor, verifica que tengo los permisos necesarios."
                )

        # Default response
        return self.format_response(
            "Estoy aquí para ayudarte con la gestión de emails. "
            "Puedo revisar tu bandeja de entrada, enviar correos, "
            "buscar mensajes específicos y ayudarte a mantener todo organizado. "
            "¿Qué necesitas específicamente?"
        )
