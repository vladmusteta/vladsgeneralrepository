#!/bin/bash

# Script to scale down deployments in the romm namespace

echo "Scaling down deployments in the 'romm' namespace..."

# Scale down mariadb deployment
echo "Scaling down mariadb deployment to 0 replicas..."
kubectl scale deployment mariadb --replicas=0 -n romm

# Check if the previous command was successful
if [ $? -eq 0 ]; then
    echo "✓ mariadb deployment scaled down successfully"
else
    echo "✗ Failed to scale down mariadb deployment"
    exit 1
fi

# Scale down romm deployment
echo "Scaling down romm deployment to 0 replicas..."
kubectl scale deployment romm --replicas=0 -n romm

# Check if the previous command was successful
if [ $? -eq 0 ]; then
    echo "✓ romm deployment scaled down successfully"
else
    echo "✗ Failed to scale down romm deployment"
    exit 1
fi

echo "Both deployments have been scaled down to 0 replicas."
echo "To verify, run: kubectl get deployments -n romm"
