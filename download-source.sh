#!/bin/bash
set -ex
set -o pipefail

TAG="libpdfium"
PDFIUM_VERSION=$(rpmspec -q --qf "%{version}\n" libpdfium.spec | head -n1 | awk -F^ '{print $1}')

podman build -f "download-source/Containerfile" -t "${TAG}" "download-source"
podman run -ti --rm --security-opt label=disable -v ./download-source:/work:z ${TAG} \
    ./fetch-pdfium.sh "${PDFIUM_VERSION}"

mv "download-source/libpdfium-${PDFIUM_VERSION}.tar.gz" .
