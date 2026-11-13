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
sudo apt-get update
sudo apt-get install --no-install-recommends -y curl gnupg2 jq xsltproc

# Install Trivy: one fixed release, checked against its SHA-256 before it goes on the PATH.
# Not from Aqua's apt repository: apt would install whatever version it resolves at job time.
# When Renovate bumps the version, update both checksums from trivy_<version>_checksums.txt of that release.
# renovate: datasource=github-releases depName=aquasecurity/trivy
TRIVY_VERSION=v0.76.1
case "$(uname -m)" in
    x86_64)
        trivy_arch="64bit"
        TRIVY_SHA256="c7cbe3137fb8a48a17574bede3dd6beb16742d1e9772929940fc90082c39d9c0" # trivy_0.76.1_Linux-64bit.tar.gz  # pragma: allowlist secret
        ;;
    aarch64 | arm64)
        trivy_arch="ARM64"
        TRIVY_SHA256="e174dff2a6dba5e3ae41f8d0537a6324405bd08132497340304c6b20e0f16a1f" # trivy_0.76.1_Linux-ARM64.tar.gz  # pragma: allowlist secret
        ;;
    *)
        echo "No Trivy checksum for architecture $(uname -m)" >&2
        exit 1
        ;;
esac
trivy_tmp="$(mktemp -d)"
trivy_tar="trivy_${TRIVY_VERSION#v}_Linux-${trivy_arch}.tar.gz"
curl --proto '=https' --tlsv1.2 -fsSL -o "${trivy_tmp}/${trivy_tar}" \
    "https://github.com/aquasecurity/trivy/releases/download/${TRIVY_VERSION}/${trivy_tar}"
echo "${TRIVY_SHA256}  ${trivy_tmp}/${trivy_tar}" | sha256sum --check --strict
tar -xzf "${trivy_tmp}/${trivy_tar}" -C "${trivy_tmp}" trivy
sudo install -m 0755 "${trivy_tmp}/trivy" /usr/local/bin/trivy
rm -rf "${trivy_tmp}"
trivy --version

# Install project specific tools
.github/workflows/_install_dev_tools_project.bash

log "Completed installation of development tools."
