import json
from pathlib import Path
from typing import List, Dict, Optional

class ThreadManager:
    """Manages conversation threads for the CLI application."""
    
    def __init__(self, config):
        self.config = config
        self.threads_dir = Path.home() / ".cllm" / "threads"
        self.threads_dir.mkdir(parents=True, exist_ok=True)
    
    def get_thread_path(self, thread_id: str) -> Path:
        """Get the file path for a thread."""
        return self.threads_dir / f"{thread_id}.json"
    
    def load_history(self, thread_id: Optional[str] = None) -> List[Dict[str, str]]:
        """Load conversation history from a thread file."""
        thread_file = self.get_thread_path(thread_id)
        
        if thread_file.exists():
            return json.loads(thread_file.read_text())
        return []
    
    def save_history(self, history: List[Dict[str, str]], thread_id: Optional[str] = None) -> None:
        """Save conversation history to a thread file."""
        thread_file = self.get_thread_path(thread_id)
        
        thread_file.write_text(json.dumps(history, indent=2))
    
    def clear_thread(self, thread_id: str) -> bool:
        """Clear a thread's history."""
        thread_file = self.get_thread_path(thread_id)
        if thread_file.exists():
            thread_file.unlink()
            return True
        return False
    
    def list_threads(self) -> list[str]:
        """List all available threads."""
        thread_path = Path.home() / ".cllm" / "threads"
        if not thread_path.exists():
            return []
        
        return [f.stem for f in thread_path.glob("*.json")]