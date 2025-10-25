#!/bin/bash

#
# DigitalOcean App Platform Deployment Script for Astro Engine
# Automated CLI deployment with validation and monitoring
#
# Usage: ./deploy-digitalocean.sh [OPTIONS]
#
# Options:
#   --create        Create new app
#   --update        Update existing app
#   --validate      Validate configuration only
#   --help          Show this help message
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SPEC_FILE=".do/app.yaml"
APP_NAME="astro-engine"
REGION="blr"  # Bangalore, India

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
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

check_prerequisites() {
    print_header "Checking Prerequisites"

    # Check if doctl is installed
    if ! command -v doctl &> /dev/null; then
        print_error "doctl CLI not found"
        echo ""
        echo "Install doctl:"
        echo "  macOS:   brew install doctl"
        echo "  Linux:   snap install doctl"
        echo "  Windows: https://docs.digitalocean.com/reference/doctl/how-to/install/"
        echo ""
        echo "Then authenticate:"
        echo "  doctl auth init"
        exit 1
    fi
    print_success "doctl CLI found"

    # Check if authenticated
    if ! doctl account get &> /dev/null; then
        print_error "doctl not authenticated"
        echo ""
        echo "Authenticate with:"
        echo "  doctl auth init"
        exit 1
    fi
    print_success "doctl authenticated"

    # Check if spec file exists
    if [ ! -f "$SPEC_FILE" ]; then
        print_error "Spec file not found: $SPEC_FILE"
        exit 1
    fi
    print_success "Spec file found: $SPEC_FILE"

    # Check if git repository is clean
    if [ -n "$(git status --porcelain)" ]; then
        print_warning "Git repository has uncommitted changes"
        echo "It's recommended to commit all changes before deploying"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    print_success "Prerequisites check complete"
    echo ""
}

validate_spec() {
    print_header "Validating App Specification"

    # Validate YAML syntax
    if command -v yamllint &> /dev/null; then
        if yamllint "$SPEC_FILE" &> /dev/null; then
            print_success "YAML syntax valid"
        else
            print_error "YAML syntax errors found"
            yamllint "$SPEC_FILE"
            exit 1
        fi
    else
        print_warning "yamllint not installed - skipping YAML syntax check"
    fi

    # Validate doctl can parse the spec
    if doctl apps spec validate "$SPEC_FILE" &> /dev/null; then
        print_success "DigitalOcean spec validation passed"
    else
        print_error "DigitalOcean spec validation failed"
        doctl apps spec validate "$SPEC_FILE"
        exit 1
    fi

    print_success "Validation complete"
    echo ""
}

generate_secret_key() {
    print_info "Generating random SECRET_KEY..."
    # Generate a 64-character random hex string
    SECRET_KEY=$(openssl rand -hex 32)
    print_success "SECRET_KEY generated (save this!)"
    echo "SECRET_KEY=$SECRET_KEY"
    echo ""
    print_warning "IMPORTANT: Update this in DigitalOcean App Platform settings!"
    echo ""
}

create_app() {
    print_header "Creating New DigitalOcean App"

    print_info "Creating app: $APP_NAME"
    print_info "Region: $REGION"
    print_info "Spec file: $SPEC_FILE"
    echo ""

    # Confirm
    read -p "Proceed with app creation? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "App creation cancelled"
        exit 0
    fi

    # Create the app
    print_info "Creating app (this may take a few minutes)..."
    if APP_OUTPUT=$(doctl apps create --spec "$SPEC_FILE" --format ID --no-header 2>&1); then
        APP_ID="$APP_OUTPUT"
        print_success "App created successfully!"
        print_success "App ID: $APP_ID"
        echo ""

        # Show app details
        print_info "Fetching app details..."
        doctl apps get "$APP_ID"
        echo ""

        print_success "Deployment initiated!"
        print_info "Monitor deployment progress:"
        echo "  doctl apps list"
        echo "  doctl apps get $APP_ID"
        echo "  doctl apps logs $APP_ID --type BUILD"
        echo "  doctl apps logs $APP_ID --type RUN"
        echo ""

        print_warning "Next steps:"
        echo "1. Update SECRET_KEY in App Platform settings"
        echo "2. Configure custom domain (optional)"
        echo "3. Monitor first deployment"
        echo "4. Test API endpoints"
        echo ""

        # Save app ID
        echo "$APP_ID" > .do/app_id.txt
        print_info "App ID saved to .do/app_id.txt"
    else
        print_error "App creation failed"
        echo "$APP_OUTPUT"
        exit 1
    fi
}

update_app() {
    print_header "Updating Existing DigitalOcean App"

    # Get app ID
    if [ -f ".do/app_id.txt" ]; then
        APP_ID=$(cat .do/app_id.txt)
        print_info "Using saved App ID: $APP_ID"
    else
        print_warning "No saved App ID found"
        print_info "Listing your apps:"
        doctl apps list
        echo ""
        read -p "Enter App ID to update: " APP_ID
    fi

    print_info "Updating app: $APP_ID"
    print_info "Spec file: $SPEC_FILE"
    echo ""

    # Confirm
    read -p "Proceed with app update? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "App update cancelled"
        exit 0
    fi

    # Update the app
    print_info "Updating app (this may take a few minutes)..."
    if doctl apps update "$APP_ID" --spec "$SPEC_FILE"; then
        print_success "App updated successfully!"
        echo ""

        print_info "Deployment initiated!"
        print_info "Monitor deployment progress:"
        echo "  doctl apps get $APP_ID"
        echo "  doctl apps logs $APP_ID --type BUILD --follow"
        echo "  doctl apps logs $APP_ID --type RUN --follow"
    else
        print_error "App update failed"
        exit 1
    fi
}

show_help() {
    cat << EOF
DigitalOcean App Platform Deployment Script for Astro Engine

Usage: $0 [OPTIONS]

Options:
  --create        Create new app on DigitalOcean
  --update        Update existing app
  --validate      Validate configuration only (no deployment)
  --secret        Generate random SECRET_KEY
  --help          Show this help message

Examples:
  # Validate configuration
  $0 --validate

  # Create new app
  $0 --create

  # Update existing app
  $0 --update

  # Generate secret key
  $0 --secret

Prerequisites:
  1. Install doctl: https://docs.digitalocean.com/reference/doctl/
  2. Authenticate: doctl auth init
  3. Commit all changes to git

For more information:
  https://docs.digitalocean.com/products/app-platform/
EOF
}

# Main script
main() {
    case "${1:-}" in
        --create)
            check_prerequisites
            validate_spec
            generate_secret_key
            create_app
            ;;
        --update)
            check_prerequisites
            validate_spec
            update_app
            ;;
        --validate)
            check_prerequisites
            validate_spec
            print_success "Configuration is valid and ready for deployment!"
            ;;
        --secret)
            generate_secret_key
            ;;
        --help)
            show_help
            ;;
        *)
            print_error "Invalid option: ${1:-none}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
