import requests
import argparse
import os
import re
import sys

def fetch_category_slugs(url, category_ids, username, app_password):
    categories_api_url = f"{url}/wp-json/wp/v2/categories"
    response = requests.get(categories_api_url, params={"include": ",".join(map(str, category_ids))}, auth=(username, app_password))
    response.raise_for_status()
    categories = response.json()
    return [category["slug"] for category in categories]

def fetch_post_from_wordpress(url, post_slug, username, app_password, lang):
    api_url = f"{url}/{lang}/wp-json/wp/v2/posts"
    print(api_url)
    response = requests.get(api_url, params={"slug": post_slug}, auth=(username, app_password))
    response.raise_for_status()
    posts = response.json()
    if not posts:
        raise ValueError(f"Post with slug '{post_slug}' not found.")
    return posts[0]


def convert_post_to_file(post, output_dir, lang, site_url, username, app_password):
    title = post.get("title", {}).get("rendered", "")
    content = post.get("content", {}).get("rendered", "")
    slug = post.get("slug", "")
    category_ids = post.get("categories", [])
    category_slugs = fetch_category_slugs(site_url, category_ids, username, app_password)
    categories = ",".join(category_slugs)
    format_str = "Fall24-October10"
    language = lang
    output_path = os.path.join(output_dir, f"{slug}.txt")

    if not os.path.exists(output_dir):
        raise FileNotFoundError(f"Directory '{output_dir}' does not exist.")

    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(f"Format: {format_str}\n")
        file.write(f"Language: {language}\n")
        file.write(f"Title: {title}\n")
        file.write(f"Slug: {slug}\n")
        file.write(f"Categories: {categories}\n")
        file.write(content.strip())


def main():
    parser = argparse.ArgumentParser(description="Export WordPress post to file.")
    parser.add_argument("--post", required=True, help="Slug of the WordPress post.")
    parser.add_argument("--output-dir", required=True, help="Directory to save the output file (e.g., src).")
    parser.add_argument("--lang", required=True, help="Language code (e.g., ru).")
    parser.add_argument("--blog", required=True, help="Path to the auth file with login and Application Password.")
    args = parser.parse_args()

    file_path = args.post
    auth_file = args.blog

    with open(auth_file, "r", encoding="utf-8") as file:
        lines = file.readlines()
        if len(lines) != 3:
            print("Auth file must contain three lines: blog URL, login, and Application Password.")
            sys.exit(1)

        site_url = lines[0].strip()
        username = lines[1].strip()
        app_password = lines[2].strip()

    try:
        post = fetch_post_from_wordpress(site_url, file_path, username, app_password, args.lang)
        convert_post_to_file(post, args.output_dir, args.lang, site_url, username, app_password)
        print(f"Post saved successfully to '{args.output_dir}'")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
