
# Essential Kubernetes `kubectl` Commands

----------

### **1. Get Information About Resources**

These are your primary commands for seeing what's running in your cluster.

-   `kubectl get <resource>`: The most common command. Lists resources.
    
    -   `kubectl get pods`
        
    -   `kubectl get deployments`
        
    -   `kubectl get services`
        
    -   `kubectl get all` (lists common resources like pods, services, and deployments)
        
    -   `kubectl get pods -n kube-system` (specifies a namespace)
        
-   `kubectl describe <resource> <name>`: Provides a detailed, multi-line view of a specific resource. This is crucial for debugging.
    
    -   `kubectl describe pod my-app-pod-xyz`
        

----------

### **2. Manage Deployments and Scaling**

These commands are essential for deploying and managing applications.

-   `kubectl apply -f <file.yaml>`: The standard way to create or update resources from a YAML file.
    
-   `kubectl delete -f <file.yaml>`: Deletes the resources defined in a YAML file.
    
-   `kubectl scale deployment <deployment-name> --replicas=<number>`: Adjusts the number of replicas for a deployment.
    
    -   `kubectl scale deployment my-app --replicas=3`
        
-   `kubectl rollout status deployment <deployment-name>`: Tracks the progress of a deployment update.
    
-   `kubectl rollout undo deployment <deployment-name>`: Rolls back a deployment to its previous version.
    

----------

### **3. Interacting with Pods**

These commands are vital for debugging and inspecting running applications.

-   `kubectl logs <pod-name>`: Fetches the logs from a pod's container.
    
    -   `kubectl logs <pod-name> -f` (streams logs in real-time)
        
-   `kubectl exec -it <pod-name> -- bash`: Gets an interactive shell inside a running container. Use `sh` if `bash` isn't available.
    
-   `kubectl port-forward <pod-name> <local-port>:<container-port>`: Forwards a local port to a port on a pod, allowing you to access a service running inside the cluster.
    

----------

### **4. Advanced and Troubleshooting**

These are powerful commands for more complex tasks.

-   `kubectl patch <resource> <name> -p '<JSON_PATCH>'`: Applies a specific patch to a resource without needing to modify the full YAML.
    
    -   `kubectl patch deployment my-app -p '{"spec":{"template":{"spec":{"containers":[{"name":"my-container","image":"nginx:1.21"}]}}}}'`
        
-   `kubectl edit <resource> <name>`: Opens a live resource in your text editor for direct modification.
    
-   `kubectl top pod`: Shows the CPU and memory usage of pods. (Requires the **Metrics Server** to be installed).