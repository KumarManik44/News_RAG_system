import subprocess
import sys
import os
from pathlib import Path

def setup_production_environment():
    """Setup production environment for RAG system"""
    
    print("🚀 Setting up Production Environment...")
    
    # 1. Install production dependencies
    print("📦 Installing production dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    subprocess.run([sys.executable, "-m", "pip", "install", "psutil", "gunicorn"])
    
    # 2. Create production directories
    print("📁 Creating production directories...")
    Path("logs").mkdir(exist_ok=True)
    Path("data/backups").mkdir(parents=True, exist_ok=True)
    Path("monitoring/reports").mkdir(parents=True, exist_ok=True)
    
    # 3. Setup environment variables
    print("⚙️ Setting up environment...")
    env_content = """
# Production Environment Variables
ENVIRONMENT=production
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
WORKERS=4
MAX_REQUESTS=1000
BACKUP_ENABLED=true
MONITORING_ENABLED=true
"""
    
    with open(".env.prod", "w") as f:
        f.write(env_content)
    
    # 4. Create systemd service file (Linux)
    print("🔧 Creating service configuration...")
    service_content = f"""
[Unit]
Description=News RAG Summarizer API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory={os.getcwd()}
Environment=PATH={os.getcwd()}/venv/bin
ExecStart={sys.executable} -m gunicorn api.main:app -w 4 -b 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
"""
    
    with open("deploy/news-rag.service", "w") as f:
        f.write(service_content)
    
    # 5. Create backup script
    print("💾 Setting up backup system...")
    backup_script = """#!/bin/bash
# Backup script for News RAG System

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="data/backups"

# Backup database
cp news_articles.db "$BACKUP_DIR/news_articles_$DATE.db"

# Backup FAISS index
cp faiss_index.bin "$BACKUP_DIR/faiss_index_$DATE.bin"
cp faiss_metadata.pkl "$BACKUP_DIR/faiss_metadata_$DATE.pkl"

# Cleanup old backups (keep last 7 days)
find "$BACKUP_DIR" -name "*.db" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.bin" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.pkl" -mtime +7 -delete

echo "Backup completed: $DATE"
"""
    
    with open("deploy/backup.sh", "w") as f:
        f.write(backup_script)
    
    os.chmod("deploy/backup.sh", 0o755)
    
    print("✅ Production setup complete!")
    print("\nNext steps:")
    print("1. Copy news-rag.service to /etc/systemd/system/")
    print("2. Run: sudo systemctl enable news-rag")
    print("3. Run: sudo systemctl start news-rag")
    print("4. Add backup.sh to crontab for daily backups")

if __name__ == "__main__":
    setup_production_environment()
