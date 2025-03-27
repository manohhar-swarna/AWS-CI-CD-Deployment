#!/bin/bash

# Get the ID of the currently running container
container_id=$(docker ps -q)

# Stop and remove the currently running container if it exists
if [ -n "$container_id" ]; then
  echo "Stopping container: $container_id"
  docker stop "$container_id"

  echo "Removing container: $container_id"
  docker rm "$container_id"
else
  echo "No running containers found."
fi

docker image prune -f

docker pull #ECR repository name
docker run -d -p 8080:8080 #ECR repository name
