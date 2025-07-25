#!/bin/bash

# Script to scale down RetroArch deployment to 0 replicas
# This will shut down the RetroArch pod but preserve all data

echo "🎮 Scaling down RetroArch deployment..."

# Scale down the deployment
kubectl scale deployment retroarch -n retroarch --replicas=0

# Check the status
if [ $? -eq 0 ]; then
    echo "✅ RetroArch deployment scaled down successfully!"
    echo ""
    echo "Current status:"
    kubectl get deployment retroarch -n retroarch
    echo ""
    echo "📊 GPU resources are now available for other workloads"
else
    echo "❌ Failed to scale down RetroArch deployment"
    exit 1
fi

# Optional: Show pod termination progress
echo ""
echo "⏳ Waiting for pod to terminate..."
kubectl wait --for=delete pod -l app=retroarch -n retroarch --timeout=60s 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ RetroArch pod terminated successfully"
else
    echo "ℹ️  Pod already terminated or timeout reached"
fi

echo ""
echo "💾 Your RetroArch data is preserved in: /home/k8svolumes/retroarch/mounted_volume"
echo "🔄 To start RetroArch again, run: ./retroarch-scale-up.sh"