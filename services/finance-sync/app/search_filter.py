"""Search and Filter Engine for Architecture Components"""
from typing import List, Dict, Optional, Set
from enum import Enum
from architecture_models import ArchitectureModel, BaseNode, Edge, Layer, Flow

class SearchScope(str, Enum):
    NODES = "nodes"
    EDGES = "edges"
    LAYERS = "layers"
    FLOWS = "flows"
    ALL = "all"

class SearchEngine:
    """Full-text and semantic search across architecture"""
    
    def __init__(self, arch: ArchitectureModel):
        self.arch = arch
        self.build_index()
    
    def build_index(self):
        """Build search index"""
        self.node_index: Dict[str, List[BaseNode]] = {}
        self.edge_index: Dict[str, List[Edge]] = {}
        
        for node in self.arch.nodes:
            for tag in node.tags:
                if tag not in self.node_index:
                    self.node_index[tag] = []
                self.node_index[tag].append(node)
    
    def search(self, query: str, scope: SearchScope = SearchScope.ALL) -> Dict:
        """Search architecture"""
        results = {}
        query_lower = query.lower()
        
        if scope in [SearchScope.NODES, SearchScope.ALL]:
            results["nodes"] = [
                n for n in self.arch.nodes
                if query_lower in n.name.lower() or query_lower in (n.description or "").lower()
            ]
        
        if scope in [SearchScope.LAYERS, SearchScope.ALL]:
            results["layers"] = [
                l for l in self.arch.layers
                if query_lower in l.name.lower()
            ]
        
        return results
    
    def filter_by_type(self, node_type: str) -> List[BaseNode]:
        """Filter nodes by type"""
        return [n for n in self.arch.nodes if n.type.value == node_type]
    
    def filter_by_layer(self, layer_id: str) -> List[BaseNode]:
        """Filter nodes by layer"""
        return [n for n in self.arch.nodes if n.layer_id == layer_id]
    
    def filter_by_tags(self, tags: Set[str]) -> List[BaseNode]:
        """Filter nodes by tags"""
        return [
            n for n in self.arch.nodes
            if any(tag in n.tags for tag in tags)
        ]
