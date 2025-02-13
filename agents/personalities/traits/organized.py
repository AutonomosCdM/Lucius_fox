from typing import Dict, Any
from ..base import BasePersonality, TraitType, ValueType

class OrganizedPersonality(BasePersonality):
    """Personalidad organizada, ideal para gestión de tiempo y recursos"""
    
    def __init__(self, name: str, role: str, description: str = None):
        super().__init__(
            name=name,
            role=role,
            description=description,
            traits={
                TraitType.OPENNESS: 0.6,        # Adaptabilidad moderada
                TraitType.CONSCIENTIOUSNESS: 0.9,# Muy organizada
                TraitType.EXTRAVERSION: 0.6,     # Moderadamente extrovertida
                TraitType.AGREEABLENESS: 0.8,    # Alta empatía
                TraitType.NEUROTICISM: 0.2       # Muy estable emocionalmente
            },
            values={
                ValueType.EFFICIENCY: 0.9,      # Alta eficiencia
                ValueType.CREATIVITY: 0.5,      # Creatividad moderada
                ValueType.PRECISION: 0.9,       # Alta precisión
                ValueType.COLLABORATION: 0.8     # Alta colaboración
            }
        )
    
    def adapt_to_context(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Adapta el estilo según el contexto de planificación"""
        base_style = super().adapt_to_context(context)
        
        # Modificar según el tipo de evento
        if context.get("event_type") == "meeting":
            base_style["formality"] += 0.1
            base_style["detail_level"] += 0.2
        elif context.get("event_type") == "personal":
            base_style["formality"] -= 0.1
            base_style["flexibility"] += 0.2
        
        # Ajustar según la urgencia
        if context.get("urgency") == "high":
            base_style["directness"] += 0.2
            base_style["flexibility"] -= 0.1
        
        # Ajustar según el número de participantes
        if context.get("participants_count", 0) > 5:
            base_style["formality"] += 0.1
            base_style["detail_level"] += 0.1
        
        # Normalizar valores
        return {k: max(0.0, min(1.0, v)) for k, v in base_style.items()}
    
    def get_scheduling_style(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene el estilo de programación específico"""
        base_style = self.get_response_style()
        
        return {
            "approach": self._calculate_approach(context),
            "formality": base_style["formality"],
            "detail_level": base_style["detail_level"],
            "flexibility": base_style.get("flexibility", 0.5),
            "efficiency": self.values[ValueType.EFFICIENCY],
            "precision": self.values[ValueType.PRECISION]
        }
    
    def _calculate_approach(self, context: Dict[str, Any]) -> str:
        """Calcula el enfoque apropiado para la programación"""
        if context.get("urgency") == "high":
            return "efficient"
        elif context.get("event_type") == "meeting":
            return "structured"
        elif context.get("participants_count", 0) > 5:
            return "collaborative"
        else:
            return "balanced"
