---
itemId: API-QUPATH-INSTALLATION
itemTitle: QuPath Installation Management API
itemType: Software Item Spec
itemFulfills: SWR-VISUALIZATION-1, SWR-VISUALIZATION-2, SWR-VISUALIZATION-5
owner: engineering@aignostics.com
approvers: product@aignostics.com, architecture@aignostics.com
informed: stakeholders@aignostics.com
date: 2025-07-31
status: active
product: Platform
platform: Platform
components: 
  - QuPath Installation Service
  - Version Management API
  - Configuration API
risk: low
sop: SW-SOP-01
---

# QuPath Installation Management API

The QuPath Installation Management API enables users to manage QuPath installations, versions, and configurations for image analysis workflows.

## Base URL

```
https://api.aignostics.com/v1/qupath
```

## Authentication

All requests require a Bearer token:

```http
Authorization: Bearer <your-access-token>
```

## Endpoints

### List Available Versions

Get a list of available QuPath versions for installation.

```http
GET /qupath/versions
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `platform` | string | No | Filter by platform: `windows`, `macos`, `linux` |
| `architecture` | string | No | Filter by architecture: `x64`, `arm64` |
| `stable_only` | boolean | No | Show only stable releases (default: true) |

**Example Request:**

```bash
curl -X GET "https://api.aignostics.com/v1/qupath/versions?platform=linux&stable_only=true" \
  -H "Authorization: Bearer your-access-token"
```

**Example Response:**

```json
{
  "versions": [
    {
      "version": "0.5.0",
      "release_date": "2025-06-15",
      "stable": true,
      "platforms": ["windows", "macos", "linux"],
      "architectures": ["x64", "arm64"],
      "download_url": "https://github.com/qupath/qupath/releases/tag/v0.5.0",
      "changelog_url": "https://qupath.readthedocs.io/en/0.5/docs/changelog.html"
    },
    {
      "version": "0.4.3",
      "release_date": "2025-03-20",
      "stable": true,
      "platforms": ["windows", "macos", "linux"],
      "architectures": ["x64"],
      "download_url": "https://github.com/qupath/qupath/releases/tag/v0.4.3"
    }
  ]
}
```

### Get Installation Status

Check the status of QuPath installations for the user.

```http
GET /qupath/installations
```

**Example Request:**

```bash
curl -X GET "https://api.aignostics.com/v1/qupath/installations" \
  -H "Authorization: Bearer your-access-token"
```

**Example Response:**

```json
{
  "installations": [
    {
      "installation_id": "qp_inst_123",
      "version": "0.5.0",
      "platform": "linux",
      "architecture": "x64",
      "status": "ready",
      "install_path": "/opt/qupath/0.5.0",
      "installed_at": "2025-07-30T14:00:00Z",
      "last_used": "2025-07-31T09:30:00Z",
      "extensions": [
        {
          "name": "QuPath-ImageJ-Extension",
          "version": "1.0.0",
          "enabled": true
        }
      ]
    }
  ]
}
```

### Install QuPath Version

Install a specific version of QuPath.

```http
POST /qupath/install
```

**Request Body:**

```json
{
  "version": "0.5.0",
  "platform": "linux",
  "architecture": "x64",
  "install_extensions": ["imagej", "stardist"],
  "set_as_default": true
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | string | Yes | QuPath version to install |
| `platform` | string | Yes | Target platform |
| `architecture` | string | Yes | Target architecture |
| `install_extensions` | array | No | Extensions to install |
| `set_as_default` | boolean | No | Set as default installation |

**Example Request:**

```bash
curl -X POST "https://api.aignostics.com/v1/qupath/install" \
  -H "Authorization: Bearer your-access-token" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "0.5.0",
    "platform": "linux",
    "architecture": "x64",
    "install_extensions": ["imagej"]
  }'
```

**Example Response:**

```json
{
  "installation_id": "qp_inst_456",
  "status": "installing",
  "progress_url": "/qupath/installations/qp_inst_456/progress",
  "estimated_completion": "2025-07-31T11:15:00Z"
}
```

### Get Installation Progress

Monitor the progress of a QuPath installation.

```http
GET /qupath/installations/{installation_id}/progress
```

**Example Request:**

```bash
curl -X GET "https://api.aignostics.com/v1/qupath/installations/qp_inst_456/progress" \
  -H "Authorization: Bearer your-access-token"
```

**Example Response:**

```json
{
  "installation_id": "qp_inst_456",
  "status": "installing",
  "progress_percentage": 65,
  "current_step": "Installing extensions",
  "steps_completed": 3,
  "total_steps": 5,
  "estimated_completion": "2025-07-31T11:10:00Z",
  "logs": [
    "Downloading QuPath 0.5.0...",
    "Extracting installation files...",
    "Installing core components..."
  ]
}
```

### Configure Installation

Update configuration settings for a QuPath installation.

```http
PUT /qupath/installations/{installation_id}/config
```

**Request Body:**

```json
{
  "memory_limit_gb": 8,
  "java_options": ["-Xms2g", "-Xmx8g"],
  "default_image_server": "bioformats",
  "extensions": {
    "imagej": {
      "enabled": true,
      "memory_limit_mb": 1024
    },
    "stardist": {
      "enabled": false
    }
  }
}
```

**Example Request:**

```bash
curl -X PUT "https://api.aignostics.com/v1/qupath/installations/qp_inst_123/config" \
  -H "Authorization: Bearer your-access-token" \
  -H "Content-Type: application/json" \
  -d '{
    "memory_limit_gb": 8,
    "default_image_server": "bioformats"
  }'
```

**Example Response:**

```json
{
  "installation_id": "qp_inst_123",
  "config_updated": true,
  "restart_required": false,
  "updated_at": "2025-07-31T11:00:00Z"
}
```

### Launch QuPath Instance

Start a QuPath instance for image analysis.

```http
POST /qupath/installations/{installation_id}/launch
```

**Request Body:**

```json
{
  "project_path": "/data/projects/sample_analysis",
  "image_path": "/data/images/sample.tif",
  "headless": false,
  "script_path": "/scripts/analysis.groovy"
}
```

**Example Request:**

```bash
curl -X POST "https://api.aignostics.com/v1/qupath/installations/qp_inst_123/launch" \
  -H "Authorization: Bearer your-access-token" \
  -H "Content-Type: application/json" \
  -d '{
    "project_path": "/data/projects/sample_analysis",
    "headless": false
  }'
```

**Example Response:**

```json
{
  "session_id": "qp_session_789",
  "status": "launching",
  "access_url": "https://qupath.aignostics.com/sessions/qp_session_789",
  "launched_at": "2025-07-31T11:05:00Z"
}
```

### List Extensions

Get available extensions for QuPath installations.

```http
GET /qupath/extensions
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `qupath_version` | string | No | Filter by QuPath version compatibility |
| `category` | string | No | Filter by category: `analysis`, `visualization`, `import` |

**Example Request:**

```bash
curl -X GET "https://api.aignostics.com/v1/qupath/extensions?qupath_version=0.5.0" \
  -H "Authorization: Bearer your-access-token"
```

**Example Response:**

```json
{
  "extensions": [
    {
      "name": "imagej",
      "display_name": "ImageJ Integration",
      "version": "1.0.0",
      "description": "Integrate ImageJ functionality into QuPath",
      "category": "analysis",
      "compatible_versions": ["0.4.0", "0.5.0"],
      "download_url": "https://github.com/qupath/qupath-extension-imagej"
    },
    {
      "name": "stardist",
      "display_name": "StarDist Extension",
      "version": "2.1.0",
      "description": "Deep learning-based cell detection",
      "category": "analysis",
      "compatible_versions": ["0.5.0"]
    }
  ]
}
```

### Uninstall QuPath

Remove a QuPath installation and associated data.

```http
DELETE /qupath/installations/{installation_id}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `remove_data` | boolean | No | Remove associated project data (default: false) |

**Example Request:**

```bash
curl -X DELETE "https://api.aignostics.com/v1/qupath/installations/qp_inst_123?remove_data=false" \
  -H "Authorization: Bearer your-access-token"
```

**Example Response:**

```json
{
  "message": "QuPath installation qp_inst_123 has been scheduled for removal",
  "removal_id": "rem_abc123",
  "estimated_completion": "2025-07-31T11:30:00Z"
}
```

## CLI Usage

### List QuPath Versions

```bash
aignostics qupath versions [OPTIONS]
```

**Options:**

- `--platform` - Filter by platform: `windows`, `macos`, `linux`
- `--stable-only` - Show only stable releases

**Example:**

```bash
# List stable versions for Linux
aignostics qupath versions --platform linux --stable-only
```

### Install QuPath

```bash
aignostics qupath install <version> [OPTIONS]
```

**Options:**

- `--platform` - Target platform
- `--architecture` - Target architecture
- `--extensions` - Comma-separated list of extensions
- `--set-default` - Set as default installation

**Example:**

```bash
# Install QuPath with extensions
aignostics qupath install 0.5.0 \
  --platform linux \
  --extensions imagej,stardist \
  --set-default
```

### Launch QuPath

```bash
aignostics qupath launch [OPTIONS]
```

**Options:**

- `--installation-id` - Specific installation to use
- `--project` - Project path to open
- `--image` - Image file to load
- `--headless` - Run in headless mode

**Example:**

```bash
# Launch QuPath with project
aignostics qupath launch \
  --project /data/projects/sample_analysis \
  --image /data/images/sample.tif
```

### Configure QuPath

```bash
aignostics qupath config <installation_id> [OPTIONS]
```

**Options:**

- `--memory` - Memory limit in GB
- `--java-options` - Java runtime options
- `--enable-extension` - Enable specific extension
- `--disable-extension` - Disable specific extension

**Example:**

```bash
# Configure memory and extensions
aignostics qupath config qp_inst_123 \
  --memory 8 \
  --enable-extension imagej
```

## Python SDK

```python
from aignostics import AignosticsClient

# Initialize client
client = AignosticsClient(api_key="your-api-key")

# List available versions
versions = client.qupath.list_versions(platform="linux", stable_only=True)

# Install QuPath
installation = client.qupath.install(
    version="0.5.0",
    platform="linux",
    architecture="x64",
    extensions=["imagej", "stardist"]
)

# Monitor installation progress
progress = client.qupath.get_installation_progress(installation.installation_id)

# Configure installation
client.qupath.configure(
    installation_id="qp_inst_123",
    memory_limit_gb=8,
    extensions={"imagej": {"enabled": True}}
)

# Launch QuPath
session = client.qupath.launch(
    installation_id="qp_inst_123",
    project_path="/data/projects/sample_analysis"
)
```

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Request successful |
| 201 | Installation initiated |
| 202 | Operation accepted |
| 400 | Invalid request |
| 401 | Authentication required |
| 404 | Installation not found |
| 409 | Installation already exists |

## Error Responses

```json
{
  "error": {
    "code": "INSTALLATION_FAILED",
    "message": "QuPath installation failed",
    "details": {
      "installation_id": "qp_inst_456",
      "reason": "Download failed due to network error"
    }
  }
}
```

**Common Error Codes:**

- `INSTALLATION_FAILED` - Installation process failed
- `VERSION_NOT_AVAILABLE` - Requested version not available
- `PLATFORM_NOT_SUPPORTED` - Platform not supported
- `INSUFFICIENT_SPACE` - Not enough disk space for installation

## Rate Limits

- **Installation requests**: 5 per hour
- **Configuration updates**: 30 per minute
- **Launch requests**: 10 per minute
- **Status queries**: 60 per minute