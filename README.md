# icon_library

<p align="center">
  <img src="https://img.shields.io/badge/version-v0.1.10-blue.svg">
  <img src="https://img.shields.io/badge/license-MIT-green.svg">
  <img src="https://img.shields.io/badge/technology-Flask%20%2B%20Vanilla%20JS-blue.svg">
  <img src="https://img.shields.io/badge/docker-ready-blue.svg">
</p>

## Project Introduction

icon_library is a web application based on a separated front-end and back-end architecture, designed for managing and distributing various icon resources. The system supports icon uploading, category management, search and download functions, and is suitable for unified management of icon resources within teams.

## Author Information

- **Development Background**: I developed this software using AI tools because I found it difficult to manage icons when using sun-panel ([https://github.com/hslr-s/sun-panel](https://github.com/hslr-s/sun-panel))

## System Architecture

### Separated Front-end and Back-end Architecture

The project adopts a modern separated front-end and back-end architecture:

- **Back-end**: RESTful API service built with Python Flask framework
- **Front-end**: Single-page application built with vanilla JavaScript, HTML5, and CSS3
- **Data Storage**: Supports multiple databases like SQLite, MySQL, PostgreSQL
- **File Storage**: Local file system for storing icon resources

### Directory Structure

```
icon_library/
├── backend/               # Back-end application
│   ├── app/               # Main application module
│   │   ├── api/           # API routing layer
│   │   ├── models/        # Data model layer
│   │   ├── services/      # Business logic layer
│   │   ├── utils/         # Utility functions
│   │   ├── middlewares/   # Middlewares
│   │   ├── config.py      # Configuration file
│   │   └── __init__.py    # Application initialization
│   ├── uploads/           # Upload file storage directory
│   ├── app.py             # Application entry
│   ├── init_db.py         # Database initialization script
│   ├── requirements.txt   # Python dependencies
│   ├── .env               # Environment variables
│   └── .env.example       # Environment variables example
├── frontend/              # Front-end application
│   ├── public/            # Static resources
│   ├── src/               # Source code
│   │   ├── api/           # API communication module
│   │   ├── components/    # Components
│   │   ├── styles/        # CSS styles
│   │   ├── utils/         # Utility functions
│   │   └── main.js        # Main script
│   ├── index.html         # Entry HTML
│   └── package.json       # NPM configuration
├── start.bat              # Windows startup script
├── start.sh               # Linux/Mac startup script
└── README.md              # Project documentation
```

### Core Features

1. **Complete Separation of Front-end and Back-end**
   - Backend provides RESTful API interfaces
   - Frontend fetches data through AJAX calls
   - Supports Cross-Origin Resource Sharing (CORS)

2. **Modular Design**
   - Backend adopts MVC architectural pattern
   - Layered design: API layer, service layer, data access layer
   - Easy to extend and maintain

3. **Complete Functionality**
   - Icon uploading, previewing, downloading
   - Category management
   - User authentication
   - Responsive design

## Docker Deployment

### Environment Requirements

- **Docker**: 18.09+
- **Docker Compose**: 1.25+

### Quick Deployment

#### Using Docker Compose

1. Ensure Docker and Docker Compose are installed
2. Execute in the project root directory:

```bash
# Windows
start.bat

# Linux/Mac
chmod +x start.sh
./start.sh
```

Or directly use Docker Compose command:

```bash
docker-compose up -d
```

3. Visit http://localhost:5000

### Docker Configuration Description

The project has optimized Docker image building with the following main features:

- **Multi-stage Build**: Reduces the final image size
- **Domestic Mirror Source Support**: Solves network connection issues
- **Alpine Base Image**: Lighter runtime environment
- **Resource Limitations**: CPU and memory usage restrictions
- **Log Optimization**: Limits log size and quantity

### Custom Configuration

You can customize Docker configuration by modifying the following files:

- `Dockerfile`: Container image build configuration
- `docker-compose.yml`: Container orchestration configuration
- `.dockerignore`: Specify files to ignore during build

### Image Optimization

The project has implemented the following Docker image optimization measures:

- Using Alpine base image, reducing image size by approximately 80%
- Adopting multi-stage build to separate build and runtime environments
- Using virtual environments to isolate Python dependencies
- Removing unnecessary build dependencies
- Consolidating RUN commands to reduce image layers
- Using lightweight waitress server instead of gunicorn

Detailed optimization information can be found in the `DOCKER_OPTIMIZATION.md` file.

## Quick Start

### Environment Requirements

- **Python**: 3.7+
- **Node.js**: 12.x+
- **Browser**: Chrome, Firefox, Safari, Edge and other modern browsers

### One-click Startup

#### Windows System

1. Ensure Docker and Python are installed
2. Double-click to run the `start.bat` script
3. Access http://localhost:5000 in the browser

#### Linux/Mac System

1. Ensure Docker and Python are installed
2. Set script execution permissions: `chmod +x start.sh`
3. Run the script: `./start.sh`
4. Access http://localhost:5000 in the browser

### Manual Installation

#### Backend Installation

```bash
cd backend

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env file, set database connection and other parameters

# Initialize database
python init_db.py

# Start backend service
python app.py
```

#### Frontend Installation

```bash
cd frontend

# Install dependencies
npm install

# Start development mode
npm run dev

# Or build production version
npm run build
```

## API Documentation

### Icon-related Interfaces

- `GET /api/icons` - Get icon list
- `GET /api/icons/:id` - Get single icon information
- `POST /api/icons` - Upload new icon
- `DELETE /api/icons/:id` - Delete icon
- `GET /api/icons/files/:filename` - Download icon file

### Category-related Interfaces

- `GET /api/categories` - Get all categories
- `POST /api/categories` - Create new category
- `DELETE /api/categories/:id` - Delete category

### Authentication-related Interfaces

- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/status` - Get login status

## Configuration Instructions

### Backend Configuration

The main configuration file is `.env`, which can set the following environment variables:

- `FLASK_APP` - Flask application entry
- `FLASK_ENV` - Running environment (development/production)
- `FLASK_DEBUG` - Debug mode
- `FLASK_HOST` - Host address
- `FLASK_PORT` - Port number
- `SECRET_KEY` - Application secret key
- `SQLALCHEMY_DATABASE_URI` - Database connection URI
- `ICON_STORAGE_PATH` - Icon storage path
- `MAX_CONTENT_LENGTH` - Maximum upload file size
- `AUTH_USERNAME` - Authentication username
- `AUTH_PASSWORD` - Authentication password

### Frontend Configuration

Frontend configuration is mainly in `src/api/api.js`:

- `API_BASE_URL` - Backend API base URL
- `ICON_BASE_URL` - Icon file base URL

## Development Guide

### Backend Development

1. Create new API routes: Create new routing modules in the `app/api/` directory
2. Add business logic: Implement business functions in the `app/services/` directory
3. Define data models: Create model classes in the `app/models/` directory
4. Add utility functions: Add helper functions in the `app/utils/` directory

### Frontend Development

1. Create components: Organize UI components in the `src/components/` directory
2. Add styles: Write CSS styles in the `src/styles/` directory
3. API calls: Use the global `api` object for backend communication
4. State management: Use the `appState` object in `main.js` to manage application state

## Security Considerations

1. In production environments, default authentication information in the `.env` file must be changed
2. HTTPS protocol is recommended for production environments
3. Consider using more secure authentication mechanisms instead of simple authentication
4. Reasonably set file upload size limits to prevent DoS attacks
5. Strictly validate the type and content of uploaded files

## License

This project is licensed under the MIT License. See the LICENSE file for details.
  
## Changelog
  
### v0.1.9
- 实现图标删除功能
- 基于登录状态隐藏编辑区域按钮
- 实现图片在不同分类间转移功能
- 优化用户界面体验

### v0.1.6
- Optimized Docker image configuration, reduced image size
- Added multi-stage build and domestic mirror source support
- Improved containerized deployment solution
- Added resource limitations and log optimization
- Created `.dockerignore` and `.gitignore` files

### v0.1.5
- Refactored to separated front-end and back-end architecture
- Adopted modular design to improve code maintainability
- Optimized API design to support more functions
- Added responsive frontend interface
- Provided one-click startup script

### v0.1.0
- Initial project version
- Basic icon management functionality