# Seafile Kubernetes Deployment

A complete Kubernetes deployment configuration for Seafile, a self-hosted file synchronization and sharing platform. This setup provides a private cloud storage solution that you can run on your own infrastructure with SQLite backend and automated setup.

## Features

- Complete Seafile deployment with SQLite database backend
- Persistent local storage with configurable mount points
- Automated setup with configuration handling
- Secure credential management using Kubernetes Secrets
- External access via NodePort services
- Namespace isolation for clean organization
- Cloudflare Tunnel support for secure external access
- Support for custom domains

## Prerequisites

- Kubernetes cluster (tested on v1.20+)
- kubectl configured to access your cluster
- Local storage available on at least one node
- Sufficient storage space for your files (100Gi configured by default)

## Quick Start

### 1. Clone and Prepare
```bash
git clone <your-repo-url>
cd seafile-k8s
```

### 2. Create Directory Structure
On the node where you want to store data:
```bash
sudo mkdir -p /home/k8svolumes/seafile/mounted_volume/seafile
sudo chmod 777 /home/k8svolumes/seafile/mounted_volume/seafile
```

### 3. Configure

#### Update Configuration Files:

1. **Update domain/hostname** in `03-seafile-configmap.yaml`:
   ```yaml
   SEAFILE_SERVER_HOSTNAME: "seafile.yourdomain.com"
   SERVICE_URL: "https://seafile.yourdomain.com"
   ```

2. **Create admin credentials secret**:
   ```bash
   # Create 05-seafile-secret.yaml
   cat > 05-seafile-secret.yaml << EOF
   apiVersion: v1
   kind: Secret
   metadata:
     name: seafile-admin-secret
     namespace: seafile
   type: Opaque
   stringData:
     SEAFILE_ADMIN_EMAIL: "admin@seafile.local"
     SEAFILE_ADMIN_PASSWORD: "your-secure-password-here"  # CHANGE THIS!
   EOF
   ```

### 4. Deploy

Deploy all components:
```bash
# Apply all configurations in order
kubectl apply -f 00-seafile-ns.yaml
kubectl apply -f 01-seafile-pvc.yaml
kubectl apply -f 02-seafile-pv.yaml
kubectl apply -f 03-seafile-configmap.yaml
kubectl apply -f 04-seafile-initialrun-configmap.yaml
kubectl apply -f 05-seafile-deployment.yaml
kubectl apply -f 06-seafile-service.yaml
```

Or deploy all at once:
```bash
kubectl apply -f .
```

### 5. Verify Deployment
```bash
kubectl get pods -n seafile
kubectl get pvc -n seafile
kubectl get svc -n seafile
kubectl logs -f deployment/seafile -n seafile
```

## File Structure
```
.
├── README.md
├── 00-seafile-ns.yaml                    # Namespace definition
├── 01-seafile-pvc.yaml                   # Persistent Volume Claim
├── 02-seafile-pv.yaml                    # Persistent Volume
├── 03-seafile-configmap.yaml             # Seafile configuration
├── 04-seafile-initialrun-configmap.yaml  # Setup and startup script
├── 05-seafile-deployment.yaml            # Seafile deployment
└── 06-seafile-service.yaml               # NodePort services
```

## Configuration Details

### Storage Configuration
- **Seafile data**: `/home/k8svolumes/seafile/mounted_volume/seafile`
- **Storage size**: 100Gi (adjustable in PV/PVC)
- **Database**: SQLite3 (stored within Seafile data directory)

### Network Configuration
- **Seahub (Web Interface)**: Port 8000 → NodePort 31223
- **Fileserver**: Port 8082 → NodePort 31224

### Resource Limits
- **Memory**: 512Mi (request) / 1Gi (limit)
- **CPU**: 250m (request) / 500m (limit)

## Accessing Seafile

### Via NodePort (Direct Access)
```bash
# Get node IP
kubectl get nodes -o wide

# Access Seafile
http://NODE-IP:31223  # Web interface
http://NODE-IP:31224  # File server (for direct file access)
```

### Via Port Forwarding (Testing)
```bash
kubectl port-forward -n seafile svc/seafile 8080:8000
# Access at http://localhost:8080
```

### Via Cloudflare Tunnel (Production)
If using Cloudflare Tunnel, configure:
- `seafile.yourdomain.com` → `http://192.168.100.50:31223`
- `seafilefiles.yourdomain.com` → `http://192.168.100.50:31224`

**Note**: Cloudflare free plan limits file uploads to 100MB. For larger files, use direct access or upgrade your Cloudflare plan.

## First Login
- **URL**: `http://NODE-IP:31223` or `https://seafile.yourdomain.com`
- **Email**: Your configured admin email
- **Password**: Your configured admin password

**Important**: Change the admin password after first login!

## Automated Setup Features

The deployment includes automated setup that:
- Installs required packages (nano, sqlite3, net-tools)
- Detects and configures Seafile server directory
- Sets up SQLite database
- Configures Seahub to bind to all interfaces (0.0.0.0:8000)
- Creates admin account using provided credentials
- Configures custom domain settings and CSRF protection
- Monitors and automatically restarts services if they crash

## Troubleshooting

### Check Pod Status
```bash
kubectl get pods -n seafile
kubectl describe pod -n seafile <pod-name>
kubectl logs -f deployment/seafile -n seafile
```

### Access Container for Debugging
```bash
kubectl exec -it -n seafile deployment/seafile -- bash

# Check services
cd /opt/seafile/seafile-server-*
./seafile.sh status
./seahub.sh status

# Check network binding
netstat -tlnp | grep -E "(8000|8082)"

# Check configuration
cat /opt/seafile/conf/seahub_settings.py
cat /opt/seafile/conf/gunicorn.conf.py
```

### Common Issues

1. **Interface not accessible**: 
   - Ensure gunicorn is binding to 0.0.0.0:8000
   - Check `netstat -tlnp | grep 8000` shows `0.0.0.0:8000`

2. **Large file uploads fail**:
   - Cloudflare free plan limits to 100MB
   - Use direct IP access or port forwarding for larger files

3. **Pod keeps restarting**:
   - Check logs for errors
   - Ensure storage permissions are correct
   - Verify PV path exists on the node

4. **Login fails**:
   - Verify secret was created correctly
   - Check admin credentials in pod environment

## Maintenance

### Update Configuration
```bash
# Edit ConfigMap
kubectl edit configmap seafile-setup-script -n seafile

# Restart deployment
kubectl rollout restart deployment/seafile -n seafile
```

### Backup Strategy
```bash
# Scale down deployment
kubectl scale deployment seafile --replicas=0 -n seafile

# Backup data
sudo tar -czf seafile-backup-$(date +%Y%m%d).tar.gz /home/k8svolumes/seafile/mounted_volume/

# Scale back up
kubectl scale deployment seafile --replicas=1 -n seafile
```

### Update Seafile Version
Update the image tag in `06-seafile-deployment.yaml`:
```yaml
image: seafileltd/seafile-mc:latest  # or specific version
```

## Security Considerations

- Change default admin credentials immediately
- Use strong passwords
- Consider using HTTPS via Ingress or reverse proxy
- Restrict NodePort access via firewall rules
- Regularly backup your data
- Keep Seafile updated to latest stable version

## Large File Upload Solutions

Since Cloudflare free plan limits uploads to 100MB:

1. **Temporary Port Forward**:
   ```bash
   # Configure router to forward port 31223 to your node
   # Upload via http://YOUR-PUBLIC-IP:31223
   # Remove port forward when done
   ```

2. **kubectl Port Forward**:
   ```bash
   kubectl port-forward -n seafile svc/seafile 8888:8000
   # Upload via http://localhost:8888
   ```

3. **Tailscale VPN**:
   ```bash
   # Install Tailscale on your Kubernetes node
   curl -fsSL https://tailscale.com/install.sh | sh
   sudo tailscale up
   # Access via Tailscale IP without port forwarding
   ```

## Clean Uninstall
```bash
# Delete namespace (removes everything)
kubectl delete namespace seafile

# Clean up local storage
sudo rm -rf /home/k8svolumes/seafile/mounted_volume/*
```

## Support

- [Seafile Documentation](https://manual.seafile.com/)
- [Seafile Community Forum](https://forum.seafile.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

## License

This configuration is provided as-is. Seafile itself is licensed under its own terms - see the [Seafile website](https://www.seafile.com/) for details.

---

**Note**: This is a community-maintained deployment configuration and is not officially supported by Seafile Ltd.