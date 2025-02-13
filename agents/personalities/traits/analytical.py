from typing import Dict, Any
from ..base import BasePersonality, TraitType, ValueType

class AnalyticalPersonality(BasePersonality):
    """Personalidad analítica, ideal para investigación y análisis"""
    
    def __init__(self, name: str, role: str, description: str = None):
        super().__init__(
            name=name,
            role=role,
            description=description,
            traits={
                TraitType.OPENNESS: 0.7,        # Alta apertura a nuevas ideas
                TraitType.CONSCIENTIOUSNESS: 0.8,# Alta atención al detalle
                TraitType.EXTRAVERSION: 0.4,     # Moderadamente introvertido
                TraitType.AGREEABLENESS: 0.6,    # Moderadamente agradable
                TraitType.NEUROTICISM: 0.3       # Emocionalmente estable
            },
            values={
                ValueType.EFFICIENCY: 0.8,      # Alta valoración de eficiencia
                ValueType.CREATIVITY: 0.6,      # Moderada creatividad
                ValueType.PRECISION: 0.9,       # Alta precisión
                ValueType.COLLABORATION: 0.5     # Colaboración moderada
            }
        )
    
    def adapt_to_context(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Adapta el estilo según el contexto, con énfasis en análisis"""
        base_style = super().adapt_to_context(context)
        
        # Modificar según el tipo de análisis
        if context.get("analysis_type") == "deep":
            base_style["detail_level"] += 0.2
            base_style["formality"] += 0.1
        elif context.get("analysis_type") == "quick":
            base_style["directness"] += 0.2
            base_style["detail_level"] -= 0.1
        
        # Ajustar según la complejidad
        if context.get("complexity") == "high":
            base_style["detail_level"] += 0.1
            base_style["formality"] += 0.1
        
        # Normalizar valores
        return {k: max(0.0, min(1.0, v)) for k, v in base_style.items()}
