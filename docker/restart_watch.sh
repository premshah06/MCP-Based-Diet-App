#!/bin/bash

# Diet Coach MCP - Service Health Monitor and Auto-Restart Script
# This script monitors the health of Docker Compose services and restarts unhealthy ones

set -euo pipefail

# Configuration
COMPOSE_FILE="docker/compose.yml"
LOG_FILE="/tmp/diet-coach-monitor.log"
CHECK_INTERVAL=30  # seconds
MAX_RESTART_ATTEMPTS=3
RESTART_COOLDOWN=60  # seconds between restart attempts

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to get service status
get_service_status() {
    local service_name="$1"
    docker compose -f "$COMPOSE_FILE" ps --format json "$service_name" 2>/dev/null | \
        jq -r '.[0].Health // "unknown"' 2>/dev/null || echo "unknown"
}

# Function to restart a service
restart_service() {
    local service_name="$1"
    local attempt="$2"
    
    log "${YELLOW}Attempting to restart $service_name (attempt $attempt/$MAX_RESTART_ATTEMPTS)${NC}"
    
    if docker compose -f "$COMPOSE_FILE" restart "$service_name"; then
        log "${GREEN}Successfully restarted $service_name${NC}"
        return 0
    else
        log "${RED}Failed to restart $service_name${NC}"
        return 1
    fi
}

# Function to check and restart unhealthy services
check_and_restart_services() {
    local services=("diet-api" "diet-mcp" "ollama")
    local restart_counts_file="/tmp/diet-coach-restart-counts"
    
    # Initialize restart counts file if it doesn't exist
    if [[ ! -f "$restart_counts_file" ]]; then
        for service in "${services[@]}"; do
            echo "$service:0:0" >> "$restart_counts_file"
        done
    fi
    
    for service in "${services[@]}"; do
        local status=$(get_service_status "$service")
        log "${BLUE}Service $service status: $status${NC}"
        
        if [[ "$status" == "unhealthy" ]]; then
            # Read current restart count and last restart time
            local restart_info=$(grep "^$service:" "$restart_counts_file" || echo "$service:0:0")
            local restart_count=$(echo "$restart_info" | cut -d: -f2)
            local last_restart=$(echo "$restart_info" | cut -d: -f3)
            local current_time=$(date +%s)
            
            # Check if we're within cooldown period
            if [[ $((current_time - last_restart)) -lt $RESTART_COOLDOWN ]]; then
                log "${YELLOW}Service $service is in cooldown period, skipping restart${NC}"
                continue
            fi
            
            # Check if we've exceeded max restart attempts
            if [[ $restart_count -ge $MAX_RESTART_ATTEMPTS ]]; then
                log "${RED}Service $service has exceeded maximum restart attempts ($MAX_RESTART_ATTEMPTS)${NC}"
                log "${RED}Manual intervention required for $service${NC}"
                continue
            fi
            
            # Attempt restart
            restart_count=$((restart_count + 1))
            if restart_service "$service" "$restart_count"; then
                # Update restart count and timestamp
                sed -i "s/^$service:.*/$service:$restart_count:$current_time/" "$restart_counts_file"
                
                # Wait for service to come online
                log "${BLUE}Waiting for $service to become healthy...${NC}"
                local wait_count=0
                local max_wait=60  # seconds
                
                while [[ $wait_count -lt $max_wait ]]; do
                    sleep 5
                    wait_count=$((wait_count + 5))
                    local new_status=$(get_service_status "$service")
                    
                    if [[ "$new_status" == "healthy" ]]; then
                        log "${GREEN}Service $service is now healthy${NC}"
                        # Reset restart count on successful recovery
                        sed -i "s/^$service:.*/$service:0:0/" "$restart_counts_file"
                        break
                    elif [[ "$new_status" == "unhealthy" && $wait_count -ge $max_wait ]]; then
                        log "${RED}Service $service failed to become healthy after restart${NC}"
                    fi
                done
            else
                # Update restart count even on failed restart
                sed -i "s/^$service:.*/$service:$restart_count:$current_time/" "$restart_counts_file"
            fi
        elif [[ "$status" == "healthy" ]]; then
            # Reset restart count for healthy services
            sed -i "s/^$service:.*/$service:0:0/" "$restart_counts_file"
        elif [[ "$status" == "unknown" ]]; then
            log "${YELLOW}Service $service status unknown - may not be running${NC}"
        fi
    done
}

# Function to show service overview
show_service_overview() {
    echo -e "\n${BLUE}=== Diet Coach MCP Service Overview ===${NC}"
    docker compose -f "$COMPOSE_FILE" ps --format table
    echo ""
}

# Function to clean up old logs
cleanup_logs() {
    if [[ -f "$LOG_FILE" ]] && [[ $(wc -l < "$LOG_FILE") -gt 1000 ]]; then
        tail -500 "$LOG_FILE" > "${LOG_FILE}.tmp"
        mv "${LOG_FILE}.tmp" "$LOG_FILE"
        log "Rotated log file to keep last 500 entries"
    fi
}

# Main monitoring loop
main() {
    log "${GREEN}Starting Diet Coach MCP health monitor${NC}"
    log "Checking services every $CHECK_INTERVAL seconds"
    log "Log file: $LOG_FILE"
    
    # Check if Docker Compose file exists
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        log "${RED}Docker Compose file not found: $COMPOSE_FILE${NC}"
        log "Please run this script from the project root directory"
        exit 1
    fi
    
    # Initial service overview
    show_service_overview
    
    # Main monitoring loop
    while true; do
        check_and_restart_services
        cleanup_logs
        
        # Show brief status every 10 minutes
        if [[ $(($(date +%s) % 600)) -lt $CHECK_INTERVAL ]]; then
            show_service_overview
        fi
        
        sleep "$CHECK_INTERVAL"
    done
}

# Signal handlers
cleanup() {
    log "${YELLOW}Received termination signal, shutting down monitor${NC}"
    exit 0
}

# Set up signal handling
trap cleanup SIGINT SIGTERM

# Usage information
usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  --check-once   Run health check once and exit"
    echo "  --status       Show current service status and exit"
    echo "  --logs         Show recent monitor logs"
    echo ""
    echo "Diet Coach MCP Health Monitor"
    echo "Monitors Docker Compose services and automatically restarts unhealthy ones"
}

# Command line argument handling
case "${1:-}" in
    -h|--help)
        usage
        exit 0
        ;;
    --check-once)
        log "Running one-time health check"
        check_and_restart_services
        show_service_overview
        exit 0
        ;;
    --status)
        show_service_overview
        exit 0
        ;;
    --logs)
        if [[ -f "$LOG_FILE" ]]; then
            tail -50 "$LOG_FILE"
        else
            echo "No log file found at $LOG_FILE"
        fi
        exit 0
        ;;
    "")
        # No arguments, run main loop
        main
        ;;
    *)
        echo "Unknown option: $1"
        usage
        exit 1
        ;;
esac
