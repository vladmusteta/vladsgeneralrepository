
# Simple Linux Swap File Setup

This guide shows you how to quickly create and enable a 4GB swap file in Linux.

## Steps

Follow these commands in your terminal:

### 1. Create a 4GB file for swap

```bash
sudo fallocate -l 4G /swapfile

```

### 2. Set file permissions

```bash
sudo chmod 600 /swapfile

```

### 3. Format the file as swap

```bash
sudo mkswap /swapfile

```

### 4. Activate the swap file

```bash
sudo swapon /swapfile
```

### 5. Make swap permanent across reboots

```bash
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

```

That's it! Your 4GB swap file is now active and will persist after reboots.