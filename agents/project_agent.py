from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
from services.project_service import ProjectService
from services.task_service import TaskService
from services.document_service import DocumentService

class ProjectAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Tom",
            role="Project Manager",
            personality="Organizado, metódico y orientado a objetivos"
        )
        self.current_project: Optional[Dict[str, Any]] = None
        self.project_history: List[Dict[str, Any]] = []
        
        # Initialize services
        self.project_service = ProjectService()
        self.task_service = TaskService()
        self.document_service = DocumentService()

    def _clean_name(self, name: str) -> str:
        """Clean up a name by removing unnecessary words and characters"""
        if not name:
            return ''

        # Remove common prefixes
        prefixes = ['llamado', 'llamada', 'named', 'titled', 'titulado', 'titulada']
        name_lower = name.lower()
        for prefix in prefixes:
            if name_lower.startswith(prefix):
                name = name[len(prefix):].strip()

        # Remove quotes and extra spaces
        name = name.strip('"\'').strip()

        # Remove priority and status indicators
        indicators = ['urgente:', 'urgent:', 'alta:', 'high:', 'baja:', 'low:', 'media:', 'medium:']
        for indicator in indicators:
            if name_lower.startswith(indicator):
                name = name[len(indicator):].strip()

        return name

    def _extract_name(self, message: str, prefix_words: List[str]) -> Optional[str]:
        """Extract name from message after any of the prefix words"""
        msg = message.lower()
        
        # Try to find name after any prefix
        for prefix in prefix_words:
            if prefix in msg:
                # Find the actual prefix in original message to preserve case
                start_idx = message.lower().index(prefix) + len(prefix)
                # Extract everything after prefix
                remaining = message[start_idx:].strip(': ')
                if remaining:
                    # Split by common stop words
                    stop_words = ['con', 'with', 'para', 'for', 'y', 'and',
                                'que', 'that', 'prioridad', 'priority']
                    
                    name = remaining
                    for word in stop_words:
                        if f' {word} ' in name.lower():
                            name = name.lower().split(f' {word} ')[0]
                    
                    # Clean up the name
                    name = self._clean_name(name)
                    if name:
                        return name
        
        # If no name found after prefixes, try to extract from beginning
        words = message.split()
        for i, word in enumerate(words):
            if word.lower() in ['tarea:', 'task:', 'proyecto:', 'project:']:
                name = ' '.join(words[i+1:]).split('.')[0]
                name = self._clean_name(name)
                if name:
                    return name
        
        return None

    def extract_project_intent(self, message: str) -> Dict[str, Any]:
        """Extract project management related intent from message"""
        msg = message.lower()
        intent = {
            'action': 'unknown',
            'project': None,
            'task': None,
            'priority': 'medium',
            'deadline': None,
            'assignee': None
        }
        
        # Determine primary action and extract names
        if any(word in msg for word in ["crear", "nuevo", "iniciar", "create", "new", "start"]):
            intent['action'] = "create"
            if "proyecto" in msg or "project" in msg:
                intent['project'] = self._extract_name(
                    message,
                    ["proyecto", "project", "llamado", "named", "titulado", "titled"]
                )
            else:
                intent['task'] = self._extract_name(
                    message,
                    ["tarea", "task", "llamada", "named", "titulada", "titled"]
                )
        elif any(word in msg for word in ["actualizar", "modificar", "update", "modify"]):
            intent['action'] = "update"
        elif any(word in msg for word in ["eliminar", "borrar", "delete", "remove"]):
            intent['action'] = "delete"
        elif any(word in msg for word in ["listar", "mostrar", "ver", "list", "show", "view"]):
            intent['action'] = "list"
        elif any(word in msg for word in ["asignar", "assign"]):
            intent['action'] = "assign"
            
        # Extract priority if present
        if any(word in msg for word in ["urgente", "crítico", "urgent", "critical", "alta", "high", "prioridad alta", "high priority"]):
            intent['priority'] = "high"
        elif any(word in msg for word in ["baja", "low", "prioridad baja", "low priority"]):
            intent['priority'] = "low"
            
        return intent

    async def process(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process project management related requests"""
        if context is None:
            context = {'conversation_history': []}
            
        intent = self.extract_project_intent(message)

        # Initialize response
        response = {
            'intent': intent,
            'action_taken': None,
            'projects': [],
            'tasks': [],
            'error': None
        }

        try:
            if intent['action'] == "create":
                # Handle project/task creation
                if "proyecto" in message.lower() or "project" in message.lower():
                    name = intent['project'] or 'Nuevo Proyecto'
                    # Check for duplicates
                    existing = await self.project_service.list_projects({'name': name})
                    if existing:
                        response['error'] = f"Ya existe un proyecto llamado '{name}'"
                    else:
                        project = await self.project_service.create_project({
                            'name': name,
                            'description': message,
                            'status': 'active',
                            'priority': intent['priority']
                        })
                        response['projects'].append(project)
                        response['action_taken'] = "project_created"
                else:
                    name = intent['task'] or 'Nueva Tarea'
                    # Check for duplicates
                    existing = await self.task_service.list_tasks({'name': name})
                    if existing:
                        response['error'] = f"Ya existe una tarea llamada '{name}'"
                    else:
                        task = await self.task_service.create_task({
                            'name': name,
                            'description': message,
                            'status': 'pending',
                            'priority': intent['priority']
                        })
                        response['tasks'].append(task)
                        response['action_taken'] = "task_created"

            elif intent['action'] == "list":
                # Handle listing projects/tasks
                if "proyecto" in message.lower() or "project" in message.lower():
                    projects = await self.project_service.list_projects()
                    response['projects'] = projects
                    response['action_taken'] = "projects_listed"
                else:
                    tasks = await self.task_service.list_tasks()
                    response['tasks'] = tasks
                    response['action_taken'] = "tasks_listed"

            elif intent['action'] == "update":
                # TODO: Implement project/task updates
                pass

            elif intent['action'] == "delete":
                # TODO: Implement project/task deletion
                pass

            elif intent['action'] == "assign":
                # TODO: Implement task assignment
                pass

        except Exception as e:
            response['error'] = str(e)

        # Update project history
        self.project_history.append({
            'timestamp': context.get('timestamp'),
            'request': message,
            'response': response
        })

        return response
