#!/bin/bash
#
# Moroccan Legal AI Chatbot - Azure VM Initial Setup Script
#
# Run this ONCE on your Azure VM to set up the environment:
#   chmod +x vm-setup.sh && ./vm-setup.sh
#
# After running, log out and back in, then run:
#   cd /opt/moroccan-legal-ai && docker-compose up -d
#

set -e  # Exit on error

echo "=============================================="
echo "Moroccan Legal AI Chatbot - VM Setup"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/opt/moroccan-legal-ai"
GITHUB_REPO="https://github.com/ahmeddamouad/your_ai_lawyer.git"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Please don't run as root. Run as your normal user.${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Updating system...${NC}"
sudo apt update && sudo apt upgrade -y

echo -e "${YELLOW}Step 2: Installing Docker and dependencies...${NC}"
sudo apt install -y docker.io docker-compose git curl

echo -e "${YELLOW}Step 3: Adding user to docker group...${NC}"
sudo usermod -aG docker $USER

echo -e "${YELLOW}Step 4: Creating project directory...${NC}"
sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR

echo -e "${YELLOW}Step 5: Setting up 4GB swap space (critical for Ollama)...${NC}"
if [ -f /swapfile ]; then
    echo "Swap file already exists, skipping..."
else
    sudo fallocate -l 4G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo "Swap space created successfully"
fi
free -h

echo -e "${YELLOW}Step 6: Checking disk space...${NC}"
df -h /

echo ""
echo -e "${GREEN}=============================================="
echo "Basic setup complete!"
echo "=============================================="
echo ""
echo -e "${YELLOW}IMPORTANT: You must log out and log back in for docker permissions to work.${NC}"
echo ""
echo "Next steps:"
echo "1. Log out: exit"
echo "2. Log back in: ssh YOUR_USERNAME@YOUR_VM_IP"
echo "3. Clone your repo:"
echo "   cd $PROJECT_DIR"
echo "   git clone $GITHUB_REPO ."
echo ""
echo "4. Start Ollama and pull models:"
echo "   docker-compose up -d ollama"
echo "   docker exec legal-ollama ollama pull mistral"
echo "   docker exec legal-ollama ollama pull nomic-embed-text"
echo ""
echo "5. Start all services:"
echo "   docker-compose up -d"
echo ""
echo -e "6. Access your chatbot at: http://YOUR_VM_IP${NC}"
