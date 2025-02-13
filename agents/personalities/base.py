from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class TraitType(Enum):
    OPENNESS = "openness"
    CONSCIENTIOUSNESS = "conscientiousness"
    EXTRAVERSION = "extraversion"
    AGREEABLENESS = "agreeableness"
    NEUROTICISM = "neuroticism"

class ValueType(Enum):
    EFFICIENCY = "efficiency"
    CREATIVITY = "creativity"
    PRECISION = "precision"
    COLLABORATION = "collaboration"

@dataclass
class PersonalityTrait:
    type: TraitType
    value: float  # 0.0 to 1.0
    description: str

@dataclass
class PersonalityValue:
    type: ValueType
    value: float  # 0.0 to 1.0
    description: str

class BasePersonality:
    def __init__(
        self,
        name: str,
        role: str,
        traits: Dict[TraitType, float],
        values: Dict[ValueType, float],
        description: Optional[str] = None
    ):
        self.name = name
        self.role = role
        self.description = description or f"{role} named {name}"
        
        # Inicializar traits con valores por defecto
        self.traits = {
            TraitType.OPENNESS: 0.5,
            TraitType.CONSCIENTIOUSNESS: 0.5,
            TraitType.EXTRAVERSION: 0.5,
            TraitType.AGREEABLENESS: 0.5,
            TraitType.NEUROTICISM: 0.5,
            **{t: v for t, v in traits.items()}
        }
        
        # Inicializar values con valores por defecto
        self.values = {
            ValueType.EFFICIENCY: 0.5,
            ValueType.CREATIVITY: 0.5,
            ValueType.PRECISION: 0.5,
            ValueType.COLLABORATION: 0.5,
            **{v: val for v, val in values.items()}
        }
    
    def get_response_style(self) -> Dict[str, float]:
        """Calcula el estilo de respuesta basado en traits y values"""
        return {
            "formality": self._calculate_formality(),
            "detail_level": self._calculate_detail_level(),
            "enthusiasm": self._calculate_enthusiasm(),
            "directness": self._calculate_directness()
        }
    
    def _calculate_formality(self) -> float:
        """Calcula el nivel de formalidad basado en traits"""
        return (
            self.traits[TraitType.CONSCIENTIOUSNESS] * 0.4 +
            self.traits[TraitType.AGREEABLENESS] * 0.3 +
            (1 - self.traits[TraitType.EXTRAVERSION]) * 0.3
        )
    
    def _calculate_detail_level(self) -> float:
        """Calcula el nivel de detalle basado en traits y values"""
        return (
            self.traits[TraitType.CONSCIENTIOUSNESS] * 0.4 +
            self.values[ValueType.PRECISION] * 0.4 +
            self.traits[TraitType.OPENNESS] * 0.2
        )
    
    def _calculate_enthusiasm(self) -> float:
        """Calcula el nivel de entusiasmo basado en traits"""
        return (
            self.traits[TraitType.EXTRAVERSION] * 0.5 +
            self.traits[TraitType.OPENNESS] * 0.3 +
            (1 - self.traits[TraitType.NEUROTICISM]) * 0.2
        )
    
    def _calculate_directness(self) -> float:
        """Calcula el nivel de franqueza basado en traits"""
        return (
            (1 - self.traits[TraitType.AGREEABLENESS]) * 0.4 +
            self.traits[TraitType.CONSCIENTIOUSNESS] * 0.3 +
            self.values[ValueType.EFFICIENCY] * 0.3
        )
    
    def adapt_to_context(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Adapta el estilo según el contexto"""
        base_style = self.get_response_style()
        
        # Ajustar según el tipo de tarea
        if context.get("task_type") == "technical":
            base_style["formality"] += 0.1
            base_style["detail_level"] += 0.2
        elif context.get("task_type") == "creative":
            base_style["formality"] -= 0.1
            base_style["enthusiasm"] += 0.1
        
        # Ajustar según la urgencia
        if context.get("urgency") == "high":
            base_style["directness"] += 0.2
            base_style["detail_level"] -= 0.1
        
        # Normalizar valores entre 0 y 1
        return {k: max(0.0, min(1.0, v)) for k, v in base_style.items()}
