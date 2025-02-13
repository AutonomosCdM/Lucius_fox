from typing import Dict, List, Any, TypedDict, Annotated, Callable
from langgraph.graph import StateGraph, END
from langgraph.graph.nodes import Node
import asyncio
from datetime import datetime

from services.metrics_service import MetricsService
from agents.base_agent import BaseAgent

class WorkflowState(TypedDict):
    """Estado del workflow"""
    messages: List[Dict[str, Any]]  # Historial de mensajes
    current_agent: str              # Agente actual
    workflow_type: str             # Tipo de workflow (research, task, etc)
    context: Dict[str, Any]        # Contexto acumulado
    metrics: Dict[str, Any]        # Métricas del workflow
    start_time: str                # Tiempo de inicio
    status: str                    # Estado actual (running, completed, error)

class AutonomoNode(Node):
    """Nodo que representa un autónomo en el grafo"""
    
    def __init__(self, agent: BaseAgent, metrics_service: MetricsService):
        self.agent = agent
        self.metrics_service = metrics_service
        
    async def process(self, state: WorkflowState) -> WorkflowState:
        """Procesa el estado actual y retorna el nuevo estado"""
        try:
            # Registrar inicio
            start_time = datetime.now()
            
            # Extraer último mensaje
            last_message = state["messages"][-1] if state["messages"] else {"content": ""}
            
            # Procesar con el agente
            result = await self.agent.process(
                last_message["content"],
                state["context"]
            )
            
            # Registrar finalización
            end_time = datetime.now()
            
            # Actualizar métricas
            await self.metrics_service.record_task(
                self.agent.name.lower(),
                {
                    "type": state["workflow_type"],
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "handoff_success": True
                }
            )
            
            # Agregar resultado al historial
            state["messages"].append({
                "agent": self.agent.name,
                "content": str(result),
                "timestamp": datetime.now().isoformat()
            })
            
            # Actualizar contexto
            if "results" not in state["context"]:
                state["context"]["results"] = {}
            state["context"]["results"][self.agent.name] = result
            
            return state
            
        except Exception as e:
            # Registrar error
            await self.metrics_service.record_error({
                "type": "agent_error",
                "agent": self.agent.name,
                "workflow": state["workflow_type"],
                "error": str(e)
            })
            
            # Actualizar estado
            state["status"] = "error"
            state["messages"].append({
                "agent": self.agent.name,
                "content": f"Error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
            
            return state

class LangGraphOrchestrator:
    """Orquestador basado en LangGraph"""
    
    def __init__(self):
        self.metrics_service = MetricsService()
        self.graphs: Dict[str, StateGraph] = {}
        self.setup_graphs()
        
    def setup_graphs(self):
        """Configura los grafos para diferentes workflows"""
        # Workflow de investigación
        research_graph = StateGraph(WorkflowState)
        
        # Agregar nodos
        research_graph.add_node("lucius", self._create_node("lucius"))
        research_graph.add_node("mike", self._create_node("mike"))
        research_graph.add_node("tom", self._create_node("tom"))
        
        # Agregar edges
        research_graph.add_edge("lucius", "mike", self._should_research)
        research_graph.add_edge("mike", "tom", self._should_organize)
        research_graph.add_edge("tom", "lucius", self._should_report)
        research_graph.add_edge("lucius", END, self._is_complete)
        
        self.graphs["research"] = research_graph
        
        # Workflow de tareas
        task_graph = StateGraph(WorkflowState)
        
        # Agregar nodos
        task_graph.add_node("lucius", self._create_node("lucius"))
        task_graph.add_node("tom", self._create_node("tom"))
        
        # Agregar edges
        task_graph.add_edge("lucius", "tom", self._should_process_task)
        task_graph.add_edge("tom", "lucius", self._should_confirm)
        task_graph.add_edge("lucius", END, self._is_complete)
        
        self.graphs["task"] = task_graph
    
    def _create_node(self, agent_name: str) -> AutonomoNode:
        """Crea un nodo para un agente"""
        from agents.research_agent import ResearchAgent
        from agents.project_agent import ProjectAgent
        
        agents = {
            "lucius": BaseAgent(
                name="Lucius",
                role="Chief of Staff",
                personality="Profesional y eficiente"
            ),
            "mike": ResearchAgent(),
            "tom": ProjectAgent()
        }
        
        return AutonomoNode(
            agent=agents[agent_name],
            metrics_service=self.metrics_service
        )
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa una solicitud a través del workflow apropiado"""
        workflow_type = request.get("workflow", "task")
        
        if workflow_type not in self.graphs:
            return {
                "status": "error",
                "message": f"Workflow no encontrado: {workflow_type}"
            }
            
        # Crear estado inicial
        initial_state: WorkflowState = {
            "messages": [{
                "agent": "human",
                "content": request.get("message", ""),
                "timestamp": datetime.now().isoformat()
            }],
            "current_agent": "lucius",
            "workflow_type": workflow_type,
            "context": request,
            "metrics": {},
            "start_time": datetime.now().isoformat(),
            "status": "running"
        }
        
        # Registrar interacción
        await self.metrics_service.record_interaction({
            "type": workflow_type,
            "complexity": self._estimate_complexity(request)
        })
        
        # Ejecutar workflow
        try:
            graph = self.graphs[workflow_type]
            final_state = await graph.arun(initial_state)
            
            return {
                "status": "success",
                "result": final_state["context"]["results"],
                "messages": final_state["messages"]
            }
            
        except Exception as e:
            await self.metrics_service.record_error({
                "type": "workflow_error",
                "workflow": workflow_type,
                "error": str(e)
            })
            
            return {
                "status": "error",
                "message": f"Error en workflow: {str(e)}"
            }
    
    def _estimate_complexity(self, request: Dict[str, Any]) -> float:
        """Estima la complejidad de una solicitud"""
        complexity = 0.5
        message = request.get("message", "")
        
        if len(message) > 500:
            complexity += 0.2
        elif len(message) > 200:
            complexity += 0.1
            
        return min(1.0, complexity)
    
    # Condiciones de transición
    def _should_research(self, state: WorkflowState) -> bool:
        """Determina si se debe pasar a investigación"""
        return "investigar" in state["messages"][-1]["content"].lower()
    
    def _should_organize(self, state: WorkflowState) -> bool:
        """Determina si se debe organizar resultados"""
        return True  # Por ahora, siempre organizamos
    
    def _should_report(self, state: WorkflowState) -> bool:
        """Determina si se debe generar reporte"""
        return True  # Por ahora, siempre reportamos
    
    def _should_process_task(self, state: WorkflowState) -> bool:
        """Determina si se debe procesar una tarea"""
        return True  # Por ahora, siempre procesamos
    
    def _should_confirm(self, state: WorkflowState) -> bool:
        """Determina si se debe confirmar una tarea"""
        return True  # Por ahora, siempre confirmamos
    
    def _is_complete(self, state: WorkflowState) -> bool:
        """Determina si el workflow está completo"""
        return (
            state["status"] == "error" or
            len(state["messages"]) >= 4  # Al menos human -> lucius -> agente -> lucius
        )
