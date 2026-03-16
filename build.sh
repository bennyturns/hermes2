#!/bin/bash
# Hermes - Container Build Script

set -e

# Configuration
IMAGE_NAME="${IMAGE_NAME:-quay.io/redhat-et/hermes}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
BUILD_CONTEXT="${BUILD_CONTEXT:-.}"

echo "=================================================="
echo "Building Hermes Container Image"
echo "=================================================="
echo "Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "Context: ${BUILD_CONTEXT}"
echo ""

# Detect container runtime (podman preferred, fallback to docker)
if command -v podman &> /dev/null; then
    RUNTIME="podman"
elif command -v docker &> /dev/null; then
    RUNTIME="docker"
else
    echo "❌ Error: Neither podman nor docker found"
    exit 1
fi

echo "Using container runtime: ${RUNTIME}"
echo ""

# Build the image
echo "Building image..."
${RUNTIME} build \
    --tag "${IMAGE_NAME}:${IMAGE_TAG}" \
    --file Containerfile \
    --label "build.date=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
    --label "build.version=${IMAGE_TAG}" \
    --label "vcs.ref=$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" \
    ${BUILD_CONTEXT}

echo ""
echo "✅ Build complete: ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""

# Show image info
echo "Image information:"
${RUNTIME} images "${IMAGE_NAME}:${IMAGE_TAG}"

echo ""
echo "=================================================="
echo "Next steps:"
echo "=================================================="
echo "1. Test locally:"
echo "   ${RUNTIME} run -p 8000:8000 ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""
echo "2. Push to registry:"
echo "   ${RUNTIME} push ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""
echo "3. Deploy to OpenShift:"
echo "   oc apply -k k8s/"
echo "=================================================="
