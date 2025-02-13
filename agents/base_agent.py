from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class BaseAgent(ABC):
    def __init__(self, name: str, role: str, personality: str):
        self.name = name
        self.role = role
        self.personality = personality

    @abstractmethod
    async def process(self, message: str, context: Dict[str, Any]) -> str:
        """Process a message and return a response"""
        pass

    def format_response(self, message: str) -> str:
        """Format the response with the agent's signature"""
        return f"[{self.name}]: {message}"
