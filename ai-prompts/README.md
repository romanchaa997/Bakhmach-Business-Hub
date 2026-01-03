# AI Prompts Repository

This folder contains AI agent prompts and configuration schemas for the Bakhmach-Business-Hub ecosystem.

## Files

### UHIP/Audityzer Agent System Prompt
- **Files**: `UHIP-AUDITYZER-AGENT-SYSTEM-PROMPT.txt` / `.md`
- **Purpose**: Define the behavior and responsibilities of the technical assistance agent
- **Use Case**: Reads ARCHITECTURE.json and API contracts to answer developer questions
- **Scope**: Architecture consultation, API contract reference, integration guidance, data flow analysis

### Agent Response Schema
- **File**: `AGENT-RESPONSE-SCHEMA.json`
- **Purpose**: Define the JSON structure for agent responses
- **Content**: Response format with result, confidence score, references, and suggested follow-ups
- **Used by**: Agent implementations in Python/Node.js

## Integration

### Python Usage
```python
import json
from pathlib import Path

# Load system prompt
with open('UHIP-AUDITYZER-AGENT-SYSTEM-PROMPT.txt', 'r') as f:
    system_prompt = f.read()

# Load response schema
with open('AGENT-RESPONSE-SCHEMA.json', 'r') as f:
    response_schema = json.load(f)
```

### Node.js Usage
```javascript
const fs = require('fs');
const systemPrompt = fs.readFileSync('UHIP-AUDITYZER-AGENT-SYSTEM-PROMPT.txt', 'utf-8');
const responseSchema = JSON.parse(fs.readFileSync('AGENT-RESPONSE-SCHEMA.json', 'utf-8'));
```

## Development

When adding new prompts:
1. Follow the existing naming convention: `[PROJECT]-AGENT-[DESCRIPTOR].[FORMAT]`
2. Include both `.txt` (raw text) and `.md` (markdown) versions
3. Create a corresponding schema file in JSON format
4. Update this README with file descriptions
5. Commit with descriptive message using `feat:` prefix
