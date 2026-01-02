# Architecture Visualization JSON Schema
## Bakhmach Business Hub - Interactive Visualization Model

**Version:** 1.0  
**Format:** JSON Schema + GraphQL  
**Target Formats:** Web (React/Three.js), XR (WebXR), PDF (Vector)  

---

## Purpose

This document defines the JSON schema for representing the Bakhmach Business Hub architecture in a format suitable for:
1. Interactive web-based visualization
2. XR/AR experiences (WebXR compatible)
3. Automated diagram generation
4. Real-time metrics overlay

---

## Core Schema Structure

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Bakhmach Business Hub Architecture",
  "type": "object",
  "required": ["version", "metadata", "domains", "connections"],
  "properties": {
    "version": {
      "type": "string",
      "description": "Schema version",
      "example": "1.0"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "name": { "type": "string" },
        "description": { "type": "string" },
        "owner": { "type": "string" },
        "lastUpdated": { "type": "string", "format": "date-time" },
        "status": { "enum": ["planning", "foundation", "implementation", "production"] }
      }
    },
    "domains": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/Domain"
      }
    },
    "connections": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/Connection"
      }
    },
    "metrics": {
      "type": "object",
      "$ref": "#/definitions/MetricsSnapshot"
    }
  },
  "definitions": {
    "Domain": {
      "type": "object",
      "required": ["id", "name", "type", "position"],
      "properties": {
        "id": { "type": "string", "description": "Unique identifier" },
        "name": { "type": "string", "description": "Domain name" },
        "type": {
          "enum": [
            "code_optimization",
            "ml_pipeline",
            "production_services",
            "daily_workflow",
            "consciousness_agi"
          ]
        },
        "description": { "type": "string" },
        "path": { "type": "string", "description": "Repository path" },
        "status": { "enum": ["planning", "foundation", "implementation", "production"] },
        "readiness": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "Readiness percentage"
        },
        "position": {
          "type": "object",
          "properties": {
            "x": { "type": "number" },
            "y": { "type": "number" },
            "z": { "type": "number", "description": "For 3D visualization" }
          },
          "required": ["x", "y"]
        },
        "dimensions": {
          "type": "object",
          "properties": {
            "width": { "type": "number" },
            "height": { "type": "number" },
            "depth": { "type": "number" }
          }
        },
        "color": {
          "type": "object",
          "properties": {
            "hex": { "type": "string", "pattern": "^#[0-9A-F]{6}$" },
            "rgb": {
              "type": "object",
              "properties": {
                "r": { "type": "integer", "minimum": 0, "maximum": 255 },
                "g": { "type": "integer", "minimum": 0, "maximum": 255 },
                "b": { "type": "integer", "minimum": 0, "maximum": 255 }
              }
            }
          }
        },
        "components": {
          "type": "array",
          "items": {
            "$ref": "#/definitions/Component"
          }
        },
        "metrics": {
          "type": "object",
          "additionalProperties": { "type": "number" }
        }
      }
    },
    "Component": {
      "type": "object",
      "required": ["id", "name", "type"],
      "properties": {
        "id": { "type": "string" },
        "name": { "type": "string" },
        "type": { "type": "string" },
        "description": { "type": "string" },
        "technology": { "type": "array", "items": { "type": "string" } },
        "dependencies": { "type": "array", "items": { "type": "string" } },
        "metrics": {
          "type": "object",
          "additionalProperties": {"type": "number" }
        }
      }
    },
    "Connection": {
      "type": "object",
      "required": ["id", "from", "to"],
      "properties": {
        "id": { "type": "string" },
        "from": { "type": "string", "description": "Source domain/component ID" },
        "to": { "type": "string", "description": "Target domain/component ID" },
        "type": { "enum": ["dependency", "data_flow", "communication", "inference"] },
        "weight": {
          "type": "number",
          "description": "Connection strength (0-1)"
        },
        "latency": {
          "type": "number",
          "description": "Average latency in ms"
        },
        "throughput": {
          "type": "number",
          "description": "Throughput in requests/sec"
        },
        "protocol": {
          "enum": ["REST", "GraphQL", "gRPC", "WebSocket", "Message Queue", "File Transfer"]
        },
        "bidirectional": { "type": "boolean" }
      }
    },
    "MetricsSnapshot": {
      "type": "object",
      "properties": {
        "timestamp": { "type": "string", "format": "date-time" },
        "overall_health_score": { "type": "number", "minimum": 0, "maximum": 100 },
        "domain_metrics": {
          "type": "object",
          "additionalProperties": {
            "type": "object",
            "properties": {
              "uptime_percentage": { "type": "number" },
              "error_rate": { "type": "number" },
              "response_time_p95": { "type": "number" },
              "readiness": { "type": "number" }
            }
          }
        }
      }
    }
  }
}
```

---

## Example Visualization Data

```json
{
  "version": "1.0",
  "metadata": {
    "name": "Bakhmach Business Hub",
    "description": "Integrated platform cooperative architecture",
    "owner": "@romanchaa997",
    "lastUpdated": "2025-12-04T12:00:00Z",
    "status": "foundation"
  },
  "domains": [
    {
      "id": "code_opt",
      "name": "Code Optimization",
      "type": "code_optimization",
      "path": "/code",
      "status": "foundation",
      "readiness": 20,
      "position": { "x": 0, "y": 0, "z": 0 },
      "dimensions": { "width": 200, "height": 150 },
      "color": { "hex": "#FF6B6B" },
      "components": [
        {
          "id": "profiler",
          "name": "Performance Profiler",
          "type": "tool",
          "technology": ["py-spy", "perf"],
          "metrics": { "latency_ms": 45, "cpu_usage_percent": 12 }
        },
        {
          "id": "benchmarker",
          "name": "Benchmark Suite",
          "type": "tool",
          "technology": ["pytest", "k6"]
        }
      ]
    },
    {
      "id": "ml_pipe",
      "name": "ML Pipeline",
      "type": "ml_pipeline",
      "path": "/ml",
      "status": "foundation",
      "readiness": 20,
      "position": { "x": 250, "y": 0, "z": 0 },
      "dimensions": { "width": 200, "height": 150 },
      "color": { "hex": "#4ECDC4" },
      "components": [
        { "id": "ingest", "name": "Data Ingestion", "type": "service" },
        { "id": "training", "name": "Model Training", "type": "service" },
        { "id": "registry", "name": "Model Registry", "type": "service" }
      ]
    },
    {
      "id": "prod_svc",
      "name": "Production Services",
      "type": "production_services",
      "path": "/services",
      "status": "foundation",
      "readiness": 25,
      "position": { "x": 500, "y": 0, "z": 0 },
      "color": { "hex": "#FFE66D" }
    }
  ],
  "connections": [
    {
      "id": "conn_1",
      "from": "code_opt",
      "to": "prod_svc",
      "type": "dependency",
      "weight": 0.8,
      "latency": 50,
      "protocol": "REST"
    },
    {
      "id": "conn_2",
      "from": "ml_pipe",
      "to": "prod_svc",
      "type": "data_flow",
      "weight": 0.7,
      "protocol": "gRPC"
    }
  ],
  "metrics": {
    "timestamp": "2025-12-04T12:00:00Z",
    "overall_health_score": 72.5,
    "domain_metrics": {
      "code_opt": { "uptime_percentage": 99.8, "error_rate": 0.02 },
      "ml_pipe": { "uptime_percentage": 99.5, "error_rate": 0.05 },
      "prod_svc": { "uptime_percentage": 99.9, "error_rate": 0.01 }
    }
  }
}
```

---

## Visualization Library Recommendations

### Web (2D/3D)
- **Three.js** - WebGL rendering
- **Babylon.js** - Advanced 3D engine
- **D3.js** - Data-driven diagrams
- **Cytoscape.js** - Network visualization

### XR/AR
- **WebXR API** - Native XR support
- **A-Frame** - WebXR abstraction layer
- **Babylon.js** - XR scene management

### PDF Export
- **SVG to PDF** - Vector graphics preservation
- **Puppeteer** - Headless rendering
- **PDFKit** - Dynamic PDF generation

---

## Rendering Pipelines

### Web Visualization Pipeline
1. Fetch JSON from GitHub API
2. Transform into visualization data
3. Render with Three.js
4. Add interactive metrics overlay
5. Real-time update via WebSocket

### XR Visualization Pipeline
1. Parse JSON schema
2. Generate 3D geometries
3. Position in virtual space
4. Enable hand-gesture interactions
5. Display real-time metrics in HUD

---

**Status:** Published  
**Distribution:** Public Repository  
**Last Updated:** December 4, 2025
