import requests

def fetch_us_states():
    url = "https://api.entrenandolatinosinroofing.com/api/v1/states/?format=json"

    try:
        resp = requests.get(url, timeout=8)

        resp.raise_for_status()

        data = resp.json()

        # Validar que la API devolvió una lista
        if not isinstance(data, list):
            print("ERROR: API no devolvió una lista:", data)
            return []

        estados = []

        for item in data:
            name = item.get("name")
            code = item.get("geoname_code") or item.get("slug")

            if name and code:
                estados.append({"name": name, "code": code})

        return estados

    except Exception as e:
        print("ERROR FETCH API:", str(e))
        return []
