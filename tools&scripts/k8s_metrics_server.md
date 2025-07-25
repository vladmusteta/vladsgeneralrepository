# Simple Metrics Server Installation with Helm

This guide shows you how to quickly install `metrics-server` in your Kubernetes cluster using Helm.

## Steps

Follow these commands in your terminal:

### 1. Add the Metrics Server Helm Repository

```bash
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
```

### 2. Update Your Helm Repositories

```bash
helm repo update```

### 3.Create a Custom Values File
This file configures `metrics-server` with specific arguments and port settings.
```bash
cat > metrics-server-values.yaml << EOF
# Completely override default args
defaultArgs: []

# Set our custom args
args:
  - --cert-dir=/tmp
  - --secure-port=4443
  - --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname
  - --kubelet-use-node-status-port
  - --metric-resolution=15s
  - --kubelet-insecure-tls

# Set correct container port
containerPort: 4443

# Set service ports
service:
  port: 443
  targetPort: 4443

# Override probe configurations
livenessProbe:
  httpGet:
    path: /livez
    port: 4443
    scheme: HTTPS
  initialDelaySeconds: 0
  periodSeconds: 10
  timeoutSeconds: 1
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /readyz
    port: 4443
    scheme: HTTPS
  initialDelaySeconds: 20
  periodSeconds: 10
  timeoutSeconds: 1
  failureThreshold: 3

# Resource settings
resources:
  requests:
    cpu: 100m
    memory: 200Mi
EOF
```
### 4. Install or Upgrade Metrics Server
```bash
helm upgrade --install metrics-server metrics-server/metrics-server \ --namespace kube-system \ --values metrics-server-values.yaml
```

### Then, you can use 