import os
from typing import List, Dict, Any, Optional
from serpapi import GoogleSearch
from bs4 import BeautifulSoup
import requests
import json

class SearchService:
    def __init__(self):
        self.serp_api_key = os.getenv('SERP_API_KEY')
        if not self.serp_api_key:
            raise ValueError("SERP_API_KEY environment variable not set")
        self.search_history: List[Dict[str, Any]] = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    async def google_search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Perform a Google search using SerpAPI"""
        try:
            params = {
                "engine": "google",
                "q": query,
                "api_key": self.serp_api_key,
                "num": num_results
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            organic_results = results.get('organic_results', [])
            return [{
                'title': item.get('title', ''),
                'link': item.get('link', ''),
                'snippet': item.get('snippet', ''),
                'source': 'google'
            } for item in organic_results]
            
        except Exception as e:
            print(f"Error en SerpAPI Search: {e}")
            return []



    async def extract_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract main content from a webpage with metadata"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'iframe', 'form']):
                element.decompose()
                
            # Extract metadata
            metadata = {
                'title': soup.title.string if soup.title else '',
                'meta_description': soup.find('meta', {'name': 'description'}).get('content', '') if soup.find('meta', {'name': 'description'}) else '',
                'url': url,
                'timestamp': response.headers.get('last-modified', ''),
            }
            
            # Find main content
            main_content = soup.find('main') or soup.find('article') or soup.find('div', {'class': ['content', 'main', 'article']})
            if not main_content:
                main_content = soup.find('body')
            
            # Get main content
            main_content = soup.find('main') or soup.find('article') or soup.find('body')
            if main_content:
                content = main_content.get_text(strip=True)
                metadata['content'] = content
                return metadata
            return None
            
        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
            return None

    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Perform a search using SerpAPI"""
        results = await self.google_search(query)
        
        # Extract content for top results
        for result in results[:3]:
            content = await self.extract_content(result['link'])
            if content:
                result['full_content'] = content
        
        # Store in history
        self.search_history.append({
            'query': query,
            'results': results,
            'timestamp': None  # Add timestamp here
        })
        
        return results

    def get_recent_searches(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent search history"""
        return self.search_history[-limit:]

    def clear_history(self) -> None:
        """Clear search history"""
        self.search_history = []
