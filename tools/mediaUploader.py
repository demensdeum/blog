import requests
import os
import argparse
import sys
from requests.auth import HTTPBasicAuth

def upload_to_wordpress(file_path, site_url, username, app_password):
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' was not found in the 'media' folder.")
        return

    url = f'{site_url}/wp-json/wp/v2/media'

    with open(file_path, 'rb') as file:
        headers = {
            'Content-Disposition': f'attachment; filename={file_path}',
            'Content-Type': 'video/mp4',
        }
        response = requests.post(url, headers=headers, data=file, auth=HTTPBasicAuth(username, app_password))

    if response.status_code == 201:
        print('File uploaded successfully!')
        print('Response:', response.json())
    else:
        print(f'Error: {response.status_code}')
        print(response.text)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload video file to WordPress from the media folder.')
    parser.add_argument('--media', type=str, help='The name of the video file to upload')
    parser.add_argument('--blog', type=str, help='Path to the authentication file')
    args = parser.parse_args()

    with open(args.blog, "r", encoding="utf-8") as file:
        lines = file.readlines()
        if len(lines) != 3:
            print("Auth file must contain three lines: blog url, login, and Application Password.")
            sys.exit(1)

        site_url = lines[0].strip()
        username = lines[1].strip()
        app_password = lines[2]. strip()

    upload_to_wordpress(args.media, site_url, username, app_password)
