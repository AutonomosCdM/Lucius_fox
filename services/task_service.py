from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os

class TaskService:
    def __init__(self):
        self.tasks_file = "data/tasks.json"
        self.tasks: List[Dict[str, Any]] = []
        self._load_tasks()

    def _load_tasks(self) -> None:
        """Load tasks from file"""
        if os.path.exists(self.tasks_file):
            with open(self.tasks_file, 'r') as f:
                self.tasks = json.load(f)
        else:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.tasks_file), exist_ok=True)
            self.tasks = []
            self._save_tasks()

    def _save_tasks(self) -> None:
        """Save tasks to file"""
        with open(self.tasks_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)

    async def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task"""
        task = {
            'id': len(self.tasks) + 1,
            'name': task_data['name'],
            'description': task_data.get('description', ''),
            'status': task_data.get('status', 'pending'),
            'priority': task_data.get('priority', 'medium'),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'due_date': task_data.get('due_date'),
            'assignee': task_data.get('assignee'),
            'project_id': task_data.get('project_id'),
            'dependencies': [],
            'metadata': {}
        }
        
        self.tasks.append(task)
        self._save_tasks()
        return task

    async def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Get a task by ID"""
        for task in self.tasks:
            if task['id'] == task_id:
                return task
        return None

    async def update_task(self, task_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a task"""
        for i, task in enumerate(self.tasks):
            if task['id'] == task_id:
                self.tasks[i].update(updates)
                self.tasks[i]['updated_at'] = datetime.now().isoformat()
                self._save_tasks()
                return self.tasks[i]
        return None

    async def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        for i, task in enumerate(self.tasks):
            if task['id'] == task_id:
                del self.tasks[i]
                self._save_tasks()
                return True
        return False

    async def list_tasks(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """List all tasks, optionally filtered"""
        if not filters:
            return self.tasks

        filtered_tasks = []
        for task in self.tasks:
            match = True
            for key, value in filters.items():
                if key in task and task[key] != value:
                    match = False
                    break
            if match:
                filtered_tasks.append(task)

        return filtered_tasks

    async def assign_task(self, task_id: int, assignee: str) -> bool:
        """Assign a task to a user"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['assignee'] = assignee
                task['updated_at'] = datetime.now().isoformat()
                self._save_tasks()
                return True
        return False

    async def add_dependency(self, task_id: int, dependency_id: int) -> bool:
        """Add a dependency to a task"""
        for task in self.tasks:
            if task['id'] == task_id:
                if dependency_id not in task['dependencies']:
                    task['dependencies'].append(dependency_id)
                    task['updated_at'] = datetime.now().isoformat()
                    self._save_tasks()
                return True
        return False

    async def get_task_dependencies(self, task_id: int) -> List[Dict[str, Any]]:
        """Get all dependencies for a task"""
        task = await self.get_task(task_id)
        if not task:
            return []

        dependencies = []
        for dep_id in task['dependencies']:
            dep = await self.get_task(dep_id)
            if dep:
                dependencies.append(dep)

        return dependencies

    async def get_project_tasks(self, project_id: int) -> List[Dict[str, Any]]:
        """Get all tasks for a project"""
        return await self.list_tasks({'project_id': project_id})

    async def get_assignee_tasks(self, assignee: str) -> List[Dict[str, Any]]:
        """Get all tasks assigned to a user"""
        return await self.list_tasks({'assignee': assignee})
