#!/bin/bash

# --- Configuration ---
# Define the single deployment name and its namespace
DEPLOYMENT_NAME="grafana"
NAMESPACE="monitoring"

# --- Functions ---

# Function to get current replicas for the specified deployment
get_current_replicas() {
    # Use kubectl to get the current replicas, suppress errors if deployment not found
    kubectl get deployment "$DEPLOYMENT_NAME" -n "$NAMESPACE" -o=jsonpath='{.spec.replicas}' 2>/dev/null
}

# Function to display current deployment status for the specified deployment
display_status() {
    echo "--- Current Deployment Status for '$DEPLOYMENT_NAME' in Namespace '$NAMESPACE' ---"
    local current_replicas=$(get_current_replicas)

    if [ -z "$current_replicas" ]; then
        echo "Deployment '$DEPLOYMENT_NAME' not found or no replicas set in namespace '$NAMESPACE'."
        echo "Please ensure the deployment name is correct and it exists in the specified namespace."
        return 1 # Indicate an error or deployment not found
    else
        echo "Current replicas for '$DEPLOYMENT_NAME': $current_replicas"
    fi
    echo "------------------------------------------------------"
    echo ""
    return 0
}

# Function to scale the single deployment
scale_deployment() {
    local target_replicas=$1
    echo "Attempting to scale '$DEPLOYMENT_NAME' to $target_replicas replicas in namespace '$NAMESPACE'..."

    kubectl scale deployment "$DEPLOYMENT_NAME" --replicas="$target_replicas" -n "$NAMESPACE"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to scale '$DEPLOYMENT_NAME'."
        return 1
    fi

    echo "Successfully scaled '$DEPLOYMENT_NAME' to $target_replicas replicas."
    return 0
}

# --- Main Script Logic ---

clear # Clear the screen for a cleaner interface

echo "--- Kubernetes Deployment Scaler for '$DEPLOYMENT_NAME' ---"

# Display initial status for the chosen deployment
# Exit if the deployment is not found, as subsequent operations would fail
display_status
if [ $? -ne 0 ]; then
    exit 1
fi

# Present the menu to the user
echo "Please choose an action for deployment '$DEPLOYMENT_NAME':"
echo "1) Scale Up (increase replicas)"
echo "2) Scale Down (decrease replicas)"
echo "3) Scale Completely Down to 0 replicas"
echo ""

read -p "Enter your choice (1-3): " choice

case $choice in
    # Scale Up
    1)
        # Show current status again before asking for desired replicas
        display_status
        read -p "Enter the desired number of replicas to scale UP to: " desired_replicas
        if ! [[ "$desired_replicas" =~ ^[0-9]+$ ]] || [ "$desired_replicas" -lt 0 ]; then
            echo "Invalid input. Please enter a non-negative integer for replicas."
            exit 1
        fi
        scale_deployment "$desired_replicas"
        ;;
    # Scale Down
    2)
        # Show current status again before asking for desired replicas
        display_status
        read -p "Enter the desired number of replicas to scale DOWN to: " desired_replicas
        if ! [[ "$desired_replicas" =~ ^[0-9]+$ ]] || [ "$desired_replicas" -lt 0 ]; then
            echo "Invalid input. Please enter a non-negative integer for replicas."
            exit 1
        fi
        scale_deployment "$desired_replicas"
        ;;
    # Scale Completely Down to 0
    3)
        read -p "Are you sure you want to scale '$DEPLOYMENT_NAME' completely down to 0 replicas? (yes/no): " confirm_zero
        if [[ "$confirm_zero" == "yes" || "$confirm_zero" == "y" ]]; then
            scale_deployment 0
        else
            echo "Operation cancelled."
        fi
        ;;
    # Invalid choice
    *)
        echo "Invalid choice. Please enter a number between 1 and 3."
        exit 1
        ;;
esac

echo ""
# Display final status after the operation
display_status
