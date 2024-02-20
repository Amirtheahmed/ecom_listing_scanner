# Define variables
IMAGE_NAME := listing_scanner
TAG := 1.0
DOCKER_USERNAME := acme
MACHINE_MAC ?= false

# You can override the variables from the command line:
# make build IMAGE_NAME=myimage TAG=v1 MACHINE_MAC=true

.PHONY: build push

# Build Docker image
build:
	@echo "Building Docker image $(IMAGE_NAME):$(TAG) for MACHINE_MAC=$(MACHINE_MAC)"
	@if [ "$(MACHINE_MAC)" = "true" ]; then \
		echo "Using Docker buildx"; \
		docker buildx build --platform linux/amd64 -t $(DOCKER_USERNAME)/$(IMAGE_NAME):$(TAG) --load . ; \
	else \
		echo "Using standard Docker build"; \
		docker build -t $(DOCKER_USERNAME)/$(IMAGE_NAME):$(TAG) . ; \
	fi

# Push Docker image to the repository
push:
	@echo "Pushing Docker image $(IMAGE_NAME):$(TAG) to Docker Hub"
	@docker push $(DOCKER_USERNAME)/$(IMAGE_NAME):$(TAG)

# Build and push Docker image
release: build push