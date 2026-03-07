#!/bin/bash

# Production Deployment Script for Email System
# This script helps automate the deployment process
#
# Usage:
#   chmod +x deploy.sh
#   ./deploy.sh production    # Full deployment
#   ./deploy.sh check         # Pre-deployment checks only
#   ./deploy.sh rollback      # Rollback to previous version

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/deployment.log"
BACKUP_DIR="$SCRIPT_DIR/backups"
ENV_FILE="$SCRIPT_DIR/.env.production"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1" | tee -a "$LOG_FILE"
}

# Initialize log file
init_log() {
    echo "=== Deployment Log - $(date) ===" > "$LOG_FILE"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        return 1
    fi
    log_success "Python 3 found: $(python3 --version)"

    # Check if .env.production exists
    if [ ! -f "$ENV_FILE" ]; then
        log_error ".env.production not found at $ENV_FILE"
        return 1
    fi
    log_success ".env.production found"

    # Check if requirements.txt exists
    if [ ! -f "$SCRIPT_DIR/requirements.txt" ]; then
        log_error "requirements.txt not found"
        return 1
    fi
    log_success "requirements.txt found"

    # Check if virtual environment exists
    if [ ! -d "$SCRIPT_DIR/.venv" ]; then
        log_warning "Virtual environment not found, creating one..."
        python3 -m venv "$SCRIPT_DIR/.venv"
        log_success "Virtual environment created"
    fi

    return 0
}

# Validate environment variables
validate_env() {
    log_info "Validating environment variables..."

    source "$ENV_FILE"

    # Check critical variables
    if [ -z "$DB_HOST" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ]; then
        log_error "Database configuration missing in .env.production"
        return 1
    fi

    if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "dev-secret-key-change-in-production" ]; then
        log_error "SECRET_KEY not set or using default value"
        return 1
    fi

    if [ -z "$SMTP_HOST" ] || [ -z "$SMTP_USERNAME" ] || [ -z "$SMTP_PASSWORD" ]; then
        log_error "SMTP configuration missing in .env.production"
        return 1
    fi

    log_success "Environment variables validated"
    return 0
}

# Test database connection
test_database() {
    log_info "Testing database connection..."

    source "$ENV_FILE"

    if ! mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" -e "SELECT 1;" &>/dev/null; then
        log_error "Failed to connect to database"
        return 1
    fi

    log_success "Database connection successful"
    return 0
}

# Test SMTP connection
test_smtp() {
    log_info "Testing SMTP connection..."

    source "$ENV_FILE"

    python3 <<EOF
import smtplib
try:
    server = smtplib.SMTP('$SMTP_HOST', $SMTP_PORT)
    server.starttls()
    server.login('$SMTP_USERNAME', '$SMTP_PASSWORD')
    server.quit()
    print("✓ SMTP connection successful")
except Exception as e:
    print(f"✗ SMTP connection failed: {e}")
    exit(1)
EOF

    if [ $? -eq 0 ]; then
        log_success "SMTP connection successful"
        return 0
    else
        log_error "SMTP connection failed"
        return 1
    fi
}

# Pre-deployment checks
pre_deployment_checks() {
    log_info "Running pre-deployment checks..."

    if ! check_prerequisites; then
        log_error "Prerequisites check failed"
        return 1
    fi

    if ! validate_env; then
        log_error "Environment validation failed"
        return 1
    fi

    if ! test_database; then
        log_error "Database test failed"
        return 1
    fi

    if ! test_smtp; then
        log_error "SMTP test failed"
        return 1
    fi

    log_success "All pre-deployment checks passed"
    return 0
}

# Install/update dependencies
install_dependencies() {
    log_info "Installing dependencies..."

    source "$SCRIPT_DIR/.venv/bin/activate"
    pip install --upgrade pip setuptools wheel >> "$LOG_FILE" 2>&1
    pip install -r "$SCRIPT_DIR/requirements.txt" >> "$LOG_FILE" 2>&1

    log_success "Dependencies installed"
}

# Backup database
backup_database() {
    log_info "Backing up database..."

    source "$ENV_FILE"

    mkdir -p "$BACKUP_DIR"
    BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql.gz"

    if mysqldump -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" | gzip > "$BACKUP_FILE"; then
        log_success "Database backed up to $BACKUP_FILE"
        return 0
    else
        log_error "Database backup failed"
        return 1
    fi
}

# Initialize database
init_database() {
    log_info "Initializing database..."

    source "$SCRIPT_DIR/.venv/bin/activate"
    cd "$SCRIPT_DIR"

    if FLASK_ENV=production python db_setup.py >> "$LOG_FILE" 2>&1; then
        log_success "Database initialized"
        return 0
    else
        log_error "Database initialization failed"
        return 1
    fi
}

# Run tests
run_tests() {
    log_info "Running tests..."

    source "$SCRIPT_DIR/.venv/bin/activate"
    cd "$SCRIPT_DIR"

    # Basic import test
    if python3 -c "import dashboard; print('✓ Dashboard imports successfully')" >> "$LOG_FILE" 2>&1; then
        log_success "Application tests passed"
        return 0
    else
        log_error "Application tests failed"
        return 1
    fi
}

# Deploy application
deploy() {
    log_info "Starting deployment..."

    if ! pre_deployment_checks; then
        log_error "Deployment aborted - checks failed"
        return 1
    fi

    if ! backup_database; then
        log_error "Deployment aborted - backup failed"
        return 1
    fi

    if ! install_dependencies; then
        log_error "Deployment aborted - dependency installation failed"
        return 1
    fi

    if ! init_database; then
        log_error "Deployment aborted - database initialization failed"
        return 1
    fi

    if ! run_tests; then
        log_error "Deployment aborted - tests failed"
        return 1
    fi

    log_success "Deployment completed successfully"
    log_info "Next steps:"
    log_info "  1. Restart the application: systemctl restart email-system"
    log_info "  2. Monitor logs: journalctl -u email-system -f"
    log_info "  3. Check application health: curl https://yourdomain.com/"

    return 0
}

# Rollback to previous version
rollback() {
    log_info "Rolling back to previous version..."

    if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A $BACKUP_DIR)" ]; then
        log_error "No backups available for rollback"
        return 1
    fi

    LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/backup_*.sql.gz | head -1)

    if [ -z "$LATEST_BACKUP" ]; then
        log_error "No backup files found"
        return 1
    fi

    source "$ENV_FILE"

    log_warning "Restoring from $LATEST_BACKUP (this will overwrite current database)"
    read -p "Are you sure? (yes/no): " -r
    echo

    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        if gunzip -c "$LATEST_BACKUP" | mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME"; then
            log_success "Database restored from backup"
            log_info "Restarting application..."
            systemctl restart email-system || log_warning "Could not restart application (may require manual intervention)"
            return 0
        else
            log_error "Database restoration failed"
            return 1
        fi
    else
        log_info "Rollback cancelled"
        return 1
    fi
}

# Main script
main() {
    init_log
    log_info "Email System Deployment Tool"
    
    case "${1:-production}" in
        production|deploy)
            deploy
            exit $?
            ;;
        check)
            pre_deployment_checks
            exit $?
            ;;
        rollback)
            rollback
            exit $?
            ;;
        *)
            echo "Usage: $0 [production|check|rollback]"
            echo ""
            echo "Commands:"
            echo "  production  - Full deployment (default)"
            echo "  check       - Run pre-deployment checks only"
            echo "  rollback    - Rollback to previous backup"
            exit 1
            ;;
    esac
}

main "$@"
