#!/bin/bash
#
# Add 4GB swap space for low-memory VMs
# Run with: chmod +x add-swap.sh && sudo ./add-swap.sh
#
# Required for VMs with 4GB RAM or less to run Ollama with Mistral model
#

set -e

echo "Adding 4GB swap space..."

# Check if swap already exists
if [ -f /swapfile ]; then
    echo "Swap file already exists at /swapfile"
    echo "Current swap status:"
    free -h
    exit 0
fi

# Create swap file
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make persistent across reboots
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

echo ""
echo "Swap space created successfully!"
echo ""
free -h
