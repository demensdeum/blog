import requests
import os
import argparse
import sys
import mimetypes
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

def check_if_exists(site_url, username, app_password, filename):
    search_name = os.path.basename(filename)
    url = f'{site_url}/wp-json/wp/v2/media'
    params = {
        'search': search_name,
        'per_page': 1
    }

    response = requests.get(
        url,
        params=params,
        auth=HTTPBasicAuth(username, app_password)
    )

    if response.status_code == 200:
        media_items = response.json()
        for item in media_items:
            source_url = item.get('source_url', '')
            if search_name in source_url:
                return item
    return None

def upload_to_wordpress(file_path, site_url, username, app_password):
    file_path = f"./media/{file_path}"
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' was not found.", file=sys.stderr)
        return

    if args.override == False:
        print(f"Checking if '{os.path.basename(file_path)}' already exists...", file=sys.stderr)
        existing_media = check_if_exists(site_url, username, app_password, file_path)

        if existing_media:
            print(existing_media['source_url'])
            return

    print("No duplicate found. Proceeding with upload...", file=sys.stderr)
    url = f'{site_url}/wp-json/wp/v2/media'
    filename = os.path.basename(file_path)

    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = 'application/octet-stream'

    with open(file_path, 'rb') as file:
        headers = {
            'Content-Disposition': f'attachment; filename={filename}',
            'Content-Type': mime_type,
        }
        response = requests.post(
            url,
            headers=headers,
            data=file,
            auth=HTTPBasicAuth(username, app_password)
        )

    if response.status_code == 201:
        print(response.json().get('source_url'))
    else:
        print(f'Error: {response.status_code}', file=sys.stderr)
        print(response.text, file=sys.stderr)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload any file to WordPress with duplicate checking.')
    parser.add_argument('media', type=str, help='The path of the file to upload')
    parser.add_argument('--override', action='store_true', help='Enable override mode to bypass duplicate checking')
    args = parser.parse_args()

    site_url = os.environ["SITE_URL"]
    username = os.environ["SITE_USER"]
    app_password = os.environ["SITE_PASSWORD"]

    upload_to_wordpress(args.media, site_url, username, app_password)
