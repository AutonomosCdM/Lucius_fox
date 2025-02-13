import asyncio
import uuid
from orchestration.langgraph_workflow import research_workflow, task_workflow
from langgraph.types import Command

async def test():
    thread_id = str(uuid.uuid4())
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }
    
    # Test research workflow
    print("\n=== Testing Research Workflow ===")
    request = {
        'message': 'Necesito investigar las últimas arquitecturas de LLM para procesamiento de texto',
        'priority': 'high'
    }
    
    print("Iniciando workflow de investigación...")
    async for item in research_workflow.astream(request, config):
        if '__interrupt__' in item:
            print("Esperando aprobación humana...")
            # Simular aprobación
            async for result in research_workflow.astream(Command(resume=True), config):
                print("Resultado después de aprobación:", result)
        else:
            print("Paso completado:", item)
    
    # Test task workflow
    print("\n=== Testing Task Workflow ===")
    request = {
        'message': 'Crear una tarea para implementar el pipeline de entrenamiento',
        'priority': 'medium'
    }
    
    print("Iniciando workflow de tareas...")
    async for item in task_workflow.astream(request, config):
        if '__interrupt__' in item:
            print("Esperando aprobación humana...")
            # Simular aprobación
            async for result in task_workflow.astream(Command(resume=True), config):
                print("Resultado después de aprobación:", result)
        else:
            print("Paso completado:", item)

if __name__ == "__main__":
    asyncio.run(test())
