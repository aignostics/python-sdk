#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status
set -o pipefail # Return value of a pipeline is the value of the last command to exit with a non-zero status

# Log function for better debugging
log() {
echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] $*"
}

log "Starting installation of development tools specific to Aignostics Python SDK..."

# Add your project specific installation commands below
# sudo apt-get install --no-install-recommends -y YOUR_PACKAGE
sudo apt-get install --no-install-recommends -y p7zip-rar

log "Completed installation of development tools specific to Aignostics Python SDK."
