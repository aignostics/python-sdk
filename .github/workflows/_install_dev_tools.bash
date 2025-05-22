#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status
set -o pipefail  # Return value of a pipeline is the value of the last command to exit with a non-zero status

# Log function for better debugging
log() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] $*"
}

log "Starting installation of development tools..."

wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install --no-install-recommends -y curl gnupg2 imagemagick jq trivy xsltproc

.github/workflows/_install_dev_tools_project.bash

log "Completed installation of development tools."
