"""MongoDB Models for Architecture Persistence
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId

class MongoBaseModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True

class ArchitectureDocument(MongoBaseModel):
    """MongoDB document for Architecture storage"""
    arch_id: str = Field(..., index=True)
    name: str
    description: Optional[str]
    version: str
    stack: List[str]
    tags: List[str]
    layers: List[Dict[str, Any]]
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    flows: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class VersionDocument(MongoBaseModel):
    """MongoDB document for Version history"""
    arch_id: str = Field(..., index=True)
    version: str = Field(..., index=True)
    snapshot: Dict[str, Any]
    author: Optional[str]
    commit_message: Optional[str]
    changes: List[Dict[str, Any]]
    content_hash: str

class ChangeLogDocument(MongoBaseModel):
    """MongoDB document for audit trail"""
    arch_id: str = Field(..., index=True)
    change_type: str
    component_id: str
    old_value: Optional[Any]
    new_value: Optional[Any]
    author: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
