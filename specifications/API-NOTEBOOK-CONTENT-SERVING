---
itemId: API-NOTEBOOK-CONTENT-SERVING
itemTitle: Notebook Content Serving API
itemType: Software Item Spec
itemFulfills: SWR-NOTEBOOK-3
itemExtends: ADR-15-NOTEBOOK-SERVER-LIFECYCLE-MANAGEMENT
owner: engineering@aignostics.com
approvers: product@aignostics.com, architecture@aignostics.com
informed: stakeholders@aignostics.com
date: 2025-07-31
status: active
product: Platform
platform: Platform
components: 
  - HTTP API Gateway
  - Notebook Content Service
  - iframe Integration Layer
  - Query Parameter Handler
risk: low
sop: SW-SOP-01
---

# Notebook Content Serving API

HTTP API endpoints for serving notebook content with embedded iframe functionality and query parameter processing.

## Base URL

```
https://api.aignostics.com/notebook
```

## Endpoints

### GET /notebook/{run_id}

Serve notebook content with embedded iframe functionality for application run results.

**Parameters:**
- `run_id` (path): Application run identifier
- `results_folder` (query): Results directory path for notebook access

**Request Example:**
```http
GET /notebook/4711?results_folder=/tmp HTTP/1.1
Host: api.aignostics.com
Authorization: Bearer {token}
```

**Response:**
- **Status**: `200 OK`
- **Content-Type**: `text/html`
- **Body**: HTML content with embedded iframe

**Response Example:**
```http
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 485

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Notebook - Run 4711</title>
    <style>
        body { margin: 0; padding: 0; }
        iframe { width: 100%; height: 100vh; border: none; }
    </style>
</head>
<body>
    <iframe 
        src="http://127.0.0.1:8001?run_id=4711&results_folder=/tmp"
        title="Notebook Server"
        sandbox="allow-scripts allow-same-origin allow-forms">
    </iframe>
</body>
</html>
```

### iframe Source URL Format

The embedded iframe uses localhost/127.0.0.1 addressing with run-specific parameters:

**URL Pattern:**
```
http://127.0.0.1:8001?run_id={run_id}&results_folder={results_folder}
```

**Parameter Encoding:**
- `run_id`: Application run identifier (URL-encoded)
- `results_folder`: File system path for results (URL-encoded)

**Example URLs:**
```bash
# Basic run access
http://127.0.0.1:8001?run_id=4711&results_folder=/tmp

# Complex path encoding
http://127.0.0.1:8001?run_id=analysis_2024&results_folder=%2Fuser%2Fdata%2Fresults

# Multiple parameters
http://127.0.0.1:8001?run_id=4711&results_folder=/tmp&session_id=abc123
```

## Query Parameter Handling

### Supported Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `results_folder` | string | Yes | Target directory path for notebook results |
| `session_id` | string | No | Optional session identifier for tracking |
| `view_mode` | string | No | Display mode: `full`, `embedded`, `preview` |

### Parameter Validation

```python
# Query parameter validation patterns
RESULTS_FOLDER_PATTERN = r'^[/\\]?[\w\-\./_\\]+$'
SESSION_ID_PATTERN = r'^[a-zA-Z0-9\-_]{1,64}$'
VIEW_MODE_OPTIONS = ['full', 'embedded', 'preview']

# Example validation
def validate_query_params(results_folder: str, session_id: str = None, view_mode: str = 'full'):
    if not re.match(RESULTS_FOLDER_PATTERN, results_folder):
        raise ValueError("Invalid results_folder format")
    
    if session_id and not re.match(SESSION_ID_PATTERN, session_id):
        raise ValueError("Invalid session_id format")
    
    if view_mode not in VIEW_MODE_OPTIONS:
        raise ValueError(f"Invalid view_mode. Must be one of: {VIEW_MODE_OPTIONS}")
```

## Error Handling

### HTTP Status Codes

| Status | Condition | Response |
|--------|-----------|----------|
| `200` | Successful content serving | HTML with iframe |
| `400` | Invalid query parameters | Error details |
| `401` | Authentication required | Authentication error |
| `404` | Run ID not found | Not found error |
| `500` | Server error | Internal error |

### Error Response Format

```json
{
    "error": {
        "code": "INVALID_QUERY_PARAMS",
        "message": "Invalid results_folder format",
        "details": {
            "parameter": "results_folder",
            "value": "invalid//path",
            "expected_format": "Valid file system path"
        }
    }
}
```

## Security Considerations

### iframe Security

```html
<!-- Secure iframe configuration -->
<iframe 
    src="http://127.0.0.1:8001?run_id=4711&results_folder=/tmp"
    sandbox="allow-scripts allow-same-origin allow-forms"
    referrerpolicy="strict-origin-when-cross-origin">
</iframe>
```

### Input Sanitization

- **Path Traversal Prevention**: Validate `results_folder` against directory traversal attacks
- **XSS Protection**: Sanitize all query parameters before HTML embedding
- **Parameter Validation**: Strict validation of all input parameters

### Authentication Integration

```python
# Authentication middleware integration
@require_authentication
@validate_run_access
def serve_notebook_content(run_id: str, results_folder: str):
    # Verify user has access to specified run
    if not user_has_run_access(current_user, run_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Generate secure iframe content
    return generate_notebook_iframe(run_id, results_folder)
```

## Integration with Notebook Server

### Server Communication

The API integrates with the notebook server lifecycle management:

1. **Server Status Check**: Verify notebook server is running for the run_id
2. **URL Generation**: Generate appropriate localhost URLs with parameters
3. **Health Monitoring**: Ensure server availability before serving content
4. **Session Management**: Coordinate with session management for user access

### Example Integration

```python
from aignostics.notebook import NotebookServerManager

async def serve_notebook_endpoint(run_id: str, results_folder: str):
    # Check server status
    server_manager = NotebookServerManager()
    
    if not await server_manager.is_server_running(run_id):
        await server_manager.start_server(run_id, results_folder)
    
    # Get server URL
    server_url = await server_manager.get_server_url(run_id)
    
    # Generate iframe content
    iframe_src = f"{server_url}?run_id={run_id}&results_folder={results_folder}"
    
    return generate_html_response(iframe_src)
```

## Related Documentation

- [ADR-15: Notebook Server Lifecycle Management](ADR-15-NOTEBOOK-SERVER-LIFECYCLE-MANAGEMENT.md)
- [ADR-16: Notebook Web Integration Architecture](ADR-16-NOTEBOOK-WEB-INTEGRATION-ARCHITECTURE.md)
- [Notebook Security Guidelines](docs/NOTEBOOK_SECURITY_GUIDELINES.md)
- [API Authentication Guide](docs/API_AUTHENTICATION.md)