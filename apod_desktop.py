import os
import sys
import requests
import sqlite3
from datetime import date, datetime
from hashlib import sha256
import image_lib

# Define paths
script_dir = os.path.dirname(os.path.abspath(__file__))
image_cache_dir = os.path.join(script_dir, 'images')
image_cache_db = os.path.join(image_cache_dir, 'image_cache.db')

def main():
    apod_date = get_apod_date()
    init_apod_cache()
    apod_id = add_apod_to_cache(apod_date)
    apod_info = get_apod_info(apod_id)
    if apod_info:
        print(f"Setting desktop background to APOD from {apod_date.isoformat()}...success")
        image_lib.set_desktop_background_image(apod_info['file_path'])
    else:
        print("Failed to retrieve APOD information.")

def get_apod_date():
    if len(sys.argv) > 1:
        try:
            apod_date = datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
        except ValueError:
            print("Error: Invalid date format; use YYYY-MM-DD.")
            sys.exit(1)
    else:
        apod_date = date.today()

    if apod_date > date.today():
        print("Error: APOD date cannot be in the future.")
        sys.exit(1)

    print(f"APOD date: {apod_date.isoformat()}")
    return apod_date

def init_apod_cache():
    print(f"Image cache directory: {image_cache_dir}")
    if not os.path.exists(image_cache_dir):
        os.makedirs(image_cache_dir)
        print("Image cache directory created.")
    else:
        print("Image cache directory already exists.")

    print(f"Image cache DB: {image_cache_db}")
    conn = sqlite3.connect(image_cache_db)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS apod (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            explanation TEXT,
            file_path TEXT,
            sha256 TEXT UNIQUE
        )
    ''')
    conn.close()

    if os.path.exists(image_cache_db):
        print("Image cache DB already exists.")
    else:
        print("Image cache DB created.")

def add_apod_to_cache(apod_date):
    print(f"Getting {apod_date.isoformat()} APOD information from NASA...", end="")
    apod_info = get_apod_info_from_api(apod_date)
    if not apod_info:
        return 0

    print("success")
    print(f"APOD title: {apod_info['title']}")
    print(f"APOD URL: {apod_info['url']}")
    print(f"Downloading image from {apod_info['url']}...", end="")
    image_data = image_lib.download_image(apod_info['url'])
    if not image_data:
        print("failed")
        return 0

    print("success")
    image_hash = sha256(image_data).hexdigest()
    print(f"APOD SHA-256: {image_hash}")

    if get_apod_id_from_db(image_hash) == 0:
        print("APOD image is not already in cache.")
        file_path = determine_apod_file_path(apod_info['title'], apod_info['url'])
        print(f"APOD file path: {file_path}")
        print(f"Saving image file as {file_path}...", end="")
        if image_lib.save_image_file(image_data, file_path):
            print("success")
            return add_apod_to_db(apod_info['title'], apod_info['explanation'], file_path, image_hash)
        else:
            print("failed")
            return 0
    else:
        print("APOD image is already in cache.")
        return get_apod_id_from_db(image_hash)

def get_apod_info_from_api(apod_date):
    # Replace 'DEMO_KEY' with your actual API key
    api_url = f'https://api.nasa.gov/planetary/apod?date={apod_date}&api_key=tTiomB739fjkH8ZqpjiuuuS1Ql2xSWdzYnLDZH6K&thumbs=True'
    response = requests.get(api_url)
    if response.status_code == 200:
        apod_info = response.json()
        # Check if the APOD is a video and get the thumbnail URL
        url = apod_info.get('hdurl') if apod_info.get('media_type') == 'image' else apod_info.get('thumbnail_url')
        if not url:
            print("Error: No valid URL found for APOD.")
            return None
        return {
            'title': apod_info.get('title'),
            'explanation': apod_info.get('explanation'),
            'url': url
        }
    else:
        print(f"Failed to retrieve APOD information for {apod_date}. Status code: {response.status_code}")
        print(f"Error message: {response.text}")
        return None

def get_apod_id_from_db(image_sha256):
    conn = sqlite3.connect(image_cache_db)
    cursor = conn.execute("SELECT id FROM apod WHERE sha256=?", (image_sha256,))
    apod_id = cursor.fetchone()
    conn.close()
    return apod_id[0] if apod_id else 0

def determine_apod_file_path(image_title, image_url):
    sanitized_title = "".join([c if c.isalnum() else "_" for c in image_title.strip()])
    filename = sanitized_title + os.path.splitext(image_url)[-1]
    return os.path.join(image_cache_dir, filename)

def add_apod_to_db(title, explanation, file_path, sha256):
    conn = sqlite3.connect(image_cache_db)
    cursor = conn.execute("INSERT INTO apod (title, explanation, file_path, sha256) VALUES (?, ?, ?, ?)",
                          (title, explanation, file_path, sha256))
    conn.commit()
    apod_id = cursor.lastrowid
    conn.close()
    print("Adding APOD to image cache DB...success")
    return apod_id

def get_apod_info(apod_id):
    conn = sqlite3.connect(image_cache_db)
    cursor = conn.execute("SELECT title, explanation, file_path FROM apod WHERE id=?", (apod_id,))
    apod_info = cursor.fetchone()
    conn.close()
    if apod_info:
        return {'title': apod_info[0], 'explanation': apod_info[1], 'file_path': apod_info[2]}
    else:
        return None

if __name__ == '__main__':
    main()