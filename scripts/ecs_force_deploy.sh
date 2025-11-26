#!/bin/bash
set -euo pipefail

LOG_DIR="logs/deployment"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/ecs_deploy_$(date +%Y%m%d_%H%M%S).log"

log() {
  local level="$1"; shift
  local msg="$*"
  local timestamp
  timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  echo "[$timestamp] [$level] $msg" | tee -a "$LOG_FILE"
}

abort() {
  log "ERROR" "$1"
  exit 1
}

: "${AWS_REGION?Must set AWS_REGION}"
: "${ECS_CLUSTER?Must set ECS_CLUSTER}"
: "${ECS_SERVICE?Must set ECS_SERVICE}"

log "INFO" "Triggering ECS deployment (cluster=$ECS_CLUSTER, service=$ECS_SERVICE)"
aws ecs update-service \
  --cluster "$ECS_CLUSTER" \
  --service "$ECS_SERVICE" \
  --force-new-deployment \
  --region "$AWS_REGION" >> "$LOG_FILE" 2>&1 || abort "Failed to update ECS service"

log "INFO" "Deployment triggered successfully"
log "INFO" "Logs stored at $LOG_FILE"
