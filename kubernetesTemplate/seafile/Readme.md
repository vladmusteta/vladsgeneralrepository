# Seafile Kubernetes Deployment

A complete Kubernetes deployment configuration for [Seafile](https://www.seafile.com/), a self-hosted file synchronization and sharing platform. This setup provides a Google Drive alternative that you can run on your own infrastructure.

## Features

- **Complete Seafile deployment** with MySQL database backend
- **Persistent local storage** with configurable mount points
- **Easy start/stop scripts** for maintenance and resource management
- **Ingress configuration** for external access
- **Namespace isolation** for clean organization
- **Production-ready** with health checks and resource limits

## Prerequisites

- Kubernetes cluster (tested on v1.20+)
- `kubectl` configured to access your cluster
- Ingress controller (nginx recommended)
- Local storage available on at least one node
- Sufficient storage space for your files

## Quick Start

### 1. Clone and Prepare

```bash
git clone <your-repo-url>
cd seafile-k8s
```

### 2. Create Directory Structure

On the node where you want to store data:

```bash
sudo mkdir -p /home/k8svolumes/seafile/mounted_volume/mysql
sudo mkdir -p /home/k8svolumes/seafile/mounted_volume/seafile
sudo chown -R 999:999 /home/k8svolumes/seafile/mounted_volume/mysql
sudo chown -R 8000:8000 /home/k8svolumes/seafile/mounted_volume/seafile
```

### 3. Configure

**Required changes before deployment:**

1. **Update node names** in `seafile-mysql-pv.yaml` and `seafile-pv.yaml`:
   ```bash
   kubectl get nodes  # Get your node name
   # Replace "your-node-name" with actual node name
   ```

2. **Generate new passwords** for `mysql-secret.yaml`:
   ```bash
   echo -n "your-mysql-root-password" | base64
   echo -n "your-seafile-db-password" | base64
   ```

3. **Update configuration** in `seafile-configmap.yaml`:
   - Change `SEAFILE_ADMIN_EMAIL`
   - Change `SEAFILE_ADMIN_PASSWORD`
   - Update `SEAFILE_SERVER_HOSTNAME` to your domain
   - Ensure passwords match those in the secret

4. **Configure ingress** in `seafile-ingress.yaml`:
   - Change host to your domain
   - Adjust ingress class if needed
   - Enable TLS if desired

### 4. Deploy

```bash
# Deploy in order
kubectl apply -f namespace.yaml
kubectl apply -f seafile-mysql-pv.yaml
kubectl apply -f seafile-pv.yaml
kubectl apply -f seafile-mysql-pvc.yaml
kubectl apply -f seafile-pvc.yaml
kubectl apply -f mysql-secret.yaml
kubectl apply -f mysql-deployment.yaml
kubectl apply -f mysql-service.yaml
kubectl apply -f seafile-configmap.yaml
kubectl apply -f seafile-deployment.yaml
kubectl apply -f seafile-service.yaml
kubectl apply -f seafile-ingress.yaml
```

### 5. Verify Deployment

```bash
kubectl get pods -n seafile
kubectl get pvc -n seafile
kubectl get ingress -n seafile
```

## Management Scripts

### Start/Stop Seafile

Make scripts executable:
```bash
chmod +x start-seafile.sh stop-seafile.sh
```

Stop Seafile (scales to 0 replicas):
```bash
./stop-seafile.sh
```

Start Seafile (scales to 1 replica):
```bash
./start-seafile.sh
```

These scripts are useful for:
- Maintenance windows
- Saving resources when not in use
- Clean restarts

## File Structure

```
.
├── README.md
├── namespace.yaml              # Seafile namespace
├── seafile-mysql-pv.yaml      # MySQL persistent volume
├── seafile-mysql-pvc.yaml     # MySQL persistent volume claim
├── mysql-secret.yaml          # Database credentials
├── mysql-deployment.yaml      # MySQL database deployment
├── mysql-service.yaml         # MySQL service
├── seafile-pv.yaml           # Seafile persistent volume
├── seafile-pvc.yaml          # Seafile persistent volume claim
├── seafile-configmap.yaml    # Seafile configuration
├── seafile-deployment.yaml   # Seafile application deployment
├── seafile-service.yaml      # Seafile service
├── seafile-ingress.yaml      # External access configuration
├── start-seafile.sh          # Start script
└── stop-seafile.sh           # Stop script
```

## Configuration Details

### Storage Configuration

- **MySQL data**: `/home/k8svolumes/seafile/mounted_volume/mysql`
- **Seafile data**: `/home/k8svolumes/seafile/mounted_volume/seafile`
- **Default MySQL storage**: 10Gi
- **Default Seafile storage**: 100Gi

Adjust storage sizes in the PV and PVC files as needed.

### Resource Limits

- **MySQL**: 512Mi-1Gi RAM, 250m-500m CPU
- **Seafile**: 1Gi-2Gi RAM, 500m-1000m CPU

Modify in the deployment files based on your cluster capacity.

### Network Configuration

- **Seafile HTTP**: Port 80
- **Seafile HTTPS**: Port 443
- **MySQL**: Port 3306 (internal only)

## Accessing Seafile

1. **Via Ingress**: Access through your configured hostname
2. **Via Port Forward** (for testing):
   ```bash
   kubectl port-forward -n seafile svc/seafile 8080:80
   # Access at http://localhost:8080
   ```

### First Login

- **URL**: Your configured hostname or localhost:8080
- **Email**: As configured in `SEAFILE_ADMIN_EMAIL`
- **Password**: As configured in `SEAFILE_ADMIN_PASSWORD`

**Important**: Change the admin password after first login!

## Troubleshooting

### Check Pod Status
```bash
kubectl get pods -n seafile
kubectl describe pod <pod-name> -n seafile
kubectl logs <pod-name> -n seafile
```

### Check Storage
```bash
kubectl get pv
kubectl get pvc -n seafile
```

### Common Issues

1. **Pods stuck in Pending**: Check node affinity and storage availability
2. **Seafile won't start**: Ensure MySQL is ready first
3. **Permission errors**: Verify directory ownership on the host
4. **Database connection issues**: Check passwords match between secret and configmap

### Reset Everything
```bash
kubectl delete namespace seafile
# Clean up local directories if needed
sudo rm -rf /home/k8svolumes/seafile/mounted_volume/*
```

## Security Considerations

- Change all default passwords before production use
- Use TLS/HTTPS in production (configure in ingress)
- Consider using sealed secrets or external secret management
- Regularly backup your data directory
- Keep Seafile updated to latest stable version

## Backup Strategy

Your data is stored in `/home/k8svolumes/seafile/mounted_volume/`. To backup:

```bash
# Stop Seafile first
./stop-seafile.sh

# Backup data
sudo tar -czf seafile-backup-$(date +%Y%m%d).tar.gz /home/k8svolumes/seafile/mounted_volume/

# Start Seafile
./start-seafile.sh
```

## Contributing

Feel free to submit issues and pull requests to improve this deployment configuration.

## License

This configuration is provided as-is. Seafile itself is licensed under its own terms - see the [Seafile website](https://www.seafile.com/) for details.

## Support

- [Seafile Documentation](https://manual.seafile.com/)
- [Seafile Community Forum](https://forum.seafile.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

---

**Note**: This is a community-maintained deployment configuration and is not officially supported by Seafile Ltd.