from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import os
import asyncio
from collections import deque

class MetricsService:
    def __init__(self):
        self.metrics_file = "data/metrics.json"
        self.metrics: Dict[str, Any] = {
            'cognitive_load': {
                'interactions_per_hour': 0,
                'complexity_score': 0,
                'override_rate': 0,
                'interaction_history': []
            },
            'system_health': {
                'response_time': 0,
                'success_rate': 0,
                'error_rate': 0,
                'last_errors': []
            },
            'autonomo_stats': {
                'lucius': {'tasks_completed': 0, 'avg_processing_time': 0, 'handoff_success_rate': 0},
                'mike': {'tasks_completed': 0, 'avg_processing_time': 0, 'handoff_success_rate': 0},
                'tom': {'tasks_completed': 0, 'avg_processing_time': 0, 'handoff_success_rate': 0}
            }
        }
        # Keep last hour of interactions in memory
        self.recent_interactions = deque(maxlen=1000)
        self._load_metrics()
        
    def _load_metrics(self) -> None:
        """Load metrics from file"""
        if os.path.exists(self.metrics_file):
            with open(self.metrics_file, 'r') as f:
                stored_metrics = json.load(f)
                # Update stored metrics while preserving structure
                for category in self.metrics:
                    if category in stored_metrics:
                        self.metrics[category].update(stored_metrics[category])

    def _save_metrics(self) -> None:
        """Save metrics to file"""
        os.makedirs(os.path.dirname(self.metrics_file), exist_ok=True)
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)

    async def record_interaction(self, interaction: Dict[str, Any]) -> None:
        """Record a user interaction"""
        now = datetime.now()
        interaction['timestamp'] = now.isoformat()
        self.recent_interactions.append(interaction)
        
        # Update interactions per hour
        hour_ago = now - timedelta(hours=1)
        recent_count = sum(1 for i in self.recent_interactions 
                         if datetime.fromisoformat(i['timestamp']) > hour_ago)
        self.metrics['cognitive_load']['interactions_per_hour'] = recent_count
        
        # Update complexity score (0-1)
        complexity = interaction.get('complexity', 0.5)
        self.metrics['cognitive_load']['complexity_score'] = (
            0.7 * self.metrics['cognitive_load']['complexity_score'] + 
            0.3 * complexity  # Weighted moving average
        )
        
        # Save interaction for analysis
        self.metrics['cognitive_load']['interaction_history'].append({
            'timestamp': interaction['timestamp'],
            'type': interaction.get('type'),
            'complexity': complexity
        })
        
        # Trim history if too long
        if len(self.metrics['cognitive_load']['interaction_history']) > 1000:
            self.metrics['cognitive_load']['interaction_history'] = (
                self.metrics['cognitive_load']['interaction_history'][-1000:]
            )
        
        await self._save_metrics_async()

    async def record_task(self, autonomo: str, task: Dict[str, Any]) -> None:
        """Record a task completion"""
        if autonomo not in self.metrics['autonomo_stats']:
            return
        
        stats = self.metrics['autonomo_stats'][autonomo]
        
        # Update task count
        stats['tasks_completed'] += 1
        
        # Update processing time
        if 'start_time' in task and 'end_time' in task:
            processing_time = (
                datetime.fromisoformat(task['end_time']) - 
                datetime.fromisoformat(task['start_time'])
            ).total_seconds()
            
            if stats['avg_processing_time'] == 0:
                stats['avg_processing_time'] = processing_time
            else:
                stats['avg_processing_time'] = (
                    0.9 * stats['avg_processing_time'] + 
                    0.1 * processing_time  # Exponential moving average
                )
        
        # Update handoff success rate
        if 'handoff_success' in task:
            current_rate = stats['handoff_success_rate']
            stats['handoff_success_rate'] = (
                0.95 * current_rate + 
                0.05 * (1.0 if task['handoff_success'] else 0.0)
            )
        
        await self._save_metrics_async()

    async def record_error(self, error: Dict[str, Any]) -> None:
        """Record a system error"""
        now = datetime.now()
        error['timestamp'] = now.isoformat()
        
        # Update error list
        self.metrics['system_health']['last_errors'].append(error)
        if len(self.metrics['system_health']['last_errors']) > 100:
            self.metrics['system_health']['last_errors'] = (
                self.metrics['system_health']['last_errors'][-100:]
            )
        
        # Update error rate (errors per hour)
        hour_ago = now - timedelta(hours=1)
        recent_errors = [e for e in self.metrics['system_health']['last_errors']
                        if datetime.fromisoformat(e['timestamp']) > hour_ago]
        self.metrics['system_health']['error_rate'] = len(recent_errors)
        
        await self._save_metrics_async()

    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        # Calculate current metrics
        status = {
            'cognitive_load': {
                'current_load': self.metrics['cognitive_load']['interactions_per_hour'] / 60.0,
                'complexity': self.metrics['cognitive_load']['complexity_score'],
                'override_rate': self.metrics['cognitive_load']['override_rate']
            },
            'system_health': {
                'error_rate': self.metrics['system_health']['error_rate'],
                'response_time': self.metrics['system_health']['response_time'],
                'success_rate': self.metrics['system_health']['success_rate']
            },
            'autonomo_status': {}
        }
        
        # Add autonomo stats
        for autonomo, stats in self.metrics['autonomo_stats'].items():
            status['autonomo_status'][autonomo] = {
                'active': stats['avg_processing_time'] > 0,
                'load': min(1.0, stats['tasks_completed'] / 100.0),
                'reliability': stats['handoff_success_rate']
            }
        
        return status

    async def _save_metrics_async(self) -> None:
        """Save metrics asynchronously"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._save_metrics)

    def get_cognitive_load(self) -> float:
        """Get current cognitive load (0-1)"""
        # Combine different factors into a single score
        interactions_weight = 0.4
        complexity_weight = 0.4
        override_weight = 0.2
        
        interactions_score = min(1.0, self.metrics['cognitive_load']['interactions_per_hour'] / 60.0)
        complexity_score = self.metrics['cognitive_load']['complexity_score']
        override_score = self.metrics['cognitive_load']['override_rate']
        
        return (
            interactions_weight * interactions_score +
            complexity_weight * complexity_score +
            override_weight * override_score
        )

    async def should_throttle(self) -> bool:
        """Determine if we should throttle interactions"""
        cognitive_load = self.get_cognitive_load()
        error_rate = self.metrics['system_health']['error_rate']
        
        # Throttle if:
        # 1. Cognitive load is too high (>80%)
        # 2. Error rate is too high (>5 errors/hour)
        # 3. Any autonomo is overloaded (>90% load)
        
        if cognitive_load > 0.8:
            return True
            
        if error_rate > 5:
            return True
            
        for autonomo, stats in self.metrics['autonomo_stats'].items():
            if stats['tasks_completed'] > 90:  # More than 90 tasks/hour
                return True
                
        return False
