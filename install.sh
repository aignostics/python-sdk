#!/bin/sh
# shellcheck shell=sh

# Default environment is "local"
ENV="local"

# Parse command line arguments
i=0
while [ $i -lt $# ]; do
    i=$((i + 1))
    arg="${!i}"
    
    case $arg in
        --env=*)
            ENV="${arg#*=}"
            ;;
        --env)
            i=$((i + 1))
            if [ $i -le $# ]; then
                ENV="${!i}"
            fi
            ;;
        *)
            # Unknown option
            ;;
    esac
done

echo "Installing dev tools to enable project management with oe-python-template and derivatives ..."
echo "Environment: $ENV"

# Format: "tool;package;url;environments"
# environments is a comma-separated list of environments where the tool should be installed
# If environments is empty, tool is installed in all environments
# Defaul environment is "local"
LINUX_APT_TOOLS=(
    "curl;curl;https://curl.se/;"
)

BREW_TOOLS=(
    "act;act;https://nektosact.com/;local"
    "git;git;https://git-scm.com/;local"
    "gmake;make;https://www.gnu.org/software/make/;"
    "gpg;gnupg;https://gnupg.org/;"
    "jq;jq;https://jqlang.org/;"
    "magick;imagemagick;https://imagemagick.org/;"
    "nixpacks;nixpacks;https://nixpacks.com/;"
    "pinact;pinact;https://github.com/suzuki-shunsuke/pinact;local"
    "pnpm;pnpm;https://pnpm.io/;"
    "trivy;trivy;https://trivy.dev/latest/;"
    "uv;uv;https://docs.astral.sh/uv/;local"
    "xmllint;libxml2;https://en.wikipedia.org/wiki/Libxml2;"
)

MAC_BREW_TOOLS=(
    "pinentry-mac;pinentry-mac;https://github.com/GPGTools/pinentry;local"
)

LINUX_BREW_TOOLS=(
    # Linux-specific Homebrew tools will be added here
)

UV_TOOLS=(
    "copier;copier;https://copier.readthedocs.io/;local"
)

# Function to check if a tool should be installed in the current environment
should_install_in_env() {
    local environments=$1
    
    # If environments is empty, install in all environments
    if [ -z "$environments" ]; then
        return 0  # true
    fi
    
    # Check if the current environment is in the list
    IFS=',' read -ra ENV_LIST <<< "$environments"
    for e in "${ENV_LIST[@]}"; do
        if [ "$e" = "$ENV" ]; then
            return 0  # true
        fi
    done
    
    return 1  # false
}

# Function to install/update brew tools
install_or_upgrade_brew_tool() {
    local tool=$1
    local package=$2
    local url=$3
    local environments=$4
    
    # Check if the tool should be installed in the current environment
    if ! should_install_in_env "$environments"; then
        echo "Skipping $tool installation (not needed in $ENV environment)"
        return
    fi

    if command -v "$tool" &> /dev/null; then
        tool_path=$(command -v "$tool")
        if [[ "$tool_path" == *"brew/"* ]]; then
            echo "$tool already installed via Homebrew at $tool_path, upgrading..."
            brew upgrade "$package" || true
        else
            echo "$tool already installed at $tool_path, skipping..."
        fi
    else
        echo "Installing $tool from $package... # $url"
        brew install "$package"
    fi
}

# Function to install/update Linux tools via apt
install_or_update_linux_apt_tool() {
    local tool=$1
    local package=$2
    local url=$3
    local environments=$4
    
    # Check if the tool should be installed in the current environment
    if ! should_install_in_env "$environments"; then
        echo "Skipping $tool installation (not needed in $ENV environment)"
        return
    fi

    if command -v "$tool" &> /dev/null; then
        echo "$tool already installed at $(command -v "$tool"), skipping..."
    else
        echo "Installing $tool... # $url"
        sudo apt-get update -y && sudo apt-get install --no-install-recommends "$package" -y
    fi
}

# Function to install/update tools via uv
install_or_update_uv_tool() {
    local tool=$1
    local package=$2
    local url=$3
    local environments=$4
    
    # Check if the tool should be installed in the current environment
    if ! should_install_in_env "$environments"; then
        echo "Skipping $tool installation (not needed in $ENV environment)"
        return
    fi

    if command -v "$tool" &> /dev/null; then
        echo "$tool already installed at $(command -v "$tool"), updating..."
        uv tool update "$tool"
    else
        echo "Installing $tool... # $url"
        uv tool install "$tool"
    fi
}

# Install/update Linux packages
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    for tool_entry in "${LINUX_APT_TOOLS[@]}"; do
        IFS=";" read -r tool package url environments <<< "$tool_entry"
        install_or_update_linux_apt_tool "$tool" "$package" "$url" "$environments"
    done
fi

# Install/update Homebrew itself
if ! command -v brew &> /dev/null; then
    # Check if we should install Homebrew in this environment
    if [ "$ENV" = "local" ]; then
        echo "Installing Homebrew... # https://brew.sh/"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    else
        echo "Skipping Homebrew installation (not needed in $ENV environment)"
    fi
elif [ "$ENV" = "local" ]; then
    echo "Homebrew already installed at $(command -v brew), updating..."
    brew update
fi

# Only proceed with Homebrew tools if brew is available
if command -v brew &> /dev/null; then
    # Install/update Homebrew tools
    for tool_entry in "${BREW_TOOLS[@]}"; do
        IFS=";" read -r tool package url environments <<< "$tool_entry"
        install_or_upgrade_brew_tool "$tool" "$package" "$url" "$environments"
    done
    
    # Install/update Homebrew tools for macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        for tool_entry in "${MAC_BREW_TOOLS[@]}"; do
            IFS=";" read -r tool package url environments <<< "$tool_entry"
            install_or_upgrade_brew_tool "$tool" "$package" "$url" "$environments"
        done
    fi
    
    # Install/update Homebrew tools for Linux
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        for tool_entry in "${LINUX_BREW_TOOLS[@]}"; do
            IFS=";" read -r tool package url environments <<< "$tool_entry"
            install_or_upgrade_brew_tool "$tool" "$package" "$url" "$environments"
        done
    fi
fi

# Install/update UV tools
for tool_entry in "${UV_TOOLS[@]}"; do
    IFS=";" read -r tool package url environments <<< "$tool_entry"
    install_or_update_uv_tool "$tool" "$package" "$url" "$environments"
done
