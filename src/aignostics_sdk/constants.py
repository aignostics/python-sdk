"""Static configuration of Aignostics SDK (slim package)."""

from aignostics_sdk.utils._constants import __version__

# Organizations with internal/advanced access (e.g., platform-wide queue visibility, GPU config)
INTERNAL_ORGS = {"aignostics", "pre-alpha-org", "lmu", "charite"}

# Application IDs
HETA_APPLICATION_ID = "he-tme"
TEST_APP_APPLICATION_ID = "test-app"

# WSI supported file extensions
WSI_SUPPORTED_FILE_EXTENSIONS = {".dcm", ".tiff", ".tif", ".svs"}
WSI_SUPPORTED_FILE_EXTENSIONS_TEST_APP = {".tiff"}

# API versions (keyed by version name, value is the SDK version string)
API_VERSIONS: dict[str, str] = {"v1": __version__}
