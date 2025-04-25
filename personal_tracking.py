import pandas as pd
from dotenv import load_dotenv, dotenv_values
import json 
import os 
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import concurrent.futures
import time 
from spotipy.exceptions import SpotifyException
import numpy as np
import datetime as dt 
import requests 
from github import Github
from github import Auth
from github import GithubIntegration


def get_user_tracks(user): 
    try:
        results = user.current_user_saved_tracks(limit=50)
        tracks = results['items']
        while results['next']:
            results = user.next(results)
            tracks.extend(results['items'])
            time.sleep(1)
        my_songs_df = pd.DataFrame(tracks)

        song_titles = [value.get('name') for value in my_songs_df['track'].values]
        song_release = [track['album']['release_date'] for track in my_songs_df['track']]
        song_popularity = [value.get('popularity') for value in my_songs_df['track'].values]
        song_ids = [value.get('id') for value in my_songs_df['track'].values]
        song_duration = [round(value.get('duration_ms')/60000, 2) for value in my_songs_df['track'].values]
        extracts = pd.DataFrame({'song_name': song_titles, 'song_id':song_ids, 'song_popularity': song_popularity, 'song_release': song_release, 'song_duration': song_duration})

        return extracts
    except (spotipy.exceptions.SpotifyBaseException, KeyboardInterrupt) as e: 
        print(f"Process was interrupted due to the following error: {e}")

def get_user_top_tracks(user):
   try:
    results = user.current_user_top_tracks(limit=50, time_range="long_term")
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
        time.sleep(1)
    top_tracks = pd.DataFrame(tracks)[['id', 'name', 'popularity']]
    return top_tracks
   except (spotipy.exceptions.SpotifyBaseException, KeyboardInterrupt) as e: 
        print(f"Process was interrupted due to the following error: {e}")


def gather(user):
    my_songs = get_user_tracks(user)
    my_songs = my_songs.astype({'song_popularity': int})
    
    user_popularity_score = np.average(my_songs['song_popularity'])
    # getting the tracks a user most frequently listens to 
    
    top_tracks = get_user_top_tracks(user)
    most_listened_pop_score = round(np.average(top_tracks['popularity'][0:100]),2)
    med_song_duration = round(np.average(my_songs['song_duration'][0:100]),2)
    d = {"run_date": [rundate], 
        "total_songs": [len(my_songs['song_name'])], 
        "popularity_score": [user_popularity_score], 
        "most_listened_pop_score": [most_listened_pop_score], 
        "avg_song_duration": [med_song_duration]}

    addon = pd.DataFrame(d)
    try: 
        repo.create_file(path=f"daily_dumps/song_stats_{rundate}.csv", 
                    message=f"Adding song info for {rundate}", 
                    content=addon.to_csv(index=False))
        
        old = pd.read_csv("https://raw.githubusercontent.com/okekejus/personal_spotify_tracking/refs/heads/main/daily_dumps/song_stats.csv")
        new = pd.concat([old, addon])

        contents = repo.get_contents("song_list/all_songs.csv")
        repo.update_file(contents.path, "Song list as of {rundate}", my_songs.to_csv(index=False), contents.sha)

        contents = repo.get_contents("daily_dumps/song_stats.csv")
        repo.update_file(contents.path, f"Song stats updated {rundate}", new.to_csv(index=False), contents.sha)

        return True
    except Exception as e: 
        return (f"Procedure failed because of error: {e}")
    


def main(user_url = f"https://api.github.com/user", auth = Auth.AppAuthToken(os.getenv("GITHUB_PAT"))):
    g = Github(auth=auth)
    target_repo = [repo.id for repo in g.get_user().get_repos() if repo.name == "personal_spotify_tracking"]
    repo = g.get_repo(target_repo[0])
    
    
    # Setting things up for spotify interaction
    scope = "user-library-read playlist-read-private playlist-read-collaborative"
    sp = spotipy.Spotify(auth_manager = SpotifyOAuth(scope=scope))
    rundate = str(dt.date.today()) 
    
    gather(sp)


if __name__ == "__main__": 
    load_dotenv()
    main()
