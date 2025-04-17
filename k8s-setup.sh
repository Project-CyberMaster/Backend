#!/bin/sh

mkdir -p ./k8s/config

# Generate configmap for db
kubectl create configmap postgres-config \
    --from-env-file=.env \
    --dry-run=client \
    -o yaml > ./k8s/config/postgres-configmap.yaml

# Generate secret for db
kubectl create secret generic postgres-secret \
    --from-env-file=.env.secret \
    --dry-run=client \
    -o yaml > ./k8s/config/postgres-secret.yaml

# Generate pull secrets
kubectl create secret generic pull-secret \
    --from-file=.dockerconfigjson=$HOME/.docker/config.json \
    --type=kubernetes.io/dockerconfigjson \
    --dry-run=client -o yaml > ./k8s/config/pull-secret.yaml

# Aplly everything
kubectl apply k8s/config
kubectl apply k8s/backend
kubectl apply k8s/postgres