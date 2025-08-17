#!/usr/bin/env python3
"""
TEF AI Practice Tool - Production Deployment Script
Handles production deployment and configuration
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TEFDeployer:
    """Production deployment manager for TEF AI Practice Tool."""
    
    def __init__(self, environment="production"):
        self.environment = environment
        self.project_root = Path(__file__).parent
        self.deploy_dir = self.project_root / "deploy"
        
    def check_prerequisites(self):
        """Check if all prerequisites are met."""
        logger.info("🔍 Checking deployment prerequisites...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            logger.error("❌ Python 3.8+ is required")
            return False
        logger.info(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check required files
        required_files = [
            "main.py", "models.py", "auth.py", "prompt.py", 
            "requirements.txt", "index.html"
        ]
        
        for file in required_files:
            if not (self.project_root / file).exists():
                logger.error(f"❌ Required file missing: {file}")
                return False
        logger.info("✅ All required files present")
        
        # Check environment file
        env_file = self.project_root / ".env"
        if not env_file.exists():
            logger.warning("⚠️  .env file not found - will create from template")
            self.create_env_file()
        
        return True
    
    def create_env_file(self):
        """Create production environment file."""
        try:
            env_template = self.project_root / "config.env"
            env_file = self.project_root / ".env"
            
            if env_template.exists():
                shutil.copy2(env_template, env_file)
                logger.info("✅ Created .env file from template")
                
                # Update with production settings
                self.update_env_production()
            else:
                logger.error("❌ config.env template not found")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to create .env file: {e}")
            return False
    
    def update_env_production(self):
        """Update .env file with production settings."""
        try:
            env_file = self.project_root / ".env"
            
            # Read current content
            with open(env_file, 'r') as f:
                content = f.read()
            
            # Update for production
            content = content.replace("DEBUG=true", "DEBUG=false")
            content = content.replace("HOST=0.0.0.0", "HOST=0.0.0.0")
            content = content.replace("ENVIRONMENT=development", "ENVIRONMENT=production")
            
            # Write updated content
            with open(env_file, 'w') as f:
                f.write(content)
            
            logger.info("✅ Updated .env file for production")
            
        except Exception as e:
            logger.error(f"❌ Failed to update .env file: {e}")
    
    def install_dependencies(self):
        """Install production dependencies."""
        logger.info("📦 Installing production dependencies...")
        
        try:
            # Upgrade pip
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                         check=True, capture_output=True)
            
            # Install requirements
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                         check=True, capture_output=True)
            
            logger.info("✅ Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install dependencies: {e}")
            return False
    
    def run_database_migrations(self):
        """Run database migrations."""
        logger.info("🗄️  Running database migrations...")
        
        try:
            subprocess.run([sys.executable, "migrations.py", "migrate"], 
                         check=True, capture_output=True)
            logger.info("✅ Database migrations completed")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Database migrations failed: {e}")
            return False
    
    def create_production_config(self):
        """Create production configuration files."""
        logger.info("⚙️  Creating production configuration...")
        
        try:
            # Create gunicorn config
            gunicorn_config = self.project_root / "gunicorn.conf.py"
            with open(gunicorn_config, 'w') as f:
                f.write(self.get_gunicorn_config())
            
            # Create systemd service file
            service_file = self.project_root / "tef-evaluator.service"
            with open(service_file, 'w') as f:
                f.write(self.get_systemd_service())
            
            # Create nginx config
            nginx_config = self.project_root / "nginx.conf"
            with open(nginx_config, 'w') as f:
                f.write(self.get_nginx_config())
            
            logger.info("✅ Production configuration files created")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create production config: {e}")
            return False
    
    def get_gunicorn_config(self):
        """Get Gunicorn configuration content."""
        return '''# Gunicorn configuration for TEF AI Practice Tool
import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Logging
accesslog = "/var/log/tef-evaluator/access.log"
errorlog = "/var/log/tef-evaluator/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "tef-evaluator"

# Server mechanics
daemon = False
pidfile = "/var/run/tef-evaluator.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = None

# SSL (uncomment for HTTPS)
# keyfile = "/etc/ssl/private/tef-evaluator.key"
# certfile = "/etc/ssl/certs/tef-evaluator.crt"
'''
    
    def get_systemd_service(self):
        """Get systemd service file content."""
        return f'''[Unit]
Description=TEF AI Practice Tool
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory={self.project_root}
Environment=PATH={self.project_root}/venv/bin
ExecStart={self.project_root}/venv/bin/gunicorn -c gunicorn.conf.py main:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
'''
    
    def get_nginx_config(self):
        """Get Nginx configuration content."""
        return '''# Nginx configuration for TEF AI Practice Tool
server {
    listen 80;
    server_name your-domain.com;  # Update with your domain
    
    # Redirect HTTP to HTTPS (uncomment when SSL is configured)
    # return 301 https://$server_name$request_uri;
    
    # For now, serve HTTP
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Static files (if serving from Nginx)
    location /static/ {
        alias /path/to/your/static/files/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}

# HTTPS configuration (uncomment when SSL is configured)
# server {
#     listen 443 ssl http2;
#     server_name your-domain.com;
#     
#     ssl_certificate /etc/ssl/certs/tef-evaluator.crt;
#     ssl_certificate_key /etc/ssl/private/tef-evaluator.key;
#     
#     # SSL configuration
#     ssl_protocols TLSv1.2 TLSv1.3;
#     ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
#     ssl_prefer_server_ciphers off;
#     
#     # Same location blocks as above
#     location / {
#         proxy_pass http://127.0.0.1:8000;
#         # ... same proxy settings
#     }
# }
'''
    
    def create_virtual_environment(self):
        """Create virtual environment for production."""
        logger.info("🐍 Creating virtual environment...")
        
        try:
            venv_path = self.project_root / "venv"
            
            if venv_path.exists():
                logger.info("ℹ️  Virtual environment already exists")
                return True
            
            # Create virtual environment
            subprocess.run([sys.executable, "-m", "venv", "venv"], 
                         check=True, capture_output=True)
            
            logger.info("✅ Virtual environment created")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to create virtual environment: {e}")
            return False
    
    def install_production_dependencies(self):
        """Install dependencies in virtual environment."""
        logger.info("📦 Installing production dependencies in virtual environment...")
        
        try:
            venv_pip = self.project_root / "venv" / "bin" / "pip"
            
            # Upgrade pip
            subprocess.run([str(venv_pip), "install", "--upgrade", "pip"], 
                         check=True, capture_output=True)
            
            # Install requirements
            subprocess.run([str(venv_pip), "install", "-r", "requirements.txt"], 
                         check=True, capture_output=True)
            
            # Install production server
            subprocess.run([str(venv_pip), "install", "gunicorn"], 
                         check=True, capture_output=True)
            
            logger.info("✅ Production dependencies installed")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install production dependencies: {e}")
            return False
    
    def run_tests(self):
        """Run application tests."""
        logger.info("🧪 Running application tests...")
        
        try:
            # Start server in background
            server_process = subprocess.Popen([sys.executable, "run.py"], 
                                           stdout=subprocess.PIPE, 
                                           stderr=subprocess.PIPE)
            
            # Wait for server to start
            import time
            time.sleep(5)
            
            # Run tests
            test_result = subprocess.run([sys.executable, "test_app.py"], 
                                       capture_output=True, text=True)
            
            # Stop server
            server_process.terminate()
            server_process.wait()
            
            if test_result.returncode == 0:
                logger.info("✅ All tests passed")
                return True
            else:
                logger.error(f"❌ Tests failed: {test_result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Test execution failed: {e}")
            return False
    
    def create_log_directories(self):
        """Create log directories."""
        logger.info("📁 Creating log directories...")
        
        try:
            log_dir = Path("/var/log/tef-evaluator")
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Set permissions
            subprocess.run(["sudo", "chown", "www-data:www-data", str(log_dir)], 
                         check=True, capture_output=True)
            subprocess.run(["sudo", "chmod", "755", str(log_dir)], 
                         check=True, capture_output=True)
            
            logger.info("✅ Log directories created")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create log directories: {e}")
            return False
    
    def deploy(self):
        """Run complete deployment process."""
        logger.info("🚀 Starting TEF AI Practice Tool deployment...")
        logger.info("=" * 60)
        
        # Check prerequisites
        if not self.check_prerequisites():
            logger.error("❌ Prerequisites check failed")
            return False
        
        # Create virtual environment
        if not self.create_virtual_environment():
            logger.error("❌ Virtual environment creation failed")
            return False
        
        # Install production dependencies
        if not self.install_production_dependencies():
            logger.error("❌ Production dependencies installation failed")
            return False
        
        # Run database migrations
        if not self.run_database_migrations():
            logger.error("❌ Database migrations failed")
            return False
        
        # Create production configuration
        if not self.create_production_config():
            logger.error("❌ Production configuration creation failed")
            return False
        
        # Create log directories
        if not self.create_log_directories():
            logger.error("❌ Log directory creation failed")
            return False
        
        # Run tests
        if not self.run_tests():
            logger.error("❌ Tests failed")
            return False
        
        logger.info("=" * 60)
        logger.info("🎉 Deployment completed successfully!")
        logger.info("=" * 60)
        logger.info("📋 Next steps:")
        logger.info("1. Update nginx.conf with your domain")
        logger.info("2. Copy nginx.conf to /etc/nginx/sites-available/")
        logger.info("3. Enable the site: sudo ln -s /etc/nginx/sites-available/tef-evaluator /etc/nginx/sites-enabled/")
        logger.info("4. Copy tef-evaluator.service to /etc/systemd/system/")
        logger.info("5. Enable and start the service: sudo systemctl enable tef-evaluator")
        logger.info("6. Restart nginx: sudo systemctl restart nginx")
        logger.info("=" * 60)
        
        return True

def main():
    """Main deployment function."""
    if len(sys.argv) > 1:
        environment = sys.argv[1]
    else:
        environment = "production"
    
    deployer = TEFDeployer(environment)
    
    if deployer.deploy():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
