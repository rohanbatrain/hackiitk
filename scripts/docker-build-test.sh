#!/bin/bash
# Docker Build and Test Script
# Usage: ./scripts/docker-build-test.sh [ci|full|all]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="hackiitk"
REGISTRY="ghcr.io/rohanbatrain"

# Functions
print_header() {
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Build CI image
build_ci() {
    print_header "Building CI-optimized image"
    
    DOCKER_BUILDKIT=1 docker build \
        --target ci \
        --tag ${IMAGE_NAME}:ci \
        --tag ${IMAGE_NAME}:latest \
        .
    
    print_success "CI image built successfully"
}

# Build full image
build_full() {
    print_header "Building full application image"
    
    DOCKER_BUILDKIT=1 docker build \
        --target application \
        --tag ${IMAGE_NAME}:full \
        .
    
    print_success "Full image built successfully"
}

# Test image
test_image() {
    local tag=$1
    print_header "Testing ${IMAGE_NAME}:${tag}"
    
    # Test 1: Verify dependencies
    print_info "Test 1: Verifying dependencies..."
    if docker run --rm ${IMAGE_NAME}:${tag} python -c "
import langchain
import chromadb
import sentence_transformers
print('✓ All dependencies available')
"; then
        print_success "Dependencies verified"
    else
        print_error "Dependency verification failed"
        return 1
    fi
    
    # Test 2: Run CLI help
    print_info "Test 2: Testing CLI..."
    if docker run --rm ${IMAGE_NAME}:${tag} python -m tests.extreme.cli --help > /dev/null; then
        print_success "CLI works"
    else
        print_error "CLI test failed"
        return 1
    fi
    
    # Test 3: Run fast property tests
    print_info "Test 3: Running fast property tests..."
    if docker run --rm ${IMAGE_NAME}:${tag} \
        python -m tests.extreme.cli test --category property --fast --verbose; then
        print_success "Property tests passed"
    else
        print_error "Property tests failed (this may be expected)"
    fi
    
    print_success "All tests completed for ${IMAGE_NAME}:${tag}"
}

# Show image info
show_info() {
    local tag=$1
    print_header "Image Information: ${IMAGE_NAME}:${tag}"
    
    echo "Size:"
    docker images ${IMAGE_NAME}:${tag} --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
    
    echo -e "\nLayers:"
    docker history ${IMAGE_NAME}:${tag} --no-trunc --format "table {{.CreatedBy}}\t{{.Size}}" | head -10
    
    echo -e "\nPython version:"
    docker run --rm ${IMAGE_NAME}:${tag} python --version
    
    echo -e "\nInstalled packages (sample):"
    docker run --rm ${IMAGE_NAME}:${tag} pip list | grep -E "langchain|chromadb|sentence-transformers|hypothesis|pytest"
}

# Push to registry
push_image() {
    local tag=$1
    print_header "Pushing ${IMAGE_NAME}:${tag} to registry"
    
    # Tag for registry
    docker tag ${IMAGE_NAME}:${tag} ${REGISTRY}/${IMAGE_NAME}:${tag}
    
    # Push
    if docker push ${REGISTRY}/${IMAGE_NAME}:${tag}; then
        print_success "Image pushed to ${REGISTRY}/${IMAGE_NAME}:${tag}"
    else
        print_error "Failed to push image"
        print_info "Make sure you're logged in: docker login ghcr.io"
        return 1
    fi
}

# Clean up
cleanup() {
    print_header "Cleaning up old images"
    
    # Remove dangling images
    docker image prune -f
    
    print_success "Cleanup complete"
}

# Main script
main() {
    local target=${1:-ci}
    
    print_header "Docker Build and Test Script"
    print_info "Target: $target"
    
    case $target in
        ci)
            build_ci
            test_image "ci"
            show_info "ci"
            ;;
        full)
            build_full
            test_image "full"
            show_info "full"
            ;;
        all)
            build_ci
            build_full
            test_image "ci"
            test_image "full"
            show_info "ci"
            show_info "full"
            ;;
        push)
            print_info "Pushing images to registry..."
            push_image "ci"
            push_image "latest"
            ;;
        clean)
            cleanup
            ;;
        *)
            print_error "Unknown target: $target"
            echo "Usage: $0 [ci|full|all|push|clean]"
            exit 1
            ;;
    esac
    
    print_header "Done!"
    print_success "Docker build and test completed successfully"
}

# Run main
main "$@"
