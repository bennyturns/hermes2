# Hermes Simulation — Live Demo on OpenShift

Deploy the Hermes simulation dashboard to your OpenShift cluster.

## Prerequisites

- `oc` CLI authenticated to your cluster
- Access to a container registry (e.g. quay.io)

## Build & Push

From the **repo root** (not this folder):

```bash
# Set your registry
export IMAGE=quay.io/<your-org>/hermes-simulation:latest

# Build
podman build -f live-demo/Containerfile -t $IMAGE .

# Push
podman push $IMAGE
```

## Deploy

```bash
# Create namespace
oc apply -f live-demo/deploy/namespace.yaml

# Update the image reference in the deployment
sed "s|IMAGE_PLACEHOLDER|$IMAGE|" live-demo/deploy/deployment.yaml | oc apply -f -

# Create service and route
oc apply -f live-demo/deploy/service.yaml
oc apply -f live-demo/deploy/route.yaml

# Get the URL
oc get route hermes-simulation -n hermes-demo -o jsonpath='{.spec.host}'
```

## Verify

```bash
oc get pods -n hermes-demo
oc logs -f deployment/hermes-simulation -n hermes-demo
```

## Clean Up

```bash
oc delete namespace hermes-demo
```
