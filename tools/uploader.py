#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import sys
import argparse
import base64

parser = argparse.ArgumentParser(description="Upload or update a WordPress post.")
parser.add_argument("--post", required=True, help="Path to the post file.")
parser.add_argument("--blog", required=True, help="Path to the auth file with login and Application Password.")

args = parser.parse_args()
file_path = args.post
auth_file = args.blog

with open(auth_file, "r", encoding="utf-8") as file:
    lines = file.readlines()
    if len(lines) != 3:
        print("Auth file must contain three lines: blog url, login and Application Password.")
        sys.exit(1)
    
    site_url = lines[0].strip()
    username = lines[1].strip()
    app_password = lines[2].strip()

auth_token = base64.b64encode(f"{username}:{app_password}".encode()).decode()

api_url = f"{site_url}/wp-json/wp/v2/posts"
headers = {
    "Authorization": f"Basic {auth_token}",
    "Content-Type": "application/json"
}

with open(file_path, "r", encoding="utf-8") as file:
    lines = file.readlines()
    if len(lines) < 3:
        print("File must contain at least three lines: slug, title, and content.")
        sys.exit(1)
    
    slug = lines[0].strip() 
    post_title = lines[1].strip()
    content = ''.join(lines[2:]).strip()

search_params = {
    "slug": slug
}
print(f"Title: {post_title}")
print(f"Search slug: {slug}")
response = requests.get(api_url, headers=headers, params=search_params)
posts = response.json()

if posts:
    post_id = posts[0]["id"]
    confirm = input(f"Post found: {post_id};\nURL: {site_url}?p=3609\nUpdate? (y/n) ")
    if confirm != "y":
        print("Not confirmed")
        exit(1)    
    update_data = {
        "title": post_title,
        "content": content
    }
    update_response = requests.post(f"{api_url}/{post_id}", headers=headers, json=update_data)
    if update_response.status_code == 200:
        print(f"Post updated successfully. ID: {post_id}")
    else:
        print(f"Failed to update post: {update_response.status_code}")
else:
    create_data = {
        "title": post_title,
        "content": content,
        "slug": slug,
        "status": "publish"
    }
    create_response = requests.post(api_url, headers=headers, json=create_data)
    if create_response.status_code == 201:
        new_post_id = create_response.json()["id"]
        print(f"Post created successfully. ID: {new_post_id}")
    else:
        print(f"Failed to create post: {create_response.status_code}")
