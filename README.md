# Personal Music Tracker 🎹

This project is a derivative of mainstreamer. I figured it would be interesting to see how my personal music taste changes over time, and also answer some questions I have related to music. 

## Tools

### Software 
- Python (spotipy, numpy, librosa, pandas, pyGithub, time, os, datetime)
- Jupyter Notebook (VS Code IDE)

### Deployment
My personal data is gathered using the attached script. It has been set to run daily using cron jobs on my iOS desktop.


## Background
Spotify possesses a "Popularity Index" - a score ranging from 0-100 for each song within its catalog. The index influences how songs are pushed into playlists/recommended to users. Any song with an index of 20+ is eligible for playlists and recommendations. The index is based on a variety of factors, determined using Spotify's rather detailed algorithm. 

Using this metric, I decided to assess what my music taste looks like on a daily basis by collecting the average score of all songs in my library on a daily basis. I chose the average as they can be influenced by outliers, and as not every song will have a high popularity, I wanted to capture the days where some songs in my library were more popular than others. 

## Questions to be Answered
- What is my average popularity index?
- What kind of music do I *truly* like? 
- Do popular songs have something that guarantees they will be popular?
- Do songs I *truly* like have something that guarantees I will like them?
- What do my favourite songs look like? 

# Set-Up
Using the `spotipy` python module, I created a script that fetches all the songs in my library, calculates the average, stores said average for the day, and updates GitHub with: 
- All songs in my library on a given day
```
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
```

- My most listened songs over a "long term", which spotify considers 1 year.
```
def get_user_top_tracks(user):
   try:
    results = user.current_user_top_tracks(limit=50, time_range="long_term")
    tracks = results['items']
    while results['next']:
        results = user.next(results)
        tracks.extend(results['items'])
        time.sleep(1)
    top_tracks = pd.DataFrame(tracks)[['id', 'name', 'popularity']]
    return top_tracks
   except (spotipy.exceptions.SpotifyBaseException, KeyboardInterrupt) as e: 
        print(f"Process was interrupted due to the following error: {e}")
```
- Average popularity score for 2 categories: All songs in library & Top 100 most listened songs
```
   most_listened_pop_score = round(np.average(top_tracks['popularity'][0:100]),2)
   med_song_duration = round(np.average(my_songs['song_duration'][0:100]),2)

```

## What is my Average Popularity Index? 
Based on the songs I listen to the most, my popularity index is displayed below: 

![Popularity Index Graph, based on Spotify's Popularity Algorithm](plots/Popularity%20Score%20Plot.png)

The higher a popularity score, the more people are listening to it. As my overall score is above 50, I think that means my music taste is fairly common. I think something that falls below 50 should be considered a rare taste in music. With mainstreamer, anyone who uses Spotify will be able to check, so maybe this person does exist! 


## Next Steps 
- Pretty much every function in the retrieval script could be sped up, so I will work on speeding each one up, which might include making requests to the spotify API directly. 
- Build this logic into an online app using the `streamlit` module, so anyone who uses spotify can get the same functionality. 
