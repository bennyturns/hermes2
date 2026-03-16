# Hermes - Deployment Guide

Complete guide for deploying Hermes to OpenShift or local environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Container Build](#container-build)
4. [OpenShift Deployment](#openshift-deployment)
5. [Configuration](#configuration)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

- **Container Runtime:** Podman (preferred) or Docker
- **OpenShift CLI:** `oc` command-line tool
- **Kustomize:** Built into `oc` and `kubectl`
- **Python 3.11+** (for local development)

### Access Requirements

- OpenShift cluster access with project creation permissions
- Quay.io or internal registry access (for container images)
- Google Cloud Vertex AI credentials (for production mode)

---

## Local Development

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:

```bash
# Mock mode for development (no real AI calls)
MOCK_MODE=true
MOCK_AGENTS=true
MOCK_EXECUTION=true

# Database
DATABASE_PATH=hermes.db

# Logging
LOG_LEVEL=DEBUG
ENVIRONMENT=development
```

### 3. Initialize Database

```bash
python app.py
# Database automatically initializes on first run
```

### 4. Run Development Server

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Access at: http://localhost:8000

---

## Container Build

### 1. Build Image

```bash
# Using the build script (recommended)
./build.sh

# Or manually with podman
podman build -t quay.io/redhat-et/hermes:latest -f Containerfile .

# Or with docker
docker build -t quay.io/redhat-et/hermes:latest -f Containerfile .
```

### 2. Test Container Locally

```bash
# Run with mock mode
podman run -p 8000:8000 \
  -e MOCK_MODE=true \
  -e MOCK_AGENTS=true \
  quay.io/redhat-et/hermes:latest

# Run with persistent data
podman run -p 8000:8000 \
  -v $(pwd)/data:/data \
  quay.io/redhat-et/hermes:latest
```

### 3. Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "hermes",
  "version": "1.0.0",
  "database": "connected",
  "vertex_ai": "not_configured",
  "mock_mode": true
}
```

### 4. Push to Registry

```bash
# Login to registry
podman login quay.io

# Push image
podman push quay.io/redhat-et/hermes:latest
```

---

## OpenShift Deployment

### 1. Create Vertex AI Secret

**Production mode requires Vertex AI credentials:**

```bash
# Copy the example secret
cp k8s/secret.yaml.example k8s/secret.yaml

# Edit with your credentials
vi k8s/secret.yaml
```

Fill in:
- `VERTEX_PROJECT_ID`: Your Google Cloud project ID
- `GOOGLE_APPLICATION_CREDENTIALS_JSON`: Service account JSON

**For mock/development mode**, skip this step and set `MOCK_MODE=true` in ConfigMap.

### 2. Configure Route Hostname

Edit `k8s/route.yaml`:

```yaml
spec:
  host: hermes.apps.your-cluster.example.com  # Update this
```

### 3. Deploy to OpenShift

```bash
# Login to OpenShift
oc login https://api.your-cluster.example.com

# Deploy using Kustomize
oc apply -k k8s/

# Or manually
oc apply -f k8s/namespace.yaml
oc apply -f k8s/serviceaccount.yaml
oc apply -f k8s/configmap.yaml
oc apply -f k8s/secret.yaml  # If created
oc apply -f k8s/pvc.yaml
oc apply -f k8s/deployment.yaml
oc apply -f k8s/service.yaml
oc apply -f k8s/route.yaml
oc apply -f k8s/networkpolicy.yaml
```

### 4. Verify Deployment

```bash
# Check pods
oc get pods -n hermes

# Check route
oc get route -n hermes

# View logs
oc logs -f deployment/hermes -n hermes

# Check health
ROUTE=$(oc get route hermes -n hermes -o jsonpath='{.spec.host}')
curl https://${ROUTE}/health
```

### 5. Access Application

Get the route URL:

```bash
oc get route hermes -n hermes
```

Open in browser: `https://hermes.apps.your-cluster.example.com`

---

## Configuration

### Environment Variables

Key configuration via ConfigMap (`k8s/configmap.yaml`):

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment name | `production` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `MOCK_MODE` | Enable mock mode (no real AI) | `false` |
| `MOCK_AGENTS` | Use mock AI responses | `false` |
| `MOCK_EXECUTION` | Dry-run file operations | `false` |
| `VERTEX_PROJECT_ID` | Google Cloud project | (from secret) |
| `VERTEX_REGION` | Vertex AI region | `us-east5` |
| `VERTEX_MODEL` | Claude model ID | `claude-sonnet-4-5@20250929` |
| `DATABASE_PATH` | SQLite database path | `/data/hermes.db` |

### Resource Limits

Default pod resources (`k8s/deployment.yaml`):

```yaml
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 2000m
    memory: 2Gi
```

Adjust based on workload:
- **Light usage:** 1 replica, 256Mi RAM
- **Production:** 2+ replicas, 1Gi+ RAM
- **High load:** 4+ replicas, autoscaling

### Persistent Storage

Default PVC size: 10Gi

To increase:

```bash
oc edit pvc hermes-data -n hermes
# Update spec.resources.requests.storage
```

---

## Monitoring

### Health Checks

Kubernetes probes configured:

- **Liveness:** `/health` every 30s
- **Readiness:** `/health` every 10s
- **Startup:** `/health` every 5s (up to 60s)

### Logs

```bash
# Stream pod logs
oc logs -f deployment/hermes -n hermes

# View all logs
oc logs deployment/hermes -n hermes --all-containers=true

# Logs from specific pod
oc logs hermes-xxxxx-yyyyy -n hermes
```

### Metrics

Application exposes metrics at `/metrics` (Prometheus format).

To enable scraping, the deployment includes annotations:

```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8000"
  prometheus.io/path: "/metrics"
```

### Events

```bash
# Check events
oc get events -n hermes --sort-by='.lastTimestamp'

# Watch events
oc get events -n hermes --watch
```

---

## Troubleshooting

### Pod Not Starting

**Check pod status:**

```bash
oc describe pod -l app=hermes -n hermes
```

Common issues:
- Image pull errors → Check registry credentials
- Crash loop → Check logs for errors
- Pending → Check PVC and resource quotas

### Database Issues

**Reset database:**

```bash
# Delete and recreate PVC (WARNING: deletes all data)
oc delete pvc hermes-data -n hermes
oc apply -f k8s/pvc.yaml
oc rollout restart deployment/hermes -n hermes
```

**Backup database:**

```bash
# Copy database from pod
POD=$(oc get pod -l app=hermes -n hermes -o jsonpath='{.items[0].metadata.name}')
oc cp ${POD}:/data/hermes.db ./backup/hermes-$(date +%Y%m%d).db -n hermes
```

### Vertex AI Connection Issues

**Check credentials:**

```bash
# Verify secret exists
oc get secret hermes-vertex-ai -n hermes

# Check environment variables
oc exec deployment/hermes -n hermes -- env | grep VERTEX
```

**Test from pod:**

```bash
oc exec -it deployment/hermes -n hermes -- python3 -c "
from vertex_client import vertex_client
import asyncio
status = asyncio.run(vertex_client.get_vertex_status())
print(status)
"
```

### Network Policy Issues

**Temporary disable NetworkPolicy:**

```bash
oc delete networkpolicy hermes-allow-ingress -n hermes
# Test if issue resolves
# Re-apply after testing
oc apply -f k8s/networkpolicy.yaml
```

### Route Not Accessible

**Check route:**

```bash
oc get route hermes -n hermes
oc describe route hermes -n hermes
```

**Test from within cluster:**

```bash
oc run test --rm -it --image=registry.access.redhat.com/ubi9/ubi -- curl http://hermes.hermes.svc:8000/health
```

---

## Scaling

### Manual Scaling

```bash
# Scale to 4 replicas
oc scale deployment/hermes --replicas=4 -n hermes
```

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: hermes
  namespace: hermes
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: hermes
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

Apply:

```bash
oc apply -f hpa.yaml
```

---

## Security

### Security Context

Pods run with:
- Non-root user (UID 1001)
- Read-only root filesystem (disabled for SQLite)
- Dropped all capabilities
- No privilege escalation

### Network Policies

Default policy:
- Ingress: Only from OpenShift router
- Egress: DNS, HTTPS (443), internal services

### TLS/HTTPS

Route uses edge TLS termination. Certificate automatically managed by OpenShift.

---

## Backup and Recovery

### Database Backup

```bash
# Create backup script
cat > backup.sh <<'EOF'
#!/bin/bash
NAMESPACE=hermes
POD=$(oc get pod -l app=hermes -n ${NAMESPACE} -o jsonpath='{.items[0].metadata.name}')
BACKUP_DIR=./backups
DATE=$(date +%Y%m%d-%H%M%S)

mkdir -p ${BACKUP_DIR}
oc cp ${NAMESPACE}/${POD}:/data/hermes.db ${BACKUP_DIR}/hermes-${DATE}.db
echo "Backup saved: ${BACKUP_DIR}/hermes-${DATE}.db"
EOF

chmod +x backup.sh
./backup.sh
```

### Database Restore

```bash
# Restore from backup
POD=$(oc get pod -l app=hermes -n hermes -o jsonpath='{.items[0].metadata.name}')
oc cp ./backups/hermes-20260313.db ${POD}:/data/hermes.db -n hermes
oc rollout restart deployment/hermes -n hermes
```

---

## Updates and Rollouts

### Update Image

```bash
# Build and push new image
./build.sh
podman push quay.io/redhat-et/hermes:v1.1.0

# Update deployment
oc set image deployment/hermes hermes=quay.io/redhat-et/hermes:v1.1.0 -n hermes

# Watch rollout
oc rollout status deployment/hermes -n hermes
```

### Rollback

```bash
# View rollout history
oc rollout history deployment/hermes -n hermes

# Rollback to previous version
oc rollout undo deployment/hermes -n hermes

# Rollback to specific revision
oc rollout undo deployment/hermes --to-revision=2 -n hermes
```

---

## Support

For issues and questions:
- GitHub: https://github.com/redhat-et/hermes/issues
- Internal: Red Hat OCTO team Slack #emerging-technologies

---

**Last Updated:** 2026-03-13
**Version:** 1.0.0
