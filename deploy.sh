#!/bin/bash
# ============================================================================
# Deployment Script for Drone Components Configurator
# ============================================================================
# Швидкий деплой на різні платформи
# Використання: bash deploy.sh [platform]
# Платформи: local, streamlit-cloud, docker, heroku
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if platform is specified
PLATFORM=${1:-"local"}

print_header "Drone Components Configurator - Deploy Script"
echo "Платформа: $PLATFORM"

# ============================================================================
# LOCAL DEPLOYMENT
# ============================================================================
if [ "$PLATFORM" == "local" ]; then
    print_header "Локальний деплой"
    
    # Check Python version
    print_info "Перевірка Python версії..."
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    print_success "Python $python_version"
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_info "Створення віртуального середовища..."
        python3 -m venv venv
        print_success "Віртуальне середовище створено"
    else
        print_info "Віртуальне середовище вже існує"
    fi
    
    # Activate virtual environment
    print_info "Активація віртуального середовища..."
    source venv/bin/activate
    
    # Install dependencies
    print_info "Встановлення залежностей..."
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt > /dev/null 2>&1
    print_success "Залежності встановлено"
    
    # Check secrets file
    if [ ! -f ".streamlit/secrets.toml" ]; then
        print_warning "Файл .streamlit/secrets.toml не знайдено"
        
        if [ -f ".streamlit/secrets.toml.example" ]; then
            print_info "Копіювання з шаблону..."
            cp .streamlit/secrets.toml.example .streamlit/secrets.toml
            print_warning "Відредагуйте .streamlit/secrets.toml перед запуском!"
        fi
    else
        print_success "Secrets файл знайдено"
    fi
    
    # Run tests
    print_info "Запуск тестів..."
    python test_setup.py
    
    # Start application
    print_header "Запуск додатку"
    print_success "Додаток доступний на: http://localhost:8501"
    streamlit run app.py

# ============================================================================
# STREAMLIT CLOUD DEPLOYMENT
# ============================================================================
elif [ "$PLATFORM" == "streamlit-cloud" ]; then
    print_header "Streamlit Cloud Деплой"
    
    print_info "Перевірка Git репозиторію..."
    
    if [ ! -d ".git" ]; then
        print_error "Git репозиторій не ініціалізовано"
        print_info "Ініціалізація Git..."
        git init
        git add .
        git commit -m "Initial commit: Drone Components Configurator"
        print_success "Git репозиторій створено"
    fi
    
    print_info "Інструкції для Streamlit Cloud:"
    echo ""
    echo "1. Завантажте код на GitHub:"
    echo "   git remote add origin <your-repo-url>"
    echo "   git push -u origin main"
    echo ""
    echo "2. Перейдіть на https://streamlit.io/cloud"
    echo ""
    echo "3. Підключіть GitHub репозиторій"
    echo ""
    echo "4. Налаштуйте Secrets (Settings → Secrets):"
    echo "   Скопіюйте вміст .streamlit/secrets.toml"
    echo ""
    echo "5. Deploy!"
    echo ""
    print_success "Ваш додаток буде доступний на https://share.streamlit.io/..."

# ============================================================================
# DOCKER DEPLOYMENT
# ============================================================================
elif [ "$PLATFORM" == "docker" ]; then
    print_header "Docker Деплой"
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker не встановлено"
        print_info "Встановіть Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    print_success "Docker знайдено"
    
    # Create Dockerfile if not exists
    if [ ! -f "Dockerfile" ]; then
        print_info "Створення Dockerfile..."
        cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
EOF
        print_success "Dockerfile створено"
    fi
    
    # Create .dockerignore
    if [ ! -f ".dockerignore" ]; then
        print_info "Створення .dockerignore..."
        cat > .dockerignore << 'EOF'
venv/
__pycache__/
*.pyc
.git/
.gitignore
README.md
SETUP_GUIDE.md
test_setup.py
quickstart.py
.streamlit/secrets.toml
EOF
        print_success ".dockerignore створено"
    fi
    
    # Build Docker image
    print_info "Збірка Docker образу..."
    docker build -t drone-calculator:latest .
    print_success "Docker образ зібрано"
    
    # Run container
    print_info "Запуск Docker контейнера..."
    
    # Check if secrets file exists
    if [ -f ".streamlit/secrets.toml" ]; then
        docker run -d \
            -p 8501:8501 \
            -v "$(pwd)/.streamlit:/app/.streamlit" \
            --name drone-calculator \
            drone-calculator:latest
    else
        print_warning "Secrets файл не знайдено. Запуск без secrets..."
        docker run -d \
            -p 8501:8501 \
            --name drone-calculator \
            drone-calculator:latest
    fi
    
    print_success "Docker контейнер запущено"
    print_info "Додаток доступний на: http://localhost:8501"
    
    # Show logs
    print_info "Логи контейнера (Ctrl+C для виходу):"
    docker logs -f drone-calculator

# ============================================================================
# HEROKU DEPLOYMENT
# ============================================================================
elif [ "$PLATFORM" == "heroku" ]; then
    print_header "Heroku Деплой"
    
    # Check if Heroku CLI is installed
    if ! command -v heroku &> /dev/null; then
        print_error "Heroku CLI не встановлено"
        print_info "Встановіть: https://devcenter.heroku.com/articles/heroku-cli"
        exit 1
    fi
    
    print_success "Heroku CLI знайдено"
    
    # Login check
    print_info "Перевірка авторизації Heroku..."
    if ! heroku auth:whoami &> /dev/null; then
        print_info "Потрібна авторизація..."
        heroku login
    fi
    
    # Create Heroku app
    APP_NAME="drone-calculator-$(date +%s)"
    print_info "Створення Heroku app: $APP_NAME..."
    heroku create $APP_NAME
    
    # Create Procfile
    if [ ! -f "Procfile" ]; then
        print_info "Створення Procfile..."
        echo "web: streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile
        print_success "Procfile створено"
    fi
    
    # Create setup.sh
    if [ ! -f "setup.sh" ]; then
        print_info "Створення setup.sh..."
        cat > setup.sh << 'EOF'
mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"your-email@domain.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml
EOF
        chmod +x setup.sh
        print_success "setup.sh створено"
    fi
    
    # Set environment variables
    print_info "Налаштування змінних оточення..."
    print_warning "Додайте Supabase credentials через Heroku Dashboard"
    
    # Deploy
    print_info "Деплой на Heroku..."
    git add .
    git commit -m "Deploy to Heroku" || true
    git push heroku main
    
    # Open app
    print_success "Деплой завершено!"
    heroku open

# ============================================================================
# UNKNOWN PLATFORM
# ============================================================================
else
    print_error "Невідома платформа: $PLATFORM"
    echo ""
    echo "Доступні платформи:"
    echo "  local           - Локальний запуск"
    echo "  streamlit-cloud - Streamlit Cloud"
    echo "  docker          - Docker контейнер"
    echo "  heroku          - Heroku PaaS"
    echo ""
    echo "Використання: bash deploy.sh [platform]"
    exit 1
fi

print_header "Деплой завершено!"
