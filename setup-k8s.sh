#!/bin/sh

mkdir -p ./k8s/config

# Generate configmap for db
kubectl create configmap postgres-config \
    --from-env-file=.env \
    --dry-run=client \
    -o yaml > ./k8s/config/configmaps/postgres-configmap.yaml

# Generate secret for db
kubectl create secret generic postgres-secret \
    --from-env-file=.env.secret \
    --dry-run=client \
    -o yaml > ./k8s/config/secrets/postgres-secret.yaml

# Generate pull secrets
kubectl create secret generic pull-secret \
    --from-file=.dockerconfigjson=$HOME/.docker/config.json \
    --type=kubernetes.io/dockerconfigjson \
    --dry-run=client -o yaml > ./k8s/config/secrets/pull-secret.yaml

# Aplly everything
kubectl apply -f k8s/config/secrets
kubectl apply -f k8s/config/configmaps
kubectl apply -f k8s/config/namespaces
kubectl apply -f k8s/config/serviceaccounts
kubectl apply -f k8s/config/roles
kubectl apply -f k8s/config/middleware
kubectl apply -f k8s/postgres
kubectl apply -f k8s/backend