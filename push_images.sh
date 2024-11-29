#!/bin/bash

DOCKER_HUB_USERNAME="kalebrs"

images=(
  "audiotranscribe-frontend"
  "audiotranscribe-backend"
  "audiotranscribe-postgres"
  "audiotranscribe-minio"
  "audiotranscribe-nginx"
)

for image in "${images[@]}"; do
  echo "Tagging $image:latest as $DOCKER_HUB_USERNAME/$image:latest..."
  docker tag "kalebrs/$image:latest" "$DOCKER_HUB_USERNAME/$image:latest"

  echo "Pushing $DOCKER_HUB_USERNAME/$image:latest to Docker Hub..."
  docker push "$DOCKER_HUB_USERNAME/$image:latest"
done

# open bash, run ./push_images.sh