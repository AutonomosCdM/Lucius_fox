from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os

class ProjectService:
    def __init__(self):
        self.projects_file = "data/projects.json"
        self.projects: List[Dict[str, Any]] = []
        self._load_projects()

    def _load_projects(self) -> None:
        """Load projects from file"""
        if os.path.exists(self.projects_file):
            with open(self.projects_file, 'r') as f:
                self.projects = json.load(f)
        else:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.projects_file), exist_ok=True)
            self.projects = []
            self._save_projects()

    def _save_projects(self) -> None:
        """Save projects to file"""
        with open(self.projects_file, 'w') as f:
            json.dump(self.projects, f, indent=2)

    async def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project"""
        project = {
            'id': len(self.projects) + 1,
            'name': project_data['name'],
            'description': project_data.get('description', ''),
            'status': project_data.get('status', 'active'),
            'priority': project_data.get('priority', 'medium'),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'tasks': [],
            'team': [],
            'metadata': {}
        }
        
        self.projects.append(project)
        self._save_projects()
        return project

    async def get_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Get a project by ID"""
        for project in self.projects:
            if project['id'] == project_id:
                return project
        return None

    async def update_project(self, project_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a project"""
        for i, project in enumerate(self.projects):
            if project['id'] == project_id:
                self.projects[i].update(updates)
                self.projects[i]['updated_at'] = datetime.now().isoformat()
                self._save_projects()
                return self.projects[i]
        return None

    async def delete_project(self, project_id: int) -> bool:
        """Delete a project"""
        for i, project in enumerate(self.projects):
            if project['id'] == project_id:
                del self.projects[i]
                self._save_projects()
                return True
        return False

    async def list_projects(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """List all projects, optionally filtered"""
        if not filters:
            return self.projects

        filtered_projects = []
        for project in self.projects:
            match = True
            for key, value in filters.items():
                if key in project and project[key] != value:
                    match = False
                    break
            if match:
                filtered_projects.append(project)

        return filtered_projects

    async def add_task_to_project(self, project_id: int, task_id: int) -> bool:
        """Add a task to a project"""
        for project in self.projects:
            if project['id'] == project_id:
                if task_id not in project['tasks']:
                    project['tasks'].append(task_id)
                    project['updated_at'] = datetime.now().isoformat()
                    self._save_projects()
                return True
        return False

    async def add_team_member(self, project_id: int, user_id: str) -> bool:
        """Add a team member to a project"""
        for project in self.projects:
            if project['id'] == project_id:
                if user_id not in project['team']:
                    project['team'].append(user_id)
                    project['updated_at'] = datetime.now().isoformat()
                    self._save_projects()
                return True
        return False

    async def get_project_stats(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Get project statistics"""
        project = await self.get_project(project_id)
        if not project:
            return None

        return {
            'task_count': len(project['tasks']),
            'team_size': len(project['team']),
            'status': project['status'],
            'age_days': (datetime.now() - datetime.fromisoformat(project['created_at'])).days
        }
