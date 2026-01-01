"""Architecture Manager - Central Integration Point
Orchestrates all architecture visualization components
"""
from typing import Dict, Optional, List
from architecture_models import ArchitectureModel, UseCase, ChannelType
from visualization_matrix import VisualizationMatrix
from versioning_system import ArchitectureVersionManager
from rendering_engines import RenderingEngine
from use_cases_config import get_enabled_layers_for_channel, MONOBANK_ARCHITECTURE


class ArchitectureManager:
    """Central manager for architecture visualization system"""
    
    def __init__(self):
        """Initialize manager with all components"""
        self.architectures: Dict[str, ArchitectureModel] = {}
        self.version_manager = ArchitectureVersionManager()
        self.rendering_engine = RenderingEngine()
        self.visualization_matrix = VisualizationMatrix()
        
        # Load default architecture
        self.register_architecture(MONOBANK_ARCHITECTURE)
    
    def register_architecture(self, arch: ArchitectureModel) -> None:
        """Register a new architecture"""
        self.architectures[arch.id] = arch
        self.version_manager.create_snapshot(
            arch,
            arch.version,
            author="system",
            commit_message=f"Registered {arch.name}"
        )
    
    def get_architecture(self, arch_id: str) -> Optional[ArchitectureModel]:
        """Get architecture by ID"""
        return self.architectures.get(arch_id)
    
    def render_architecture(
        self,
        arch_id: str,
        use_case: UseCase,
        channel: ChannelType
    ) -> str:
        """Render architecture for specific use-case and channel"""
        arch = self.get_architecture(arch_id)
        if not arch:
            raise ValueError(f"Architecture {arch_id} not found")
        
        return self.rendering_engine.render(arch, use_case, channel)
    
    def get_visualization_config(
        self,
        use_case: UseCase,
        channel: ChannelType,
        component_type: str = "node"
    ) -> Dict:
        """Get visualization configuration"""
        fields = VisualizationMatrix.get_fields_for_usecase_channel(
            use_case.value, channel.value, component_type
        )
        rendering = VisualizationMatrix.get_rendering_config(
            use_case.value, channel.value
        )
        
        return {
            "fields": list(fields),
            "rendering": rendering,
            "use_case": use_case.value,
            "channel": channel.value
        }
    
    def get_enabled_layers(
        self,
        arch_id: str,
        use_case: UseCase,
        channel: ChannelType
    ) -> List[str]:
        """Get enabled layers for architecture"""
        arch = self.get_architecture(arch_id)
        if not arch:
            raise ValueError(f"Architecture {arch_id} not found")
        
        enabled_layer_ids = get_enabled_layers_for_channel(use_case, channel)
        return [
            layer.id for layer in arch.layers
            if layer.id in enabled_layer_ids
        ]
    
    def create_version(
        self,
        arch_id: str,
        version: str,
        author: Optional[str] = None,
        commit_message: Optional[str] = None
    ) -> None:
        """Create new version of architecture"""
        arch = self.get_architecture(arch_id)
        if not arch:
            raise ValueError(f"Architecture {arch_id} not found")
        
        arch.version = version
        self.version_manager.create_snapshot(
            arch, version, author, commit_message
        )
    
    def list_architectures(self) -> List[Dict]:
        """Get list of all registered architectures"""
        return [
            {
                "id": arch.id,
                "name": arch.name,
                "version": arch.version,
                "stack": arch.stack,
                "layer_count": len(arch.layers),
                "node_count": len(arch.nodes),
                "edge_count": len(arch.edges)
            }
            for arch in self.architectures.values()
        ]
    
    def get_architecture_summary(self, arch_id: str) -> Dict:
        """Get summary of architecture"""
        arch = self.get_architecture(arch_id)
        if not arch:
            raise ValueError(f"Architecture {arch_id} not found")
        
        return {
            "id": arch.id,
            "name": arch.name,
            "description": arch.description,
            "version": arch.version,
            "stack": arch.stack,
            "tags": arch.tags,
            "layers": [
                {"id": l.id, "name": l.name, "type": l.type.value}
                for l in arch.layers
            ],
            "statistics": {
                "total_layers": len(arch.layers),
                "total_nodes": len(arch.nodes),
                "total_edges": len(arch.edges),
                "total_flows": len(arch.flows)
            }
        }


# Global manager instance
_manager: Optional[ArchitectureManager] = None


def get_manager() -> ArchitectureManager:
    """Get or create global manager instance"""
    global _manager
    if _manager is None:
        _manager = ArchitectureManager()
    return _manager


def initialize_manager() -> ArchitectureManager:
    """Initialize and return manager"""
    global _manager
    _manager = ArchitectureManager()
    return _manager
