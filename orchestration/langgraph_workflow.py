from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import json

from langgraph.func import entrypoint, task
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt

from services.metrics_service import MetricsService
from agents.lucius_agent import LuciusAgent
from agents.research_agent import ResearchAgent
from agents.project_agent import ProjectAgent

# Servicios compartidos
metrics_service = MetricsService()

# Agentes
lucius = LuciusAgent()

mike = ResearchAgent()
tom = ProjectAgent()

@task
async def process_with_lucius(message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Procesa un mensaje con Lucius"""
    start_time = datetime.now()
    result = await lucius.process(message, context)
    end_time = datetime.now()
    
    await metrics_service.record_task('lucius', {
        'type': 'evaluation',
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'handoff_success': True
    })
    
    return result

@task
async def process_with_mike(message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Procesa un mensaje con Mike"""
    start_time = datetime.now()
    result = await mike.process(message, context)
    end_time = datetime.now()
    
    await metrics_service.record_task('mike', {
        'type': 'research',
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'handoff_success': True
    })
    
    return result

@task
async def process_with_tom(message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Procesa un mensaje con Tom"""
    start_time = datetime.now()
    result = await tom.process(message, context)
    end_time = datetime.now()
    
    await metrics_service.record_task('tom', {
        'type': 'project',
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'handoff_success': True
    })
    
    return result

@entrypoint(checkpointer=MemorySaver())
async def research_workflow(request: Dict[str, Any]) -> Dict[str, Any]:
    """Workflow de investigación"""
    # Registrar inicio
    await metrics_service.record_interaction({
        'type': 'research',
        'complexity': _estimate_complexity(request)
    })
    
    # Evaluar con Lucius
    evaluation = await process_with_lucius(
        request.get('message', ''),
        {'workflow': 'research'}
    )
    
    # Verificar si necesitamos revisión humana
    if evaluation.get('needs_review', False):
        is_approved = interrupt({
            'evaluation': evaluation,
            'action': 'Por favor revisa la evaluación inicial'
        })
        if not is_approved:
            return {
                'status': 'rejected',
                'reason': 'Evaluación inicial rechazada'
            }
    
    # Investigar con Mike
    research = await process_with_mike(
        request.get('message', ''),
        {'evaluation': evaluation}
    )
    
    # Organizar con Tom
    organization = await process_with_tom(
        json.dumps(research),
        {'research': research}
    )
    
    # Reporte final con Lucius
    final_report = await process_with_lucius(
        json.dumps(organization),
        {'organization': organization}
    )
    
    return {
        'status': 'success',
        'evaluation': evaluation,
        'research': research,
        'organization': organization,
        'report': final_report
    }

@entrypoint(checkpointer=MemorySaver())
async def task_workflow(request: Dict[str, Any]) -> Dict[str, Any]:
    """Workflow de gestión de tareas"""
    # Registrar inicio
    await metrics_service.record_interaction({
        'type': 'task',
        'complexity': _estimate_complexity(request)
    })
    
    # Evaluar con Lucius
    evaluation = await process_with_lucius(
        request.get('message', ''),
        {'workflow': 'task'}
    )
    
    # Verificar si necesitamos revisión humana
    if evaluation.get('needs_review', False):
        is_approved = interrupt({
            'evaluation': evaluation,
            'action': 'Por favor revisa la evaluación de la tarea'
        })
        if not is_approved:
            return {
                'status': 'rejected',
                'reason': 'Evaluación de tarea rechazada'
            }
    
    # Procesar con Tom
    task_result = await process_with_tom(
        request.get('message', ''),
        {'evaluation': evaluation}
    )
    
    # Confirmación final con Lucius
    confirmation = await process_with_lucius(
        json.dumps(task_result),
        {'task_result': task_result}
    )
    
    return {
        'status': 'success',
        'evaluation': evaluation,
        'task': task_result,
        'confirmation': confirmation
    }

def _estimate_complexity(request: Dict[str, Any]) -> float:
    """Estima la complejidad de una solicitud"""
    complexity = 0.5
    message = request.get('message', '')
    
    if len(message) > 500:
        complexity += 0.2
    elif len(message) > 200:
        complexity += 0.1
        
    return min(1.0, complexity)
