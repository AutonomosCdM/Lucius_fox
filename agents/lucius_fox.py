from typing import Dict, Any, List
from datetime import datetime
from .base_agent import BaseAgent
from .calendar_agent import CalendarAgent
from .email_agent import EmailAgent

class LuciusFox(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Lucius Fox",
            role="Chief of Staff",
            personality="Profesional, eficiente y proactivo"
        )
        self.agents: Dict[str, BaseAgent] = {}
        self.conversation_context: Dict[str, Any] = {}
        
        # Initialize and register agents
        self.register_agent(CalendarAgent())
        self.register_agent(EmailAgent())

    def register_agent(self, agent: BaseAgent):
        """Register a new agent under Lucius's supervision"""
        self.agents[agent.name] = agent

    def get_conversation_context(self, thread_id: str) -> Dict[str, Any]:
        """Get the full context of a conversation thread"""
        return self.conversation_context.get(thread_id, {'history': [], 'current_task': None, 'active_agent': None})

    def update_conversation_context(self, thread_id: str, message: str, user: str, 
    agent_response: str = None, task: str = None, active_agent: str = None):
        """Update the conversation context with new information"""
        if thread_id not in self.conversation_context:
            self.conversation_context[thread_id] = {'history': [], 'current_task': None, 'active_agent': None}

        context = self.conversation_context[thread_id]
        context['history'].append({
            'timestamp': datetime.now().isoformat(),
            'user': user,
            'message': message,
            'response': agent_response
        })

        if task:
            context['current_task'] = task
        if active_agent:
            context['active_agent'] = active_agent

    async def delegate_to_agent(self, agent_name: str, message: str, context: Dict[str, Any]) -> str:
        """Delegate a task to a specific agent"""
        agent = self.agents.get(agent_name)
        if not agent:
            return self.format_response(f"Lo siento, no pude encontrar al agente {agent_name}.")
        
        thread_id = context.get('thread_ts', context.get('ts'))
        conv_context = self.get_conversation_context(thread_id)
        
        # Include conversation history in the context
        context['conversation_history'] = conv_context['history']
        
        response = await agent.process(message, context)
        return response

    def should_continue_with_active_agent(self, message: str, thread_context: Dict[str, Any]) -> bool:
        """Determine if we should continue with the currently active agent"""
        if not thread_context.get('active_agent'):
            return False

        # If the last interaction was recent (within 5 minutes)
        if thread_context['history']:
            last_interaction = datetime.fromisoformat(thread_context['history'][-1]['timestamp'])
            time_diff = (datetime.now() - last_interaction).total_seconds() / 60
            if time_diff <= 5:
                return True

        return False

    async def process(self, message: str, context: Dict[str, Any]) -> str:
        """Process incoming messages and coordinate with other agents"""
        thread_id = context.get('thread_ts', context.get('ts'))
        thread_context = self.get_conversation_context(thread_id)
        user = context.get('user')

        # Check if we should continue with the active agent
        if self.should_continue_with_active_agent(message, thread_context):
            active_agent = thread_context['active_agent']
            response = await self.delegate_to_agent(active_agent, message, context)
            self.update_conversation_context(thread_id, message, user, response)
            return response

        # Initial greeting
        if any(word in message.lower() for word in ["hola", "hello", "hi"]):
            response = self.format_response(
                "¡Hola! Soy Lucius Fox, tu Chief of Staff. "  
                "Coordino con un equipo de asistentes especializados para ayudarte. "  
                "¿En qué puedo ayudarte hoy?"
            )
            self.update_conversation_context(thread_id, message, user, response)
            return response

        # Calendar-related requests
        if any(keyword in message.lower() for keyword in [
            'reunión', 'meeting', 'calendario', 'calendar', 'agenda', 'disponibilidad',
            'availability', 'schedule', 'programar'
        ]):
            initial_response = self.format_response(
                "Entiendo que necesitas ayuda con el calendario. "  
                "Permíteme consultar con Sarah, nuestra especialista en gestión de agenda."
            )
            
            # Get Sarah's response
            calendar_response = await self.delegate_to_agent("Sarah", message, context)
            
            # Update context with the calendar task and Sarah as active agent
            self.update_conversation_context(
                thread_id, message, user,
                f"{initial_response}\n{calendar_response}",
                task="calendar",
                active_agent="Sarah"
            )
            
            # Return both responses to create a conversation thread
            return f"{initial_response}\n{calendar_response}"

        # Email-related requests
        if any(keyword in message.lower() for keyword in [
            'email', 'correo', 'mail', 'gmail', 'mensaje', 'bandeja',
            'enviar', 'escribir', 'redactar'
        ]):
            initial_response = self.format_response(
                "Entiendo que necesitas ayuda con emails. "  
                "Permíteme consultar con Karla, nuestra especialista en comunicaciones."
            )
            
            # Get Karla's response
            email_response = await self.delegate_to_agent("Karla", message, context)
            
            # Update context with the email task and Karla as active agent
            self.update_conversation_context(
                thread_id, message, user,
                f"{initial_response}\n{email_response}",
                task="email",
                active_agent="Karla"
            )
            
            # Return both responses to create a conversation thread
            return f"{initial_response}\n{email_response}"

        # Default response
        response = self.format_response(
            "Entiendo tu solicitud. Déjame coordinar con el equipo para ayudarte. "  
            "¿Podrías darme más detalles sobre lo que necesitas?"
        )
        self.update_conversation_context(thread_id, message, user, response)
        return response
