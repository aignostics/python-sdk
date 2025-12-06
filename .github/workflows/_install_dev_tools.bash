#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status
set -o pipefail  # Return value of a pipeline is the value of the last command to exit with a non-zero status

# Log function for better debugging
log() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] $*"
    return 0
}

log "Starting installation of development tools..."

# Disable man-db updates to speed up package installation
sudo rm -f /var/lib/man-db/auto-update

# Install APT packages
# Use signed-by to add GPG key securely (apt-key is deprecated)
mkdir -p /etc/apt/keyrings
wget --secure-protocol=TLSv1_2 --max-redirect=0 -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor | sudo tee /etc/apt/keyrings/trivy.gpg > /dev/null
echo "deb [signed-by=/etc/apt/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install --no-install-recommends -y curl gnupg2 jq trivy xsltproc

# Install further tools not project specific
# Download Sentry CLI securely: enforce HTTPS, disable redirects
wget --secure-protocol=TLSv1_2 --max-redirect=0 -qO - https://sentry.io/get-cli/ | SENTRY_CLI_VERSION="2.57.0" sh

# Install project specific tools
.github/workflows/_install_dev_tools_project.bash

log "Completed installation of development tools."
