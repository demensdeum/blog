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

api_url_posts = f"{site_url}/wp-json/wp/v2/posts"
api_url_categories = f"{site_url}/wp-json/wp/v2/categories"
headers = {
    "Authorization": f"Basic {auth_token}",
    "Content-Type": "application/json"
}

def get_all_categories():
    categories = []
    page = 1
    while True:
        response = requests.get(api_url_categories, headers=headers, params={"per_page": 100, "page": page})
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            categories.extend(data)
            page += 1
        else:
            print(f"Failed to fetch categories. Status code: {response.status_code}")
            sys.exit(1)
    return categories

def get_category_ids(category_names):
    all_categories = get_all_categories()
    print(category_names)
    print("---")
    print(all_categories)
    category_ids = []
    for name in category_names:
        print(f"name: {name} from {category_names}")
        found = False
        for category in all_categories:
            print(f"Searching for {name}")
            if category['slug'].lower() == name.lower().strip():
                category_ids.append(category['id'])
                found = True
                break
        if not found:
            print(f"Category '{name}' not found.")
            sys.exit(1)
    return category_ids

with open(file_path, "r", encoding="utf-8") as file:
    lines = file.readlines()
    if len(lines) < 4:
        print("File must contain at least four lines: slug, title, categories, and content.")
        sys.exit(1)
    
    slug = lines[0].strip()
    post_title = lines[1].strip()
    category_names = lines[2].strip().split(",")
    content = ''.join(lines[3:]).strip()

category_ids = get_category_ids(category_names)

search_params = {"slug": slug}
response = requests.get(api_url_posts, headers=headers, params=search_params)
posts = response.json()

if posts:
    post_id = posts[0]["id"]
    confirm = input(f"Post found: {post_id};\nURL: {site_url}?p={post_id}\nUpdate? (y/n) ")
    if confirm != "y":
        print("Not confirmed")
        exit(1)

    update_data = {
        "title": post_title,
        "content": content,
        "categories": category_ids
    }

    update_response = requests.post(f"{api_url_posts}/{post_id}", headers=headers, json=update_data)
    if update_response.status_code == 200:
        print(f"Post updated successfully. ID: {post_id}")
    else:
        print(f"Failed to update post: {update_response.status_code}")
else:
    create_data = {
        "title": post_title,
        "content": content,
        "slug": slug,
        "status": "publish",
        "categories": category_ids
    }

    create_response = requests.post(api_url_posts, headers=headers, json=create_data)
    if create_response.status_code == 201:
        new_post_id = create_response.json()["id"]
        print(f"Post created successfully. ID: {new_post_id}")
    else:
        print(f"Failed to create post: {create_response.status_code}")