# Personal Music Tracker 🎹

This project is a derivative of mainstreamer. I figured it would be interesting to see how my personal music taste changes over time, and also answer some questions I have related to music. 

## Tools
### Software 
- GitHub
- Python
- Jupyter Notebook (VS Code IDE)
### Modules
`streamlit, spotipy, pandas, numpy, pygithub, time, datetime, requests, dotenv`

### Deployment
My personal data is gathered using the attached script. I run the script each day at 1AM, using [Python Anywhere](https://www.pythonanywhere.com/) - that way I don't have to worry about it. I am aware there are other cloud options, but this is the cheapest + most straight forward for this purpose.

## How common is my taste in music?  
Spotify possesses a "Popularity Index" - a score ranging from 0-100 for each song within its catalog. The index influences how songs are pushed into playlists/recommended to users. Any song with an index of 20+ is eligible for playlists and recommendations. The index is based on a variety of factors, determined using Spotify's rather detailed algorithm. 

Using this metric, I decided to assess what my music taste looks like on a daily basis by collecting the average score of all songs in my library on a daily basis. I chose the average as they can be influenced by outliers, and as not every song will have a high popularity, I wanted to capture the days where some songs in my library were more popular than others. 

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

Since its creation, my average popularity index has risen from 59 to 61 for all songs in my library. I am looking forward to see how this trend changes over time (I expect the number to increase steadily, if I am being completely honest). 

The higher a popularity score, the more people are listening to it. As my overall score is a 61, I think that means my music taste is fairly common. I think something that falls below 50% should be considered a rare taste in music. With mainstreamer, anyone who uses Spotify will be able to check, so maybe this person does exist! 

My personal data will be plotted using `streamlit`. 
I also aim to answer the following questions: 
- What kind of music do I *truly* like? 
- Do popular songs have something that guarantees they will be popular?
- Do songs I *truly* like have something that guarantees I will like them?
- What do my favourite songs look like? 
