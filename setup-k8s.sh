#!/bin/sh

mkdir -p ./k8s/config

# Generate configmap for db
minikube kubectl -- create configmap postgres-config \
    --from-env-file=.env \
    --dry-run=client \
    -o yaml > ./k8s/config/configmaps/postgres-configmap.yaml

# Generate secret for db
minikube kubectl -- create secret generic postgres-secret \
    --from-env-file=.env.secret \
    --dry-run=client \
    -o yaml > ./k8s/config/secrets/postgres-secret.yaml

# Generate pull secrets
minikube kubectl -- create secret generic pull-secret \
    --from-file=.dockerconfigjson=$HOME/.docker/config.json \
    --type=kubernetes.io/dockerconfigjson \
    --dry-run=client -o yaml > ./k8s/config/secrets/pull-secret.yaml

# Aplly everything
minikube kubectl -- apply -f k8s/config/secrets
minikube kubectl -- apply -f k8s/config/configmaps
minikube kubectl -- apply -f k8s/config/namespaces
minikube kubectl -- apply -f k8s/config/serviceaccounts
minikube kubectl -- apply -f k8s/config/roles
minikube kubectl -- apply -f k8s/config/middleware
minikube kubectl -- apply -f k8s/postgres
minikube kubectl -- apply -f k8s/backend