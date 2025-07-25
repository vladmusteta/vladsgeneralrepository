#!/bin/bash

# Script to scale up RetroArch deployment to 1 replica
# This will start the RetroArch pod with all preserved data

echo "🎮 Scaling up RetroArch deployment..."

# Scale up the deployment
kubectl scale deployment retroarch -n retroarch --replicas=1

# Check the status
if [ $? -eq 0 ]; then
    echo "✅ RetroArch deployment scaled up successfully!"
    echo ""
    echo "Current status:"
    kubectl get deployment retroarch -n retroarch
    echo ""
else
    echo "❌ Failed to scale up RetroArch deployment"
    exit 1
fi

# Wait for pod to be ready
echo "⏳ Waiting for RetroArch pod to be ready..."
kubectl wait --for=condition=ready pod -l app=retroarch -n retroarch --timeout=120s

if [ $? -eq 0 ]; then
    echo "✅ RetroArch pod is ready!"
    echo ""
    
    # Get pod name and show GPU allocation
    POD_NAME=$(kubectl get pods -n retroarch -l app=retroarch -o jsonpath='{.items[0].metadata.name}')
    echo "📦 Pod name: $POD_NAME"
    
    # Check GPU allocation
    echo ""
    echo "🎯 Checking GPU allocation..."
    kubectl exec -n retroarch $POD_NAME -- nvidia-smi 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ GPU successfully allocated to RetroArch"
    else
        echo "⚠️  Could not verify GPU allocation (this might be normal during startup)"
    fi
    
    # Get node and access information
    NODE_NAME=$(kubectl get pod $POD_NAME -n retroarch -o jsonpath='{.spec.nodeName}')
    NODE_IP=$(kubectl get node $NODE_NAME -o jsonpath='{.status.addresses[?(@.type=="InternalIP")].address}')
    
    echo ""
    echo "🌐 RetroArch is now accessible at:"
    echo "   HTTP:  http://$NODE_IP:31082"
    echo "   HTTPS: https://$NODE_IP:31083"
    echo ""
    echo "📝 Note: HTTPS uses a self-signed certificate"
    echo "🎮 First time with GPU? Right-click desktop and re-launch RetroArch"
else
    echo "❌ Pod failed to become ready within timeout"
    echo ""
    echo "🔍 Check pod status:"
    kubectl get pods -n retroarch
    echo ""
    echo "📋 Check pod logs:"
    echo "kubectl logs -n retroarch -l app=retroarch"
fi