"""Architecture Visualization API Endpoints
FastAPI endpoints for exposing architecture visualization data
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from architecture_models import ArchitectureModel, UseCase, ChannelType
from visualization_matrix import VisualizationMatrix
from use_cases_config import get_enabled_layers_for_channel, USE_CASE_REGISTRY

router = APIRouter(prefix="/api/architecture", tags=["architecture"])

# In-memory store (replace with database)
architectures: dict = {"monobank-sync-v1": None}  # Will be populated


@router.get("/architectures", response_model=List[dict])
async def list_architectures():
    """Get list of all available architectures"""
    return [{"id": k, "name": k} for k in architectures.keys()]


@router.get("/architectures/{arch_id}")
async def get_architecture(arch_id: str):
    """Get complete architecture model"""
    if arch_id not in architectures:
        raise HTTPException(status_code=404, detail=f"Architecture {arch_id} not found")
    return architectures[arch_id].model_dump()


@router.get("/architectures/{arch_id}/filtered")
async def get_filtered_architecture(
    arch_id: str,
    use_case: UseCase,
    channel: ChannelType
):
    """Get architecture filtered for specific use-case and channel"""
    if arch_id not in architectures:
        raise HTTPException(status_code=404, detail=f"Architecture {arch_id} not found")
    
    arch = architectures[arch_id]
    enabled_layers = get_enabled_layers_for_channel(use_case, channel)
    
    # Filter layers
    filtered_layers = [
        layer for layer in arch.layers
        if layer.id in enabled_layers
    ]
    
    return {
        "id": arch.id,
        "name": arch.name,
        "layers": [layer.model_dump() for layer in filtered_layers],
        "use_case": use_case,
        "channel": channel
    }


@router.get("/visualization-config")
async def get_visualization_config(
    use_case: UseCase,
    channel: ChannelType,
    component_type: str = Query("node")
):
    """Get visualization configuration for use-case and channel"""
    fields = VisualizationMatrix.get_fields_for_usecase_channel(
        use_case.value, channel.value, component_type
    )
    rendering = VisualizationMatrix.get_rendering_config(
        use_case.value, channel.value
    )
    
    return {
        "fields": list(fields),
        "rendering": rendering,
        "use_case": use_case,
        "channel": channel,
        "component_type": component_type
    }


@router.get("/use-cases")
async def list_use_cases():
    """Get available use-cases and their enabled layers"""
    result = {}
    for use_case, config in USE_CASE_REGISTRY.items():
        result[use_case.value] = {
            "channels": {
                ch.value: list(layers)
                for ch, layers in config.enabled_layers.items()
            }
        }
    return result


@router.get("/layers/{arch_id}")
async def get_layers(arch_id: str):
    """Get all layers for an architecture"""
    if arch_id not in architectures:
        raise HTTPException(status_code=404, detail=f"Architecture {arch_id} not found")
    
    arch = architectures[arch_id]
    return [
        {
            "id": layer.id,
            "name": layer.name,
            "type": layer.type.value,
            "description": layer.description,
            "node_count": len(layer.nodes),
            "depth": layer.depth
        }
        for layer in arch.layers
    ]


@router.get("/nodes/{arch_id}")
async def get_nodes(arch_id: str, layer_id: Optional[str] = None):
    """Get nodes, optionally filtered by layer"""
    if arch_id not in architectures:
        raise HTTPException(status_code=404, detail=f"Architecture {arch_id} not found")
    
    arch = architectures[arch_id]
    nodes = arch.nodes
    
    if layer_id:
        nodes = [n for n in nodes if n.layer_id == layer_id]
    
    return [node.model_dump() for node in nodes]


@router.get("/edges/{arch_id}")
async def get_edges(arch_id: str):
    """Get all edges/connections for an architecture"""
    if arch_id not in architectures:
        raise HTTPException(status_code=404, detail=f"Architecture {arch_id} not found")
    
    arch = architectures[arch_id]
    return [edge.model_dump() for edge in arch.edges]


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "architecture-visualization-api"}
