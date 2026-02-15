import re
import urllib.parse
import requests

def extract_lat_long_from_url(url):
    """
    Extracts latitude and longitude from a Google Maps URL.
    Supports various formats, including short links (maps.app.goo.gl).
    """
    try:
        # Resolve short URLs if needed
        if 'goo.gl' in url or 'g.page' in url:
            try:
                response = requests.get(url, allow_redirects=True, timeout=5)
                url = response.url
            except Exception as e:
                print(f"Error resolving short URL: {e}")

        # 1. Look for @lat,long pattern (common in /maps/place/ URLs)
        match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', url)
        if match:
            return float(match.group(1)), float(match.group(2))

        # 2. Look for q=lat,long param (common in search URLs)
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        if 'q' in params:
            # q can be "10.1234,76.5678" or "Place Name"
            q_val = params['q'][0]
            # Check if q looks like coordinates
            coord_match = re.match(r'^(-?\d+\.\d+),(-?\d+\.\d+)', q_val)
            if coord_match:
                return float(coord_match.group(1)), float(coord_match.group(2))
        
        # 3. Handle search/ syntax: /maps/search/10.1234,+76.5678
        match_search = re.search(r'/search/(-?\d+\.\d+),\+?(-?\d+\.\d+)', url)
        if match_search:
            return float(match_search.group(1)), float(match_search.group(2))

        # 4. Handle ?ll=lat,long (older format)
        if 'll' in params:
            ll_val = params['ll'][0]
            coord_match = re.match(r'^(-?\d+\.\d+),(-?\d+\.\d+)', ll_val)
            if coord_match:
                return float(coord_match.group(1)), float(coord_match.group(2))

        return None, None
    except Exception as e:
        print(f"Error extracting coordinates: {e}")
        return None, None
