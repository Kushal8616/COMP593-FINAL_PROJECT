import requests
from datetime import date

API_KEY = 'tTiomB739fjkH8ZqpjiuuuS1Ql2xSWdzYnLDZH6K'  # Replace with your actual API key
BASE_URL = 'https://api.nasa.gov/planetary/apod'

def get_apod_info(apod_date):
    """
    Retrieve APOD information for a given date from NASA's API.
    
    :param apod_date: The date for which to retrieve the APOD (as a datetime.date object).
    :return: Dictionary containing APOD information or None if the request failed.
    """
    params = {
        'api_key': API_KEY,
        'date': apod_date.isoformat(),
        'thumbs': True
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    print(f"Error: Unable to retrieve APOD information. Status code: {response.status_code}")
    return None

def get_apod_image_url(apod_info_dict):
    """
    Get the appropriate image URL from the APOD information dictionary.
    
    :param apod_info_dict: Dictionary containing APOD information.
    :return: URL of the high-definition image or thumbnail image, depending on the media type, or None if not found.
    """
    if apod_info_dict['media_type'] == 'image':
        return apod_info_dict.get('hdurl')
    elif apod_info_dict['media_type'] == 'video':
        return apod_info_dict.get('thumbnail_url')
    print("Error: APOD media type is neither image nor video.")
    return None