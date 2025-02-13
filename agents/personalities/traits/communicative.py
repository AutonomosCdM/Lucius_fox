from typing import Dict, Any
from ..base import BasePersonality, TraitType, ValueType

class CommunicativePersonality(BasePersonality):
    """Personalidad comunicativa, ideal para interacción y gestión de comunicaciones"""
    
    def __init__(self, name: str, role: str, description: str = None):
        super().__init__(
            name=name,
            role=role,
            description=description,
            traits={
                TraitType.OPENNESS: 0.7,        # Alta adaptabilidad
                TraitType.CONSCIENTIOUSNESS: 0.8,# Alta atención al detalle
                TraitType.EXTRAVERSION: 0.8,     # Muy comunicativa
                TraitType.AGREEABLENESS: 0.9,    # Muy empática
                TraitType.NEUROTICISM: 0.2       # Muy estable emocionalmente
            },
            values={
                ValueType.EFFICIENCY: 0.8,      # Alta eficiencia
                ValueType.CREATIVITY: 0.6,      # Creatividad moderada
                ValueType.PRECISION: 0.9,       # Alta precisión
                ValueType.COLLABORATION: 0.8     # Alta colaboración
            }
        )
    
    def adapt_to_context(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Adapta el estilo según el contexto de comunicación"""
        base_style = super().adapt_to_context(context)
        
        # Modificar según el tipo de comunicación
        if context.get("communication_type") == "formal":
            base_style["formality"] += 0.2
            base_style["detail_level"] += 0.1
        elif context.get("communication_type") == "casual":
            base_style["formality"] -= 0.2
            base_style["enthusiasm"] += 0.1
        
        # Ajustar según la urgencia
        if context.get("urgency") == "high":
            base_style["directness"] += 0.2
            base_style["detail_level"] -= 0.1
        
        # Ajustar según el destinatario
        if context.get("recipient_type") == "team":
            base_style["formality"] -= 0.1
            base_style["enthusiasm"] += 0.1
        elif context.get("recipient_type") == "client":
            base_style["formality"] += 0.2
            base_style["detail_level"] += 0.1
        
        # Normalizar valores
        return {k: max(0.0, min(1.0, v)) for k, v in base_style.items()}
    
    def get_communication_style(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene el estilo de comunicación específico"""
        base_style = self.get_response_style()
        
        return {
            "tone": self._calculate_tone(context),
            "formality": base_style["formality"],
            "detail_level": base_style["detail_level"],
            "enthusiasm": base_style["enthusiasm"],
            "empathy": self.traits[TraitType.AGREEABLENESS],
            "directness": base_style["directness"]
        }
    
    def _calculate_tone(self, context: Dict[str, Any]) -> str:
        """Calcula el tono apropiado para la comunicación"""
        if context.get("urgency") == "high":
            return "assertive"
        elif context.get("communication_type") == "formal":
            return "professional"
        elif context.get("recipient_type") == "team":
            return "friendly"
        else:
            return "balanced"
