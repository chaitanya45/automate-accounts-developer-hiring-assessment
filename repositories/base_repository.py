from abc import ABC, abstractmethod
from typing import Any, Optional, List

class BaseRepository(ABC):
    """Base repository with common database operations"""
    
    def __init__(self, model_class):
        self.model_class = model_class
    
    @abstractmethod
    def create(self, **kwargs) -> Any:
        """Create a new record"""
        pass
    
    @abstractmethod
    def get_by_id(self, record_id: str) -> Optional[Any]:
        """Get record by ID"""
        pass
    
    @abstractmethod
    def get_all(self) -> List[Any]:
        """Get all records"""
        pass
    
    @abstractmethod
    def update(self, record_id: str, **kwargs) -> Optional[Any]:
        """Update record"""
        pass
    
    @abstractmethod
    def delete(self, record_id: str) -> bool:
        """Delete record"""
        pass
