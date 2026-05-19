import requests

ART_API = "https://api.artic.edu/api/v1/artworks"


def fetch_artwork(external_id):
    url = f"{ART_API}/{external_id}"
    r = requests.get(url)

    if r.status_code != 200:
        return None

    return r.json().get("data")