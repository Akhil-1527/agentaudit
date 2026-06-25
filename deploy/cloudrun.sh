#!/usr/bin/env bash
# Deploy AgentAudit's HTTP API to Google Cloud Run.
#
#   GEMINI_API_KEY=... ./deploy/cloudrun.sh <gcp-project-id> [region]
#
# Requires the gcloud CLI, authenticated (`gcloud auth login`).
set -euo pipefail

PROJECT="${1:?usage: GEMINI_API_KEY=... ./deploy/cloudrun.sh <gcp-project-id> [region]}"
REGION="${2:-us-central1}"
: "${GEMINI_API_KEY:?set GEMINI_API_KEY in your environment first}"

gcloud run deploy agentaudit \
  --source . \
  --project "${PROJECT}" \
  --region "${REGION}" \
  --set-env-vars "GOOGLE_GENAI_USE_VERTEXAI=FALSE,GEMINI_API_KEY=${GEMINI_API_KEY}" \
  --allow-unauthenticated

echo "Deployed. Try:  curl -X POST <service-url>/audit -d '{\"target\":\"mock\"}' -H 'content-type: application/json'"
