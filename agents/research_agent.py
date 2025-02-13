from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
from services.search_service import SearchService
from services.document_service import DocumentService
from services.analysis_service import AnalysisService
from services.knowledge_service import KnowledgeService

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Mike",
            role="Research Specialist",
            personality="Analítico, metódico y orientado al detalle"
        )
        self.current_research: Optional[Dict[str, Any]] = None
        self.research_history: List[Dict[str, Any]] = []
        
        # Initialize services
        self.search_service = SearchService()
        self.document_service = DocumentService()
        self.analysis_service = AnalysisService()
        self.knowledge_service = KnowledgeService()

    def extract_research_intent(self, message: str) -> Dict[str, Any]:
        """Extract the main research intent and parameters from a message"""
        msg = message.lower()
        intent = {
            'action': 'unknown',
            'topic': None,
            'scope': 'general',  # general, academic, news, etc.
            'depth': 'medium',   # shallow, medium, deep
            'format': 'summary'  # summary, detailed, comparative
        }
        
        # Determine primary action
        if any(word in msg for word in ["busca", "investiga", "encuentra", "search", "research", "find"]):
            intent['action'] = "search"
        elif any(word in msg for word in ["analiza", "resume", "analyze", "summarize"]):
            intent['action'] = "analyze"
        elif any(word in msg for word in ["guarda", "documenta", "save", "document"]):
            intent['action'] = "document"
        elif any(word in msg for word in ["compara", "relaciona", "compare", "relate"]):
            intent['action'] = "compare"
            
        # Extract scope
        if any(word in msg for word in ["academic", "científico", "paper", "journal"]):
            intent['scope'] = "academic"
        elif any(word in msg for word in ["news", "noticias", "actualidad"]):
            intent['scope'] = "news"
            
        # Extract depth
        if any(word in msg for word in ["detallado", "profundo", "exhaustivo", "detailed", "deep", "thorough"]):
            intent['depth'] = "deep"
        elif any(word in msg for word in ["breve", "rápido", "básico", "brief", "quick", "basic"]):
            intent['depth'] = "shallow"
            
        # Extract format preference
        if any(word in msg for word in ["detalle", "detailed"]):
            intent['format'] = "detailed"
        elif any(word in msg for word in ["compara", "compare"]):
            intent['format'] = "comparative"
            
        return intent

    async def get_research_context(self, history: List[Dict[str, Any]], current_intent: Dict[str, Any]) -> Dict[str, Any]:
        """Build research context from conversation history and current intent"""
        context = {
            "topic": current_intent.get('topic'),
            "scope": current_intent.get('scope', 'general'),
            "depth": current_intent.get('depth', 'medium'),
            "format": current_intent.get('format', 'summary'),
            "previous_findings": [],
            "related_topics": [],
            "excluded_sources": [],
            "preferred_sources": []
        }
        
        # Analyze recent history for context
        for msg in reversed(history[-5:]):
            if msg.get('role') == 'assistant' and msg.get('research_data'):
                context['previous_findings'].extend(msg['research_data'].get('findings', []))
                context['related_topics'].extend(msg['research_data'].get('related_topics', []))
                
            if msg.get('role') == 'user' and msg.get('preferences'):
                context['excluded_sources'].extend(msg['preferences'].get('excluded_sources', []))
                context['preferred_sources'].extend(msg['preferences'].get('preferred_sources', []))
                
        # Remove duplicates while preserving order
        context['previous_findings'] = list(dict.fromkeys(context['previous_findings']))
        context['related_topics'] = list(dict.fromkeys(context['related_topics']))
        context['excluded_sources'] = list(dict.fromkeys(context['excluded_sources']))
        context['preferred_sources'] = list(dict.fromkeys(context['preferred_sources']))
        
        return context

    async def process(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process research-related requests"""
        if context is None:
            context = {'conversation_history': []}
            
        history = context.get('conversation_history', [])
        intent = self.extract_research_intent(message)
        research_context = await self.get_research_context(history, intent)

        # Initialize response
        response = {
            'intent': intent,
            'findings': [],
            'summary': '',
            'sources': [],
            'analysis': None
        }

        try:
            # Perform research based on intent
            if intent['action'] == "search":
                # Adapt search query based on context
                search_query = message
                if intent['scope'] == 'academic':
                    search_query += ' research paper scientific journal'
                elif intent['scope'] == 'news':
                    search_query += ' news recent developments'
                
                search_results = await self.search_service.google_search(search_query)
                response['sources'] = search_results

                # Extract and analyze content from top results
                for result in search_results[:3]:
                    extracted = await self.search_service.extract_content(result['link'])
                    if extracted and 'content' in extracted:
                        analysis = await self.analysis_service.analyze_text(extracted['content'])
                        key_points = await self.analysis_service.extract_key_points(extracted['content'])
                        response['findings'].extend(key_points)
                        
                        # Store analysis if this is the first result
                        if response['analysis'] is None:
                            response['analysis'] = analysis
                            # Add metadata
                            response['metadata'] = {
                                'title': extracted.get('title', ''),
                                'description': extracted.get('meta_description', ''),
                                'url': extracted.get('url', ''),
                                'timestamp': extracted.get('timestamp', '')
                            }

            elif intent['action'] == "analyze":
                # Extract text to analyze if it's after a prefix
                text_to_analyze = message
                if 'analiza el siguiente texto:' in message.lower():
                    prefix_len = len('analiza el siguiente texto:')
                    text_to_analyze = message[message.lower().index('analiza el siguiente texto:') + prefix_len:].strip()
                
                print('Analizando texto:', repr(text_to_analyze))
                
                # Analyze provided content
                analysis = await self.analysis_service.analyze_text(text_to_analyze)
                key_points = await self.analysis_service.extract_key_points(text_to_analyze)
                response['findings'] = key_points
                response['analysis'] = analysis

            elif intent['action'] == "document":
                # Save research findings
                doc_id = await self.document_service.save_document({
                    'content': message,
                    'metadata': {
                        'type': 'research_note',
                        'timestamp': context.get('timestamp'),
                        'context': research_context
                    }
                })
                response['document_id'] = doc_id

            # Generate summary based on format preference
            if response['findings']:
                if intent['format'] == 'detailed':
                    response['summary'] = '\n'.join(response['findings'])
                else:
                    response['summary'] = await self.analysis_service.generate_summary(
                        ' '.join(response['findings']),
                        max_sentences=5 if intent['depth'] == 'deep' else 3
                    )

        except Exception as e:
            response['error'] = str(e)

        # Update research history
        self.research_history.append({
            'timestamp': context.get('timestamp'),
            'request': message,
            'response': response
        })

        return response
