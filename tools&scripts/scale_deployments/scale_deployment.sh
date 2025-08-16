#!/bin/bash

# --- Global Variables ---
DEPLOYMENTS=()
NAMESPACE=""

# --- Functions ---

# Function to get current replicas for a given deployment
get_current_replicas() {
    local deployment_name=$1
    kubectl get deployment "$deployment_name" -n "$NAMESPACE" -o=jsonpath='{.spec.replicas}' 2>/dev/null
}

# Function to display current deployment status for all deployments
display_status() {
    echo "--- Current Deployment Status in Namespace '$NAMESPACE' ---"
    
    for deployment in "${DEPLOYMENTS[@]}"; do
        local current_replicas=$(get_current_replicas "$deployment")
        if [ -z "$current_replicas" ]; then
            echo "Deployment '$deployment' not found or no replicas set."
        else
            echo "Current replicas for '$deployment': $current_replicas"
        fi
    done
    
    echo "------------------------------------------------------"
    echo ""
}

# Function to scale all deployments
scale_deployments() {
    local target_replicas=$1
    echo "Attempting to scale all deployments to $target_replicas replicas..."

    local success=0 # Flag to track overall success

    for deployment in "${DEPLOYMENTS[@]}"; do
        echo "Scaling '$deployment' to $target_replicas replicas..."
        kubectl scale deployment "$deployment" --replicas="$target_replicas" -n "$NAMESPACE"
        if [ $? -ne 0 ]; then
            echo "Error: Failed to scale '$deployment'."
            success=1
        fi
    done

    if [ "$success" -eq 0 ]; then
        echo "Successfully scaled all deployments to $target_replicas replicas."
        return 0
    else
        echo "Warning: One or more deployments failed to scale successfully."
        return 1
    fi
}

# Function to collect deployment information from user
collect_deployment_info() {
    # Get namespace
    echo "--- Setup Configuration ---"
    read -p "Enter the Kubernetes namespace: " NAMESPACE
    if [ -z "$NAMESPACE" ]; then
        echo "Error: Namespace cannot be empty."
        exit 1
    fi

    # Get number of deployments
    read -p "How many deployments do you want to scale? " num_deployments
    if ! [[ "$num_deployments" =~ ^[1-9][0-9]*$ ]]; then
        echo "Error: Please enter a positive integer for number of deployments."
        exit 1
    fi

    # Collect deployment names
    echo ""
    echo "Enter the deployment names:"
    for ((i=1; i<=num_deployments; i++)); do
        read -p "Deployment $i name: " deployment_name
        if [ -z "$deployment_name" ]; then
            echo "Error: Deployment name cannot be empty."
            exit 1
        fi
        DEPLOYMENTS+=("$deployment_name")
    done

    echo ""
    echo "Configuration Summary:"
    echo "Namespace: $NAMESPACE"
    echo "Deployments to manage:"
    for ((i=0; i<${#DEPLOYMENTS[@]}; i++)); do
        echo "  $((i+1)). ${DEPLOYMENTS[i]}"
    done
    echo ""
    
    read -p "Is this configuration correct? (yes/no): " confirm
    if [[ "$confirm" != "yes" && "$confirm" != "y" ]]; then
        echo "Configuration cancelled. Please restart the script."
        exit 0
    fi
}

# --- Main Script Logic ---

clear # Clear the screen for a cleaner interface

echo "=== Dynamic Kubernetes Deployment Scaler ==="
echo ""

# Collect deployment information from user
collect_deployment_info

# Display initial status for all deployments
display_status

# Present the menu to the user
echo "Please choose an action for the deployments:"
echo "1) Scale Up (increase replicas)"
echo "2) Scale Down (decrease replicas)"
echo "3) Scale Completely Down to 0 replicas"
echo "4) Set Custom Replica Count"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    # Scale Up
    1)
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
        echo "Current deployments that will be scaled to 0:"
        for deployment in "${DEPLOYMENTS[@]}"; do
            echo "  - $deployment"
        done
        echo ""
        read -p "Are you sure you want to scale all deployments completely down to 0 replicas? (yes/no): " confirm_zero
        if [[ "$confirm_zero" == "yes" || "$confirm_zero" == "y" ]]; then
            scale_deployments 0
        else
            echo "Operation cancelled."
        fi
        ;;
    # Set Custom Replica Count
    4)
        display_status
        read -p "Enter the desired number of replicas: " desired_replicas
        if ! [[ "$desired_replicas" =~ ^[0-9]+$ ]] || [ "$desired_replicas" -lt 0 ]; then
            echo "Invalid input. Please enter a non-negative integer for replicas."
            exit 1
        fi
        scale_deployments "$desired_replicas"
        ;;
    # Invalid choice
    *)
        echo "Invalid choice. Please enter a number between 1 and 4."
        exit 1
        ;;
esac

echo ""
# Display final status after the operation
display_status

echo "Operation completed. Thank you for using the Dynamic Kubernetes Deployment Scaler!"
