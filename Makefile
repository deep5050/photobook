# Makefile for Photobook Portfolio Generator

.PHONY: all build clean help

# Default target
all: clean build

backend:
	@echo "Starting backend..."
	python3 admin_server.py

# Build the app: compress images from RAW_IMAGES to images/ and generate index.html
build:
	@echo "Building photobook..."
	python3 generate.py

# Clean generated build artifacts (compressed images and index.html)
clean:
	@echo "Cleaning generated assets..."
	rm -rf images/thumbnails
	rm -f images/*.jpg images/*.jpeg images/*.png images/*.webp
	rm -f index.html

# Help target to display available commands
help:
	@echo "Available commands:"
	@echo "  make build  - Compress images from RAW_IMAGES to images/ and generate index.html"
	@echo "  make clean  - Remove generated images, thumbnails, and index.html"
	@echo "  make help   - Display this help message"
