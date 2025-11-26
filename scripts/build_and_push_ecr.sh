#!/bin/bash
set -euo pipefail

LOG_DIR="logs/deployment"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/build_and_push_$(date +%Y%m%d_%H%M%S).log"

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
: "${BACKEND_REPO?Must set BACKEND_REPO to ECR repo URI}"
: "${FRONTEND_REPO?Must set FRONTEND_REPO to ECR repo URI}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

log "INFO" "Starting Docker build & push (tag=$IMAGE_TAG, region=$AWS_REGION)"

log "INFO" "Authenticating to ECR"
aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "${BACKEND_REPO%%/*}" \
  >> "$LOG_FILE" 2>&1 || abort "Failed to login to ECR"

build_and_push() {
  local target="$1"; shift
  local repo="$1"; shift
  local tag="${repo}:${IMAGE_TAG}"
  log "INFO" "Building $target image => $tag"
  docker build --target "$target" -t "$tag" . >> "$LOG_FILE" 2>&1 || abort "Docker build failed for $target"
  log "INFO" "Pushing $tag"
  docker push "$tag" >> "$LOG_FILE" 2>&1 || abort "Docker push failed for $target"
}

build_and_push backend "$BACKEND_REPO"
build_and_push frontend "$FRONTEND_REPO"

log "INFO" "Build & push completed successfully"
log "INFO" "Logs stored at $LOG_FILE"
