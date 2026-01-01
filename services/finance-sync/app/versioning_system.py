"""Independent Versioning System for Layers/Flows
Allows separate version control for architecture components
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from architecture_models import ArchitectureModel


class ComponentType(str, Enum):
    """Types of versionable components"""
    LAYERS = "layers"
    FLOWS = "flows"
    NODES = "nodes"
    EDGES = "edges"


class ChangeType(str, Enum):
    """Types of changes"""
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    REORDERED = "reordered"


class ComponentChange(BaseModel):
    """Record of a change to a component"""
    change_type: ChangeType
    component_id: str
    component_name: Optional[str] = None
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    description: Optional[str] = None
    timestamp: datetime = datetime.utcnow()


class ComponentVersion(BaseModel):
    """Version record for a specific component type"""
    id: str
    component_type: ComponentType
    version: str  # Semantic versioning: major.minor.patch
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    
    # Change tracking
    changes: List[ComponentChange] = []
    
    # Metadata
    author: Optional[str] = None
    commit_hash: Optional[str] = None
    commit_message: Optional[str] = None
    
    # Content snapshot
    content_hash: str = ""  # SHA256 hash of content
    
    tags: List[str] = []


class VersionHistory(BaseModel):
    """Complete version history for a component"""
    component_type: ComponentType
    versions: List[ComponentVersion] = []
    current_version: str = "1.0.0"
    
    def add_version(
        self,
        version: str,
        author: Optional[str] = None,
        commit_message: Optional[str] = None,
        changes: List[ComponentChange] = None
    ) -> ComponentVersion:
        """Add new version to history"""
        new_version = ComponentVersion(
            id=f"{self.component_type.value}-{version}",
            component_type=self.component_type,
            version=version,
            author=author,
            commit_message=commit_message,
            changes=changes or []
        )
        self.versions.append(new_version)
        self.current_version = version
        return new_version
    
    def get_version(self, version: str) -> Optional[ComponentVersion]:
        """Get specific version"""
        for v in self.versions:
            if v.version == version:
                return v
        return None
    
    def get_changes_between(
        self, 
        from_version: str, 
        to_version: str
    ) -> List[ComponentChange]:
        """Get all changes between two versions"""
        from_idx = None
        to_idx = None
        
        for i, v in enumerate(self.versions):
            if v.version == from_version:
                from_idx = i
            if v.version == to_version:
                to_idx = i
        
        if from_idx is None or to_idx is None or from_idx >= to_idx:
            return []
        
        changes = []
        for v in self.versions[from_idx + 1:to_idx + 1]:
            changes.extend(v.changes)
        
        return changes


class ArchitectureVersionManager:
    """Manager for versioning complete architecture"""
    
    def __init__(self):
        self.layer_history = VersionHistory(component_type=ComponentType.LAYERS)
        self.flow_history = VersionHistory(component_type=ComponentType.FLOWS)
        self.node_history = VersionHistory(component_type=ComponentType.NODES)
        self.edge_history = VersionHistory(component_type=ComponentType.EDGES)
        self.architecture_snapshots: List[tuple] = []  # (version, timestamp, model)
    
    def create_snapshot(
        self,
        model: ArchitectureModel,
        version: str,
        author: Optional[str] = None,
        commit_message: Optional[str] = None
    ) -> None:
        """Create snapshot of complete architecture at specific version"""
        self.architecture_snapshots.append((
            version,
            datetime.utcnow(),
            model,
            author,
            commit_message
        ))
    
    def get_snapshot(self, version: str) -> Optional[ArchitectureModel]:
        """Retrieve architecture snapshot by version"""
        for snap_version, timestamp, model, author, msg in self.architecture_snapshots:
            if snap_version == version:
                return model
        return None
