#!/bin/bash

docker build -t vladko2050/external-eval-api:latest .
docker push vladko2050/external-eval-api:latest
kubectl rollout restart deployment/external-eval-api -n external-eval
