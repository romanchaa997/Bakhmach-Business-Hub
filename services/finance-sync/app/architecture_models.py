"""Augmented Architecture Visualization Models for Finance Sync Service"""
from typing import List, Dict, Any, Optional, Literal, Set
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import json

# ===== ENUMERATIONS =====

class LayerType(str, Enum):
    """Architectural layers"""
    API = "api"
    SERVICE = "service"
    DATABASE = "database"
    INTEGRATION = "integration"
    AUTHENTICATION = "auth"
    CACHE = "cache"
    QUEUE = "queue"

class NodeType(str, Enum):
    """Node types in architecture"""
    SERVICE = "service"
    ENDPOINT = "endpoint"
    DATABASE = "database"
    QUEUE = "queue"
    EXTERNAL_API = "external_api"
    CACHE = "cache"
    COMPONENT = "component"

class UseCase(str, Enum):
    """Visualization use cases"""
    PRESENTATION = "presentation"
    DOCUMENTATION = "documentation"
    DEVELOPER_REVIEW = "dev"
    INVESTOR_PITCH = "investor"

class ChannelType(str, Enum):
    """Output channels"""
    WEB_VIEW = "web"
    XR = "xr"
    PDF = "pdf"
    INTERACTIVE = "interactive"

# ===== CORE MODELS =====

class BaseNode(BaseModel):
    """Base architecture node"""
    id: str = Field(..., description="Unique node identifier")
    name: str = Field(..., description="Human-readable name")
    type: NodeType = Field(..., description="Node type")
    description: Optional[str] = None
    layer_id: str = Field(..., description="Parent layer ID")
    x: float = Field(default=0)
    y: float = Field(default=0)
    width: float = Field(default=100)
    height: float = Field(default=100)
    color: str = Field(default="#3498db")
    icon: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)

class Edge(BaseModel):
    """Connection between nodes"""
    id: str
    source_id: str
    target_id: str
    label: Optional[str] = None
    edge_type: Literal["data_flow", "call", "dependency", "integration"] = "data_flow"
    weight: float = Field(default=1.0)
    color: str = Field(default="#95a5a6")
    dashed: bool = Field(default=False)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Layer(BaseModel):
    """Architectural layer"""
    id: str
    name: str
    type: LayerType
    description: Optional[str] = None
    nodes: List[BaseNode] = Field(default_factory=list)
    depth: int = Field(default=0)
    color: str = Field(default="#ecf0f1")
    visible: bool = Field(default=True)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Flow(BaseModel):
    """Data or control flow"""
    id: str
    name: str
    description: Optional[str] = None
    edges: List[str] = Field(default_factory=list)
    flow_type: Literal["request", "response", "event", "sync", "async"] = "request"
    sequence: int = Field(default=0)
    color: str = Field(default="#e74c3c")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ArchitectureModel(BaseModel):
    """Complete architecture model"""
    id: str
    name: str
    description: Optional[str] = None
    version: str = Field(default="1.0.0")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Core components
    nodes: List[BaseNode] = Field(default_factory=list)
    edges: List[Edge] = Field(default_factory=list)
    layers: List[Layer] = Field(default_factory=list)
    flows: List[Flow] = Field(default_factory=list)
    
    # Metadata
    stack: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def to_json(self) -> str:
        return json.dumps(self.model_dump(), default=str, indent=2)

class VersionSnapshot(BaseModel):
    """Versioned snapshot"""
    id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str
    model: ArchitectureModel
    changes: Dict[str, Any] = Field(default_factory=dict)
    author: Optional[str] = None
    commit_message: Optional[str] = None
