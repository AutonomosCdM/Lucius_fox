import asyncio
from orchestration.orchestrator import Orchestrator
from agents.research_agent import ResearchAgent
from agents.project_agent import ProjectAgent
from agents.base_agent import BaseAgent

class LuciusAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Lucius",
            role="Chief of Staff",
            personality="Profesional y eficiente"
        )
    
    async def process(self, message: str, context: dict = None) -> dict:
        # Simplified processing for testing
        return {
            'status': 'success',
            'action': 'evaluate',
            'result': 'Processed by Lucius'
        }

async def test():
    # Create orchestrator
    orchestrator = Orchestrator()
    
    # Register autonomos
    orchestrator.register_autonomo('lucius', LuciusAgent())
    orchestrator.register_autonomo('mike', ResearchAgent())
    orchestrator.register_autonomo('tom', ProjectAgent())
    
    # Test research workflow
    print("\n=== Testing Research Workflow ===")
    request = {
        'workflow': 'research',
        'message': 'Investigar arquitecturas de LLM para procesamiento de texto',
        'priority': 'high'
    }
    
    result = await orchestrator.process_request(request)
    print('Research workflow result:', result)
    
    # Test task management workflow
    print("\n=== Testing Task Management Workflow ===")
    request = {
        'workflow': 'task_management',
        'message': 'Crear tarea para implementar pipeline de entrenamiento',
        'priority': 'medium'
    }
    
    result = await orchestrator.process_request(request)
    print('Task management workflow result:', result)
    
    # Get system status
    print("\n=== System Status ===")
    status = await orchestrator.get_status()
    print('Cognitive Load:', status['cognitive_load'])
    print('System Health:', status['system_health'])
    print('Autonomo Status:', status['autonomo_status'])

if __name__ == "__main__":
    asyncio.run(test())
