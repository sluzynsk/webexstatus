#!/bin/bash 
docker buildx build --platform linux/amd64,linux/aarch64 -t sluzynsk/webexstatus:latest .
