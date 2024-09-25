#!/bin/bash
set -ex
set -o pipefail

export LC_ALL=C

if [ "$#" -ne 1 ]; then
   echo "Usage: $0 VERSION"
   echo "Version is the Chromium branch, e.g. 6738 for https://pdfium.googlesource.com/pdfium/+/refs/heads/chromium/6738"
   exit 2
fi

PDFIUM_VERSION="${1}"

# minimal download
# no V8, no skia
gclient config --unmanaged https://pdfium.googlesource.com/pdfium.git \
    --custom-var "checkout_configuration=minimal" \
    --custom-var "non_git_source=True" \
    --custom-var "checkout_rust=False" \

# clean
rm -rf pdfium

# nohooks to skip downloads of sysroot and llvm-build
gclient sync -r "pdfium@chromium/${PDFIUM_VERSION}" --no-history --shallow --reset --delete --nohooks

# unbundle ICU
rm -rf pdfium/third_party/icu
mkdir pdfium/third_party/icu
cp pdfium/build/linux/unbundle/icu.gn pdfium/third_party/icu/BUILD.gn

# add missing unbundle helper
# https://github.com/pypdfium2-team/pypdfium2/blob/main/setupsrc/pypdfium2_setup/build_pdfium.py
if [ ! -f pdfium/tools/generate_shim_headers/generate_shim_headers.py ]; then
    mkdir -p pdfium/tools/generate_shim_headers
    curl -L -o pdfium/tools/generate_shim_headers/generate_shim_headers.py \
        https://raw.githubusercontent.com/chromium/chromium/main/tools/generate_shim_headers/generate_shim_headers.py
fi

# record last commit and version
git -C pdfium/ log -1 > pdfium/COMMIT
echo "${PDFIUM_VERSION}" > pdfium/VERSION

# tar bundle
rm -f "pdfium-${PDFIUM_VERSION}.tar.gz"
tar -cf - \
    --transform "s/pdfium/libpdfium-${PDFIUM_VERSION}/" \
    --exclude-from excludes --anchored \
    --sort=name --format=posix \
    --pax-option=exthdr.name=%d/PaxHeaders/%f \
    --pax-option=delete=atime,delete=ctime \
    --clamp-mtime --mtime="${SOURCE_EPOCH:-0}" \
    --numeric-owner --owner=0 --group=0 \
    --mode=go+u,go-w \
    pdfium \
    | gzip --no-name --best > "libpdfium-${PDFIUM_VERSION}.tar.gz"
