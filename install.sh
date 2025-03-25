#!/bin/sh
# shellcheck shell=sh

echo "Installing dev tools to enable project management with oe-python-template and derivatives ..."

LINUX_APT_TOOLS=(
    "curl;curl;https://curl.se/"
)

BREW_TOOLS=(
    "uv;uv;https://docs.astral.sh/uv/"
    "git;git;https://git-scm.com/"
    "gpg;gnupg;https://gnupg.org/"
    "gmake;make;https://www.gnu.org/software/make/"
    "jq;jq;https://jqlang.org/"
    "xmllint;libxml2;https://en.wikipedia.org/wiki/Libxml2"
    "act;act;https://nektosact.com/"
    "pinact;pinact;https://github.com/suzuki-shunsuke/pinact"
)

MAC_BREW_TOOLS=(
    "pinentry-mac;pinentry-mac;https://github.com/GPGTools/pinentry"
)

LINUX_BREW_TOOLS=(
    # Linux-specific Homebrew tools will be added here
)

UV_TOOLS=(
    "copier;copier;https://copier.readthedocs.io/"
)

# Function to install/update brew tools
install_or_upgrade_brew_tool() {
    local tool=$1
    local package=$2
    local url=$3

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

    if command -v "$tool" &> /dev/null; then
        echo "$tool already installed at $(command -v "$tool"), skipping..."
    else
        echo "Installing $tool... # $url"
        sudo apt-get update -y && sudo apt-get install "$package" -y
    fi
}

# Function to install/update tools via uv
install_or_update_uv_tool() {
    local tool=$1
    local url=$3

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
        IFS=";" read -r tool package url <<< "$tool_entry"
        install_or_update_linux_apt_tool "$tool" "$package" "$url"
    done
fi

# Install/update Homebrew itself
if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew... # https://brew.sh/"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew already installed at $(command -v brew), updating..."
    brew update
fi

# Install/update Homebrew tools
for tool_entry in "${BREW_TOOLS[@]}"; do
    IFS=";" read -r tool package url <<< "$tool_entry"
    install_or_upgrade_brew_tool "$tool" "$package" "$url"
done

# Install/update Homebrew tools for macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    for tool_entry in "${MAC_BREW_TOOLS[@]}"; do
        IFS=";" read -r tool package url <<< "$tool_entry"
        install_or_upgrade_brew_tool "$tool" "$package" "$url"
    done
fi

# Install/update Homebrew tools for Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    for tool_entry in "${LINUX_BREW_TOOLS[@]}"; do
        IFS=";" read -r tool package url <<< "$tool_entry"
        install_or_upgrade_brew_tool "$tool" "$package" "$url"
    done
fi

# Install/update UV tools
for tool_entry in "${UV_TOOLS[@]}"; do
    IFS=";" read -r tool package url <<< "$tool_entry"
    install_or_update_uv_tool "$tool" "$url"
done
