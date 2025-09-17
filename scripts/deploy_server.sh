#!/bin/bash
# Deployment script for FastQCLI server

set -e  # Exit on any error

# Configuration
SERVER_USER="deploy"
SERVER_HOST="your-server.com"
SERVER_PATH="/var/www/fastqcli"
SSH_KEY_PATH="~/.ssh/id_rsa"

echo "=== FastQCLI Deployment Script ==="

# Check if running in GitHub Actions
if [ "$GITHUB_ACTIONS" = "true" ]; then
    echo "Running in GitHub Actions environment"
    # Use GitHub Actions secrets
    SERVER_USER="${{ secrets.SERVER_USER }}"
    SERVER_HOST="${{ secrets.SERVER_HOST }}"
    SERVER_PATH="${{ secrets.SERVER_PATH }}"
    SSH_KEY_PATH="${{ secrets.SSH_KEY_PATH }}"
else
    echo "Running in local environment"
    # Load from environment variables or config file
    if [ -f ".deploy_config" ]; then
        source .deploy_config
    fi
fi

# Validate configuration
if [ -z "$SERVER_USER" ] || [ -z "$SERVER_HOST" ] || [ -z "$SERVER_PATH" ]; then
    echo "ERROR: Missing deployment configuration"
    echo "Please set SERVER_USER, SERVER_HOST, and SERVER_PATH"
    exit 1
fi

echo "Deploying to: $SERVER_USER@$SERVER_HOST:$SERVER_PATH"

# Create deployment package
echo "Creating deployment package..."
DEPLOY_DIR="deploy_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$DEPLOY_DIR"

# Copy necessary files
cp -r fastqcli.py streamlit_*.py build_exe.py requirements*.txt run_streamlit.bat compile.bat "$DEPLOY_DIR/"
cp -r test_files "$DEPLOY_DIR/" 2>/dev/null || echo "No test files to copy"
cp -r README*.md QUICK_START_RU.md "$DEPLOY_DIR/"

# Create deployment script
cat > "$DEPLOY_DIR/deploy_remote.sh" << 'EOF'
#!/bin/bash
set -e

echo "=== Remote Deployment Script ==="

# Backup current version
if [ -d "fastqcli_backup" ]; then
    rm -rf fastqcli_backup
fi

if [ -d "fastqcli" ]; then
    mv fastqcli fastqcli_backup
    echo "Backup created"
fi

# Create new directory
mkdir -p fastqcli
cd fastqcli

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --user || echo "Warning: Could not install requirements.txt"
pip install -r requirements_exe.txt --user || echo "Warning: Could not install requirements_exe.txt"

# Install Sequali if not present
python -c "import sequali" 2>/dev/null || pip install sequali --user

# Test installation
echo "Testing installation..."
python -c "import fastqcli; print('FastQCLI imported successfully')"
python -c "import sequali; print('Sequali imported successfully')"

echo "Deployment completed successfully!"
echo "To run the application:"
echo "  cd fastqcli"
echo "  python fastqcli.py --help"
echo " streamlit run streamlit_simple.py"
EOF

chmod +x "$DEPLOY_DIR/deploy_remote.sh"

# Create archive
echo "Creating archive..."
tar -czf "${DEPLOY_DIR}.tar.gz" "$DEPLOY_DIR"

echo "Deployment package created: ${DEPLOY_DIR}.tar.gz"

# Deploy to server (if not in GitHub Actions - for local testing)
if [ "$GITHUB_ACTIONS" != "true" ]; then
    echo "Deploying to server..."
    
    # Copy archive to server
    scp -i "$SSH_KEY_PATH" "${DEPLOY_DIR}.tar.gz" "$SERVER_USER@$SERVER_HOST:$SERVER_PATH/"
    
    # Extract and run deployment script on server
    ssh -i "$SSH_KEY_PATH" "$SERVER_USER@$SERVER_HOST" "
        cd $SERVER_PATH &&
        tar -xzf ${DEPLOY_DIR}.tar.gz &&
        cd $DEPLOY_DIR &&
        bash deploy_remote.sh
    "
    
    echo "Deployment completed!"
    echo "Application is now running on $SERVER_HOST"
fi

# Cleanup
rm -rf "$DEPLOY_DIR" "${DEPLOY_DIR}.tar.gz"

echo "=== Deployment Finished ==="