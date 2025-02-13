from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
from services.metrics_service import MetricsService
from agents.base_agent import BaseAgent

class Orchestrator:
    def __init__(self):
        self.metrics_service = MetricsService()
        self.autonomos: Dict[str, BaseAgent] = {}
        self.workflows: Dict[str, Dict[str, Any]] = {
            'research': {
                'steps': ['lucius', 'mike', 'tom', 'lucius'],
                'transitions': {
                    'lucius': ['evaluate_request', 'prepare_report'],
                    'mike': ['conduct_research'],
                    'tom': ['organize_results']
                }
            },
            'task_management': {
                'steps': ['lucius', 'tom', 'lucius'],
                'transitions': {
                    'lucius': ['evaluate_task', 'confirm_assignment'],
                    'tom': ['process_task']
                }
            }
        }
        
    def register_autonomo(self, name: str, autonomo: BaseAgent) -> None:
        """Register an autonomo with the orchestrator"""
        self.autonomos[name] = autonomo

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a user request through the appropriate workflow"""
        # Record interaction
        await self.metrics_service.record_interaction({
            'type': 'request',
            'complexity': self._estimate_complexity(request),
            'workflow': request.get('workflow', 'unknown')
        })
        
        # Check if we should throttle
        if await self.metrics_service.should_throttle():
            return {
                'status': 'throttled',
                'message': 'Sistema temporalmente sobrecargado, por favor espere.'
            }
        
        # Get workflow
        workflow = self.workflows.get(request.get('workflow'))
        if not workflow:
            return {
                'status': 'error',
                'message': 'Workflow no encontrado'
            }
        
        # Execute workflow
        try:
            result = await self._execute_workflow(workflow, request)
            return {
                'status': 'success',
                'result': result
            }
        except Exception as e:
            await self.metrics_service.record_error({
                'type': 'workflow_error',
                'workflow': request.get('workflow'),
                'error': str(e)
            })
            return {
                'status': 'error',
                'message': f'Error en workflow: {str(e)}'
            }

    async def _execute_workflow(
        self, 
        workflow: Dict[str, Any], 
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a workflow step by step"""
        context = {
            'request': request,
            'start_time': datetime.now().isoformat(),
            'results': {}
        }
        
        for step in workflow['steps']:
            # Get autonomo
            autonomo = self.autonomos.get(step)
            if not autonomo:
                raise ValueError(f'Autonomo no encontrado: {step}')
            
            # Get transition
            transition = workflow['transitions'][step][
                len(context['results'].get(step, []))
            ]
            
            # Execute step
            try:
                start_time = datetime.now()
                # Extract message for autonomo
                message = request.get('message', '')
                # Add context to message if needed
                if context['results']:
                    message += '\nContexto previo: ' + str(context['results'])
                result = await autonomo.process(message, context)
                end_time = datetime.now()
                
                # Record task
                await self.metrics_service.record_task(step, {
                    'type': transition,
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'handoff_success': True
                })
                
                # Store result
                if step not in context['results']:
                    context['results'][step] = []
                context['results'][step].append(result)
                
            except Exception as e:
                await self.metrics_service.record_task(step, {
                    'type': transition,
                    'error': str(e),
                    'handoff_success': False
                })
                raise
        
        return context['results']

    def _estimate_complexity(self, request: Dict[str, Any]) -> float:
        """Estimate request complexity (0-1)"""
        # Simple heuristic based on:
        # 1. Length of request
        # 2. Number of steps in workflow
        # 3. Previous similar requests
        
        complexity = 0.5  # Base complexity
        
        # Adjust for request length
        message = request.get('message', '')
        if len(message) > 500:
            complexity += 0.2
        elif len(message) > 200:
            complexity += 0.1
            
        # Adjust for workflow
        workflow = self.workflows.get(request.get('workflow', ''))
        if workflow:
            complexity += len(workflow['steps']) * 0.05
            
        return min(1.0, complexity)

    async def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return await self.metrics_service.get_system_status()
