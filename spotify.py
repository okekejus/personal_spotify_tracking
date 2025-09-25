import requests 
from dotenv import load_dotenv
import os 
from urllib.parse import urlencode
import base64 
import webbrowser
import datetime as dt
from datetime import timedelta
import time
from dask.delayed import delayed 
import dask
from dask.diagnostics.progress import ProgressBar
from concurrent.futures import ThreadPoolExecutor
from itertools import chain 
import json


load_dotenv()

class SpotifyUser(object):
    
    def __init__(self, my_dict):
        
        for key in my_dict:
            setattr(self, key, my_dict[key])


def encode_credentials(envClient:str, envSecret: str): 
    encoded_creds = base64.b64encode(envClient.encode() + b":" + envSecret.encode()).decode("utf-8")
    return encoded_creds

os.environ["encoded_creds"] = encode_credentials(os.getenv("SPOTIPY_CLIENT_ID"), os.getenv("SPOTIPY_CLIENT_SECRET"))


def fetch_auth_code(scope) -> str: 
    """ Fetch Authorization Code for initial authentication. Requires human interaction as Spotify doesn't allow for headless auth. """
    try: 
        auth_headers = {"client_id": os.getenv("SPOTIPY_CLIENT_ID"), 
                    "response_type": "code", 
                    "redirect_uri": os.getenv("SPOTIPY_REDIRECT_URI"), 
                    "scope": scope}
        webbrowser.open("https://accounts.spotify.com/authorize?" + urlencode(auth_headers))
        auth_code = input("Enter authorizaton code copied from browser: ")
        
    except Exception as e: 
        auth_code = f"Error occurred during code retrieval. {e.args}"
    return auth_code


def fetch_token(auth_code) -> dict: 
    """ After fetching the code, use this to fetch the access token that can be exchanged for user data."""
    try: 
        encoded_creds = os.getenv("encoded_creds")
        token_headers = {"Authorization": "Basic " + encoded_creds, 
                    "Content-Type": "application/x-www-form-urlencoded"}
        token_data = {"grant_type": "authorization_code", 
                    "code": auth_code, 
                    "redirect_uri": os.getenv("SPOTIPY_REDIRECT_URI")}
        
        obtained_at = dt.datetime.now()
        expires_at = obtained_at + timedelta(seconds=3600)
        req = requests.post("https://accounts.spotify.com/api/token", data=token_data, headers=token_headers)

        if req.status_code == 200:
            access_token:str = req.json()["access_token"]
            refresh_token:str = req.json()['refresh_token']
            os.environ["SP_ACCESS_TOKEN"] = access_token
            os.environ["SP_REFRESH_TOKEN"] = refresh_token
            os.environ["SP_EXPIRES_AT"] = str(expires_at)
            os.environ["SP_OBTAINED_AT"] = str(obtained_at)
            resp = {"access_token":access_token, "obtained_at": obtained_at, "expires_at": expires_at, "refresh_token": refresh_token}
        else: 
            resp = {"Error": req.json()['error_description']}# should probably just make into an exception
    except requests.exceptions.RequestException as e: 
        resp = {"Error": f"{e.args}"}
    return resp


def refresh_token() -> dict: 
    """ Using the refresh token to generate a new access token."""
    try: 
        encoded_creds = os.getenv("encoded_creds")
        header = {"Authorization": "Basic " + encoded_creds, 
                "Content-Type": "application/x-www-form-urlencoded"}
        params = {"grant_type": "refresh_token",
                  "refresh_token": os.getenv("SP_REFRESH_TOKEN")}
        resp = requests.post(url="https://accounts.spotify.com/api/token", data=params, headers=header)
        if resp.status_code == 200: 
            resp = resp.json()
            resp = json.loads(resp)
        else: 
            resp = {"Error code": resp.status_code, 
                    "reason": resp.reason}
             
    except requests.exceptions.RequestException as e: 
        resp = {"Error": str(e), 
                "details": e.args}
    return resp


def validate_token(): 
    """Checking the current access token for validity, updating if invalid """

    if dt.datetime.strptime(os.getenv("SP_EXPIRES_AT"), "%Y-%m-%d %H:%M:%S.%f") <= dt.datetime.now(): 
        token_details = refresh_token(os.getenv("SP_REFRESH_TOKEN"))
        return token_details
    else: 
        token_details = os.getenv("SP_ACCESS_TOKEN")
        return token_details
    
def get_user(): 
    try: 
        tk = validate_token()
        del tk 
        user_header = {"Authorization": "Bearer " + os.getenv("SP_ACCESS_TOKEN"), "Content-Type": "application/json"}
        user_response = requests.get("https://api.spotify.com/v1/me", headers=user_header).json()
    except Exception as e: 
        user_response ={"error": e.args}

    return user_response

@delayed
def fetch_song_page(link, limit) -> list:
    try: 
        tk = validate_token()
        del tk
        user_header = {"Authorization": "Bearer " + os.getenv("SP_ACCESS_TOKEN"), "Content-Type": "application/json"}
        user_params = {"limit":limit}
        user_tracks_response = requests.get(link, params=user_params, headers=user_header)
        t = user_tracks_response.json()["items"]
        n = [t[idx]['track'] for idx, val in enumerate(t)]
    except Exception as e: 
        n = [f"Error encountered during processing: {e.args}"]
    return n

def get_total_songs():
    """ Determine the total number of tracks in a user's library. """
    tk = validate_token()
    del tk
    try: 
        user_header = {"Authorization": "Bearer " + os.getenv("SP_ACCESS_TOKEN"), "Content-Type": "application/json"}
        user_params = {"limit":1} # shrink the limit because we do not need an entire response
        user_tracks_response = requests.get("https://api.spotify.com/v1/me/tracks", params=user_params, headers=user_header)
        t = user_tracks_response.json()["total"]
        return t
    except requests.exceptions.RequestException as e: 
        print(f"Error encountered during request: {e.args}")

def generate_link_list(offset:int, limit:int, library_size) -> list: 
    """Make a list of urls to senq a request to the server for. Captures user's entire library"""
    # Logic to figure out total number of links needed in request 
    
    library_size = {"total_songs": library_size,
                    "total_pages_int": library_size // 50, 
                    "total_songs_rem":library_size % 50, 
                    "total_songs_int": library_size-(library_size % 50)} # number of pages to be fetched based on limit, remainder, to be fetched after first value is hit (?) 
    track_links = []


    for pagenum in range(1, library_size["total_pages_int"]+1):

        if library_size["total_songs_rem"] > 0: 
            next_track_set = f'https://api.spotify.com/v1/me/tracks?offset={offset}&limit={limit}' 
            track_links.append(next_track_set)
            offset = offset + 50
            if offset == library_size["total_songs_int"]: 
                track_links.append(f"https://api.spotify.com/v1/me/tracks?offset={offset+library_size['total_songs_rem']}&limit={limit}")
        else: 
            next_track_set = f'https://api.spotify.com/v1/me/tracks?offset={offset}&limit={limit}' 
            track_links.append(next_track_set)
            offset = offset + 50
    return track_links

def generate_top_link_list(library_size): 
    

    if library_size == 0: 
        link_list = []
    elif 10 <= library_size <= 100: 
        link_list = ["https://api.spotify.com/v1/me/top/tracks?offset=0&limit=10"]
    elif 101 <= library_size <= 1000: 
        link_list = ["https://api.spotify.com/v1/me/top/tracks?offset=0&limit=50"]
        counter = 1 
        while counter < 2: 
            link = f"https://api.spotify.com/v1/me/top/tracks?offset={50}&limit=50"
            link_list.append(link)
            counter = counter + 1 
    else: 
        link_list = ["https://api.spotify.com/v1/me/top/tracks?offset=0&limit=50"]
        counter = 1 
        while counter < 20: 
            link = f"https://api.spotify.com/v1/me/top/tracks?offset={50*counter}&limit=50"
            link_list.append(link)
            counter = counter + 1 
        

    return link_list

 
def get_all_song_titles(link_list, limit, workers) -> list: 
    try: 
        with ThreadPoolExecutor(max_workers=4) as executor:
            tasks = [fetch_song_page(link, limit) for link in link_list]
            results = dask.compute(*tasks, scheduler="threads", num_workers=workers, pool=executor)
            all_tracks = list(chain.from_iterable(results))
    except Exception as e: 
        all_tracks = [f"Error encountered during retreival: {e.args}"]

    return all_tracks


def fetch_top_song_page(link, limit): 
    tk = validate_token()
    del tk
    try:
        user_header = {"Authorization": "Bearer " + os.getenv("SP_ACCESS_TOKEN"), "Content-Type": "application/json"}
        user_params = {"limit":limit}
        user_tracks_response = requests.get(link, params=user_params, headers=user_header)
        ok = user_tracks_response.json()['items']
        n = [ok[idx] for idx, val in enumerate(ok)]
    except Exception as e: 
        n = [f"Error: {e}"]
    
    return n


def get_all_top_song_titles(link_list, limit: int, workers) -> list: 
    try: 
        tk = validate_token()
        del tk
        with ThreadPoolExecutor(max_workers=4) as executor: 
            tasks = [fetch_top_song_page(link, limit) for link in link_list]
            results = dask.compute(*tasks, scheduler="threads", num_workers=workers, pool=executor) 
            all_top_tracks = list(chain.from_iterable(results))
    except Exception as e: 
        all_top_tracks =  [f"Error encountered during retreival: {e.args}"]
    return all_top_tracks
            
