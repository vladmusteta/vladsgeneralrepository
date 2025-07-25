#!/bin/bash

# Script to scale up deployments in the romm namespace

echo "Scaling up deployments in the 'romm' namespace..."

# Scale up mariadb deployment
echo "Scaling up mariadb deployment to 1 replica..."
kubectl scale deployment mariadb --replicas=1 -n romm

# Check if the previous command was successful
if [ $? -eq 0 ]; then
    echo "✓ mariadb deployment scaled up successfully"
else
    echo "✗ Failed to scale up mariadb deployment"
    exit 1
fi

# Scale up romm deployment
echo "Scaling up romm deployment to 1 replica..."
kubectl scale deployment romm --replicas=1 -n romm

# Check if the previous command was successful
if [ $? -eq 0 ]; then
    echo "✓ romm deployment scaled up successfully"
else
    echo "✗ Failed to scale up romm deployment"
    exit 1
fi

echo "Both deployments have been scaled up to 1 replica."
echo "To verify, run: kubectl get deployments -n romm"
