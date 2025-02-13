import asyncio
from orchestration.langgraph_orchestrator import LangGraphOrchestrator

async def test():
    # Crear orquestador
    orchestrator = LangGraphOrchestrator()
    
    # Test research workflow
    print("\n=== Testing Research Workflow ===")
    request = {
        'workflow': 'research',
        'message': 'Necesito investigar las últimas arquitecturas de LLM para procesamiento de texto',
        'priority': 'high'
    }
    
    result = await orchestrator.process_request(request)
    print('Research workflow result:')
    print('Status:', result['status'])
    print('\nMessages:')
    for msg in result.get('messages', []):
        print(f"{msg['agent']} ({msg['timestamp']}): {msg['content'][:100]}...")
    
    # Test task workflow
    print("\n=== Testing Task Workflow ===")
    request = {
        'workflow': 'task',
        'message': 'Crear una tarea para implementar el pipeline de entrenamiento',
        'priority': 'medium'
    }
    
    result = await orchestrator.process_request(request)
    print('Task workflow result:')
    print('Status:', result['status'])
    print('\nMessages:')
    for msg in result.get('messages', []):
        print(f"{msg['agent']} ({msg['timestamp']}): {msg['content'][:100]}...")
    
    # Get system status
    print("\n=== System Status ===")
    status = await orchestrator.metrics_service.get_system_status()
    print('Cognitive Load:', status['cognitive_load'])
    print('System Health:', status['system_health'])
    print('Autonomo Status:', status['autonomo_status'])

if __name__ == "__main__":
    asyncio.run(test())
