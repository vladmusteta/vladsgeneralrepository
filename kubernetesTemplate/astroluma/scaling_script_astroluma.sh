#!/bin/bash

# Define the deployment names and namespace
DEPLOYMENT_SERVER="astroluma"
DEPLOYMENT_SECONDARY="astroluma-mongo"
NAMESPACE="dashboard"

# --- Functions ---

# Function to get current replicas for a given deployment
get_current_replicas() {
    local deployment_name=$1
    # Use kubectl to get the current replicas, suppress errors if deployment not found
    kubectl get deployment "$deployment_name" -n "$NAMESPACE" -o=jsonpath='{.spec.replicas}' 2>/dev/null
}

# Function to display current deployment status
display_status() {
    echo "--- Current Deployment Status in Namespace '$NAMESPACE' ---"
    local server_replicas=$(get_current_replicas "$DEPLOYMENT_SERVER")
    local redis_replicas=$(get_current_replicas "$DEPLOYMENT_SECONDARY")

    if [ -z "$server_replicas" ]; then
        echo "Deployment '$DEPLOYMENT_SERVER' not found or no replicas set."
    else
        echo "Current replicas for '$DEPLOYMENT_SERVER': $server_replicas"
    fi

    if [ -z "$redis_replicas" ]; then
        echo "Deployment '$DEPLOYMENT_SECONDARY' not found or no replicas set."
    else
        echo "Current replicas for '$DEPLOYMENT_SECONDARY': $redis_replicas"
    fi
    echo "------------------------------------------------------"
    echo ""
}

# Function to scale deployments
scale_deployments() {
    local target_replicas=$1
    echo "Attempting to scale '$DEPLOYMENT_SERVER' and '$DEPLOYMENT_SECONDARY' to $target_replicas replicas..."

    kubectl scale deployment "$DEPLOYMENT_SERVER" --replicas="$target_replicas" -n "$NAMESPACE"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to scale '$DEPLOYMENT_SERVER'."
        return 1
    fi

    kubectl scale deployment "$DEPLOYMENT_SECONDARY" --replicas="$target_replicas" -n "$NAMESPACE"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to scale '$DEPLOYMENT_SECONDARY'."
        return 1
    fi

    echo "Successfully scaled '$DEPLOYMENT_SERVER' and '$DEPLOYMENT_SECONDARY' to $target_replicas replicas."
    return 0
}

# --- Main Script Logic ---

clear # Clear the screen for a cleaner interface

# Display initial status
display_status

# Present the menu to the user
echo "Please choose an action:"
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
        read -p "Are you sure you want to scale both deployments completely down to 0 replicas? (yes/no): " confirm_zero
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
