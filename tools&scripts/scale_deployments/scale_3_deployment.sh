#!/bin/bash

# --- Configuration ---
# Define the deployment names individually and their namespace
DEPLOYMENT_1="immich-database"
DEPLOYMENT_2="immich-machine-learnin"
DEPLOYMENT_3="immich-server"
NAMESPACE="photos-videos"

# --- Functions ---

# Function to get current replicas for a given deployment
get_current_replicas() {
    local deployment_name=$1
    # Use kubectl to get the current replicas, suppress errors if deployment not found
    kubectl get deployment "$deployment_name" -n "$NAMESPACE" -o=jsonpath='{.spec.replicas}' 2>/dev/null
}

# Function to display current deployment status for all defined deployments
display_status() {
    echo "--- Current Deployment Status in Namespace '$NAMESPACE' ---"

    # Display status for each individual deployment
    local current_replicas_1=$(get_current_replicas "$DEPLOYMENT_1")
    if [ -z "$current_replicas_1" ]; then
        echo "Deployment '$DEPLOYMENT_1' not found or no replicas set."
    else
        echo "Current replicas for '$DEPLOYMENT_1': $current_replicas_1"
    fi

    local current_replicas_2=$(get_current_replicas "$DEPLOYMENT_2")
    if [ -z "$current_replicas_2" ]; then
        echo "Deployment '$DEPLOYMENT_2' not found or no replicas set."
    else
        echo "Current replicas for '$DEPLOYMENT_2': $current_replicas_2"
    fi

    local current_replicas_3=$(get_current_replicas "$DEPLOYMENT_3")
    if [ -z "$current_replicas_3" ]; then
        echo "Deployment '$DEPLOYMENT_3' not found or no replicas set."
    else
        echo "Current replicas for '$DEPLOYMENT_3': $current_replicas_3"
    fi

    echo "------------------------------------------------------"
    echo ""
}

# Function to scale all defined deployments
scale_deployments() {
    local target_replicas=$1
    echo "Attempting to scale all Immich deployments to $target_replicas replicas..."

    local success=0 # Flag to track overall success

    # Scale each individual deployment
    echo "Scaling '$DEPLOYMENT_1' to $target_replicas replicas..."
    kubectl scale deployment "$DEPLOYMENT_1" --replicas="$target_replicas" -n "$NAMESPACE"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to scale '$DEPLOYMENT_1'."
        success=1
    fi

    echo "Scaling '$DEPLOYMENT_2' to $target_replicas replicas..."
    kubectl scale deployment "$DEPLOYMENT_2" --replicas="$target_replicas" -n "$NAMESPACE"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to scale '$DEPLOYMENT_2'."
        success=1
    fi

    echo "Scaling '$DEPLOYMENT_3' to $target_replicas replicas..."
    kubectl scale deployment "$DEPLOYMENT_3" --replicas="$target_replicas" -n "$NAMESPACE"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to scale '$DEPLOYMENT_3'."
        success=1
    fi

    if [ "$success" -eq 0 ]; then
        echo "Successfully scaled all Immich deployments to $target_replicas replicas."
        return 0
    else
        echo "Warning: One or more deployments failed to scale successfully."
        return 1
    fi
}

# --- Main Script Logic ---

clear # Clear the screen for a cleaner interface

echo "--- Kubernetes Immich Deployment Scaler ---"

# Display initial status for all Immich deployments
display_status

# Present the menu to the user
echo "Please choose an action for Immich deployments:"
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
        scale_deployments "$desired_replicas"
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
        scale_deployments "$desired_replicas"
        ;;
    # Scale Completely Down to 0
    3)
        read -p "Are you sure you want to scale all Immich deployments completely down to 0 replicas? (yes/no): " confirm_zero
        if [[ "$confirm_zero" == "yes" || "$confirm_zero" == "y" ]]; then
            scale_deployments 0
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
