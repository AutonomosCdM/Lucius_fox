from agents.project_agent import ProjectAgent
import asyncio
from datetime import datetime

async def test():
    tom = ProjectAgent()
    context = {
        'conversation_history': [],
        'timestamp': datetime.now().isoformat()
    }
    
    # 1. Crear un nuevo proyecto
    print("\n=== Creando nuevo proyecto ===")
    query = "Crear un nuevo proyecto llamado 'Desarrollo de IA' con prioridad alta"
    response = await tom.process(query, context)
    print('Intent detectado:', response['intent'])
    if response.get('projects'):
        print('Proyecto creado:', response['projects'][0])
    
    # 2. Crear algunas tareas
    print("\n=== Creando tareas ===")
    tasks = [
        "Crear una tarea urgente: Investigación de arquitecturas de LLM",
        "Crear tarea: Implementación de pipeline de entrenamiento",
        "Nueva tarea con prioridad baja: Documentación del sistema"
    ]
    
    for task_query in tasks:
        response = await tom.process(task_query, context)
        print('\nIntent para:', task_query)
        print('Intent detectado:', response['intent'])
        if response.get('tasks'):
            print('Tarea creada:', response['tasks'][0])
    
    # 3. Listar todos los proyectos
    print("\n=== Listando proyectos ===")
    response = await tom.process("Mostrar todos los proyectos", context)
    print('Proyectos encontrados:', len(response['projects']))
    for project in response['projects']:
        print(f"- {project['name']} (Prioridad: {project['priority']})")
    
    # 4. Listar todas las tareas
    print("\n=== Listando tareas ===")
    response = await tom.process("Mostrar todas las tareas", context)
    print('Tareas encontradas:', len(response['tasks']))
    for task in response['tasks']:
        print(f"- {task['name']} (Prioridad: {task['priority']}, Estado: {task['status']})")

if __name__ == "__main__":
    asyncio.run(test())
