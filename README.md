# Personal Music Tracker 🎹

This project is a derivative of mainstreamer. I figured it would be interesting to see how my personal music taste changes over time, and also answer some questions I have related to music. 




# Background
Spotify possesses a "Popularity Index" - a score ranging from 0-100 for each song within its catalog. The index influences how songs are pushed into playlists/recommended to users. Any song with an index of 20+ is eligible for playlists and recommendations. The index is based on a variety of factors, determined using Spotify's rather detailed algorithm. The higher a song's popularity score, the more people are listening to said song.

Using this metric, I decided to assess what my music taste looks like on a daily basis by collecting the average score of all songs in my library on a daily basis. I chose the average as they can be influenced by outliers, and as not every song will have a high popularity, I wanted to capture the days where some songs in my library were more popular than others. 

## Questions to be Answered
- What is my average popularity index?
- What kind of music do I *truly* like? 
- Do popular songs have something that guarantees they will be popular?
- Do songs I *truly* like have something that guarantees I will like them?
- What do my favourite songs look like? 

## Procedure
I created a wrapper for the Spotify API, using its documentation as a reference. This wrapper does the following: 
- Authenticates a User
- Gets User's account information
- Gathers total number of songs in a User's library
- Downloads all songs in a User's library
- Downloads top 1000 songs in a User's library

Download speed for all songs in a User's library was decreased from 80 to 331 songs/second by using a combination of the `dask` and `concurrent` modules. 
