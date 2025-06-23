# External Eval API Kubernetes Deployment

A Kubernetes-deployed API service for external evaluations, accessible through Cloudflare tunnel and worker.

## Overview

This project containerizes an external evaluation API and deploys it to Kubernetes with Cloudflare integration for secure external access.

## Files Included

- `Dockerfile` - Container configuration for the API service
- `external-eval-api.js` - Main API application logic
- `views/challenge.html` - Challenge page template
- `views/access_required.html` - Access control page template
- `kubernetes/` - Kubernetes deployment manifests
- `cloudflare-worker.js` - Cloudflare worker for routing/middleware

## Deployment Steps

### 1. Application Development
Created the core API service and web interface:
- Built `external-eval-api.js` with the main API endpoints using `nano external-eval-api.js`
- Initialized Node.js project: `npm init -y`  # Create package.json with default settings
- Installed dependencies: `npm install express cookie-parser`  # Add web server and cookie handling
- Designed HTML templates for user-facing pages (`challenge.html`, `access_required.html`)

### 2. Containerization
- Wrote `Dockerfile` to package the application
- Configured appropriate base image and dependencies

#### Docker Testing & Deployment
Local testing:
```bash
docker build -t external-eval-api:latest .  # Build container image from Dockerfile
docker run -p 3000:3000 external-eval-api:latest  # Run container and map port 3000
docker ps  # List currently running containers
docker stop CONTAINER_NAME  # Stop the running container after testing
```

Push to Docker Hub:
```bash
docker login  # Authenticate with Docker Hub credentials
docker tag external-eval-api:latest vladko2050/external-eval-api:latest  # Tag image for registry
docker push vladko2050/external-eval-api:latest  # Upload image to Docker Hub
```

### 3. Kubernetes Setup
- Created Kubernetes YAML manifests for deployment and services
- Applied configurations to cluster

### 4. Cloudflare Integration
- Verified no existing Cloudflare tunnel conflicts
- Created public hostname `pdf-internal.vladsdomain` in Cloudflare tunnel
- Implemented `cloudflare-worker.js` for external routing and access control
- Configured worker route with custom domain `pdf.vladsdomain`

## Usage

### Challenge Configuration

Update challenge questions, answers, retry limits, and timeout settings:

```bash
./updateChallenge.sh
```

This runs `node setup-challenge.js` to dynamically modify challenge parameters.

### Docker Deployment

Build and deploy new container versions:

```bash
./updateDocker.sh
```

This script:
- Builds the Docker image: `docker build -t vladko2050/external-eval-api:latest .`
- Pushes to registry: `docker push vladko2050/external-eval-api:latest`
- Restarts Kubernetes deployment: `kubectl rollout restart deployment/external-eval-api -n external-eval`

## Architecture

API Service → Kubernetes Pod → Cloudflare Tunnel → Cloudflare Worker → External Access

## Notes

- Ensure Cloudflare tunnel configuration doesn't conflict with existing tunnels
- Worker handles routing and access control before requests reach the API