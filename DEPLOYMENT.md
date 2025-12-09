# Icon Manager Deployment Guide

This guide provides detailed steps for packaging and deploying the Icon Manager application to other devices. Two deployment methods are supported: Docker container deployment and traditional direct Python deployment.

## 1. Project Preparation

### 1.1 Check Project Structure

Ensure your project directory contains the following files and folders:

```
icon_store/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies list
├── templates/          # HTML templates folder
├── static/             # Static resources folder
│   ├── css/            # Style files
│   └── icons/          # Icons storage directory
├── data/               # Data storage directory
├── Dockerfile          # Docker build file
├── docker-compose.yml  # Docker Compose configuration
├── start-docker.bat    # Docker startup script (Windows)
├── run-local.bat       # Local run script (Windows)
└── DEPLOYMENT.md       # Deployment guide (this document)
```

### 1.2 Environment Requirements

**Docker Deployment**:
- Docker Engine 19.03 or higher
- Docker Compose (optional but recommended)

**Python Deployment**:
- Python 3.6 or higher (Python 3.9-3.11 recommended)
- pip package manager

## 2. Docker Container Deployment (Recommended)

The Docker deployment method provides better environment isolation and consistency, and is recommended for production environments or cross-platform deployments.

### 2.1 Deploy with Docker Compose (Easiest Method)

1. Ensure Docker and Docker Compose are installed on the target device

2. Copy the entire project to any directory on the target device

3. Enter the project directory and run the following command to start the service:

   **Windows**:
   ```
   start-docker.bat
   ```
   
   **Linux/macOS**:
   ```bash
   chmod +x start-docker.sh  # If start-docker.sh file exists
   ./start-docker.sh
   ```
   
   Or run manually:
   ```bash
   docker-compose up -d
   ```

4. After the application starts, access it in your browser: `http://localhost:5000`

### 2.2 Manual Docker Deployment

1. Build Docker image:
   ```bash
   docker build -t icon-manager .
   ```

2. Run Docker container:
   ```bash
   docker run -d -p 5000:5000 --name icon-manager \
     -v $(pwd)/static/icons:/app/static/icons \
     -e SECRET_KEY=your_secure_secret_key_here \
     icon-manager
   ```

3. Access the application: `http://localhost:5000`

### 2.3 Data Persistence

Docker deployment is configured with volume mapping to ensure icon data is stored on the host machine and won't be lost when the container restarts:
- Host path: `./static/icons`
- Container path: `/app/static/icons`

## 3. Traditional Python Deployment

If Docker cannot be installed on the target device, you can deploy using the traditional Python method.

### 3.1 Using Startup Script (Windows)

1. Ensure Python 3.6 or higher is installed on the target device

2. Copy the entire project to the target device

3. Double-click to run the `run-local.bat` script

4. The script will automatically:
   - Check Python environment
   - Install necessary dependencies
   - Create required directory structure
   - Start the application

5. Access the application: `http://localhost:5000`

### 3.2 Manual Python Deployment

1. Create necessary directory structure:
   ```bash
   mkdir -p static/icons/Uncategorized templates data
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set environment variables:
   
   **Windows**:
   ```
   set FLASK_APP=app.py
   set FLASK_ENV=development  # Use production for production environment
   set SECRET_KEY=your_secure_secret_key_here
   set ICON_STORAGE_PATH=./static/icons
   ```
   
   **Linux/macOS**:
   ```bash
   export FLASK_APP=app.py
   export FLASK_ENV=development  # Use production for production environment
   export SECRET_KEY=your_secure_secret_key_here
   export ICON_STORAGE_PATH=./static/icons
   ```

4. Start the application:
   ```bash
   python app.py
   ```

## 4. Production Environment Deployment Recommendations

### 4.1 Docker Production Environment Configuration

1. Modify environment variables in docker-compose.yml:
   - Change `SECRET_KEY` to a strong random value
   - Set `FLASK_ENV=production`

2. Consider using a reverse proxy (such as Nginx) to handle HTTPS and request routing

3. Regularly back up the `./static/icons` directory to prevent data loss

### 4.2 Python Production Environment Configuration

1. Use a production-grade WSGI server such as Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -b 0.0.0.0:5000 app:app
   ```

2. Set appropriate environment variables:
   - `FLASK_ENV=production`
   - Secure `SECRET_KEY`

3. Configure system services (such as systemd) to ensure the application starts automatically after system restarts

## 5. Common Problems and Solutions

### 5.1 Port Occupancy Issues

- If port 5000 is already in use, you can modify the port mapping in the startup script or Docker configuration
- Example: `docker run -p 8080:5000 ...` maps host port 8080 to container port 5000

### 5.2 Permission Issues

- Docker deployment: Ensure the mounted volume directory has the correct permissions
- Python deployment: Use the `--user` option to install dependencies, or use a virtual environment

### 5.3 Dependency Installation Failures

- Check network connection
- Consider using a local mirror source, for example:
  ```bash
  pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
  ```

### 5.4 Database Initialization Failures

The application will automatically fall back to file system storage mode, which doesn't affect basic functionality. If you need persistent category data, ensure the `data` directory exists and is writable.

## 6. Maintenance and Updates

### 6.1 Updating the Application

**Docker Deployment**:
1. Pull the latest code
2. Rebuild the image: `docker-compose build`
3. Restart the service: `docker-compose up -d`

**Python Deployment**:
1. Update code files
2. Reinstall dependencies (if changed): `pip install -r requirements.txt`
3. Restart the application

### 6.2 Data Backup

Regularly back up the following directories:
- `./static/icons`: All uploaded icon files
- `./data`: Category and other data information

---

## 7. Cross-Platform Deployment Notes

### 7.1 Windows to Linux Deployment

- Line ending conversion: Use the Git command `git config --global core.autocrlf input` to ensure file line endings display correctly on Linux
- Script permissions: Before running on Linux, add execute permissions to shell scripts: `chmod +x *.sh`

### 7.2 Linux to Windows Deployment

- Use Windows version startup scripts (`.bat` files)
- Note the differences in file path separators

---

After deployment is complete, the Icon Manager should run normally on the target device, and you can access the application interface through a browser and use all features.
