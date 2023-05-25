#!/bin/bash 
docker buildx build --push --platform linux/amd64,linux/aarch64 -t sluzynsk/webexstatus:latest .
