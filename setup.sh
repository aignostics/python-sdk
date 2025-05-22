echo "Creating ~/.aignostics/.env file"
mkdir -p ~/.aignostics
cat > ~/.aignostics/.env << 'EOF'
CLIENT_ID_DEVICE=YOUR_DYNAMIC_SECRET
CLIENT_ID_INTERACTIVE=YOUR_DYNAMIC_SECRET
AIGNOSTICS_SENTRY_DSN=https://5e2b6e59746a3cb502589d8c2f0e3b64@o443095.ingest.us.sentry.io/4509130454466560
AIGNOSTICS_LOGFIRE_TOKEN=pylf_v1_eu_CwtB1kc64d42qClGkVHLgZ65X4yFCSwPS6lv8ydw35Wm
AIGNOSTICS_BUCKET_PROTOCOL=gs
AIGNOSTICS_BUCKET_NAME=aignostics-platform-ext-a4f7e9
AIGNOSTICS_BUCKET_HMAC_ACCESS_KEY_ID=YOUR_STATIC_SECRET
AIGNOSTICS_BUCKET_HMAC_SECRET_ACCESS_KEY=YOUR_STATIC_SECRET
EOF
if ! command -v uv &> /dev/null; then
  echo "uv not found, installing..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  source $HOME/.local/bin/env
else
  UV_VERSION=$(uv --version | cut -d' ' -f2)
  echo "uv version $UV_VERSION found"
  if [ "$(printf '%s\n' "0.6.17" "$UV_VERSION" | sort -V | head -n1)" != "0.6.17" ]; then
    echo "Updating uv to the latest version..."
    UV_PATH=$(which uv)
    if [[ "$UV_PATH" == *"brew"* ]]; then
      echo "Updating uv using Homebrew..."
      brew upgrade uv
    else
      echo "Updating uv using the installer..."
      uv self update
    fi
  else
    echo "uv is up to date"
  fi 
fi
uvx --from git+https://github.com/aignostics/python-sdk@feat/cli-e2e-finally --with marimo aignostics system install
uvx --from git+https://github.com/aignostics/python-sdk@feat/cli-e2e-finally --with marimo aignostics --help
