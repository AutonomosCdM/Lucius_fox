import asyncio
from agents.research_agent import ResearchAgent

async def test_mike():
    mike = ResearchAgent()
    
    # Prueba 1: Búsqueda básica
    mensaje = "Busca información sobre la inteligencia artificial y su impacto en la medicina"
    intent = mike.extract_research_intent(mensaje)
    print("\nIntención detectada:")
    print(intent)
    
    # Prueba 2: Análisis de contexto
    history = [
        {
            "role": "user",
            "content": "¿Qué avances hay en el diagnóstico por imagen?",
            "preferences": {
                "preferred_sources": ["academic", "medical journals"],
                "excluded_sources": ["blogs"]
            }
        },
        {
            "role": "assistant",
            "research_data": {
                "findings": ["Uso de deep learning en radiología"],
                "related_topics": ["machine learning en medicina", "diagnóstico automatizado"]
            }
        }
    ]
    
    context = await mike.get_research_context(history, intent)
    print("\nContexto de investigación:")
    print(context)

if __name__ == "__main__":
    asyncio.run(test_mike())
