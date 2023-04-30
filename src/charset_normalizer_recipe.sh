#!/usr/bin/env bash

set -e

VERSION="2.0.1"
REVISION="1"
MODULE_NAME="charset_normalizer"
PYTHON_VERSION="3.8"
HOST_PLATFORM="$(uname | tr '[:upper:]' '[:lower:]')"
MODULE_PLATFORM="manylinux1_x86_64"
MODULE_DIR="${HOME}/.local/share/python-for-android/build/charset_normalizer"

# Download and extract the module source code
wget "https://files.pythonhosted.org/packages/${MODULE_PLATFORM:0:7}/${MODULE_NAME}-${VERSION}-${REVISION}.${MODULE_PLATFORM:8}.tar.gz" -O "${MODULE_NAME}-${VERSION}.tar.gz"
tar xvf "${MODULE_NAME}-${VERSION}.tar.gz"
cd "${MODULE_NAME}-${VERSION}"

# Build and install the ARM64 version of the module
MODULE_ARCH="arm64-v8a"
MODULE_TAG="${MODULE_PLATFORM}_${MODULE_ARCH}"
"${PYTHON_VERSION}/bin/python3" setup.py install --root="${MODULE_DIR}_${MODULE_ARCH}" --prefix=""
cd "${MODULE_DIR}_${MODULE_ARCH}/usr/local"
tar czvf "${MODULE_NAME}-${VERSION}-${REVISION}.${MODULE_TAG}.tar.gz" *
cp "${MODULE_NAME}-${VERSION}-${REVISION}.${MODULE_TAG}.tar.gz" "${HOME}/Documents/myapp/.buildozer/android/platform/build-arm64-v8a/dists/${MODULE_NAME}-${VERSION}-${REVISION}.${MODULE_TAG}.tar.gz"

# Build and install the ARMv7 version of the module
MODULE_ARCH="armeabi-v7a"
MODULE_TAG="${MODULE_PLATFORM}_${MODULE_ARCH}"
"${PYTHON_VERSION}/bin/python3" setup.py install --root="${MODULE_DIR}_${MODULE_ARCH}" --prefix=""
cd "${MODULE_DIR}_${MODULE_ARCH}/usr/local"
tar czvf "${MODULE_NAME}-${VERSION}-${REVISION}.${MODULE_TAG}.tar.gz" *
cp "${MODULE_NAME}-${VERSION}-${REVISION}.${MODULE_TAG}.tar.gz" "${HOME}/Documents/myapp/.buildozer/android/platform/build-armeabi-v7a/dists/${MODULE_NAME}-${VERSION}-${REVISION}.${MODULE_TAG}.tar.gz"
