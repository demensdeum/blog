#!/bin/bash

CONFIG_FILE="private/wordpress"
if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "Error: Configuration file '$CONFIG_FILE' not found."
  exit 1
fi

API_URL=$(sed -n '1p' "$CONFIG_FILE")
USERNAME=$(sed -n '2p' "$CONFIG_FILE")
PASSWORD=$(sed -n '3p' "$CONFIG_FILE")

TARGET_SLUG="gof-patterns"

target_post=$(curl -s --user "$USERNAME:$PASSWORD" "${API_URL}/wp-json/wp/v2/posts?slug=${TARGET_SLUG}")
target_date=$(echo "$target_post" | jq -r '.[0].date')

if [[ -z "$target_date" || "$target_date" == "null" ]]; then
  echo "Error: Post with slug '$TARGET_SLUG' not found."
  exit 1
fi

echo "Target post date: $target_date"

posts=$(curl -s --user "$USERNAME:$PASSWORD" "${API_URL}/wp-json/wp/v2/posts?before=${target_date}&per_page=100")
post_slugs=$(echo "$posts" | jq -r '.[] | .slug')

if [[ -z "$post_slugs" ]]; then
  echo "No posts found earlier than '$TARGET_SLUG'."
  exit 0
fi

echo "Processing posts..."
for slug in $post_slugs; do
  echo "Processing slug: $slug"
  ./importRecompileUpload.sh "$slug"
done

echo "All posts processed."
