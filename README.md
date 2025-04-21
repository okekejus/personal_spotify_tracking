# Personal Music Tracker

This project is a derivative of mainstreamer. I figured it would be interesting to see how my personal music taste changes over time, and also answer some questions I have related to music. 

## Tools
### Modules
`streamlit, spotipy, pandas, numpy, pygithub, time, datetime, requests, dotenv`

## How common is my taste in music?  
Spotify possesses a "Popularity Index" - a score ranging from 0-100 for each song within its catalog. The index influences how songs are pushed into playlists/recommended to users. Any song with an index of 20+ is eligible for playlists and recommendations. The index is based on a variety of factors, determined using Spotify's rather detailed algorithm. 

Using this metric, I decided to assess what my music taste looks like on a daily basis by collecting the average score of all songs in my library on a daily basis. I chose the average as they can be influenced by outliers, and as not every song will have a high popularity, I wanted to capture the days where some songs in my library were more popular than others. 

Using the `spotipy` python module, I created a script that fetches all the songs in my library, calculates the average, stores said average for the day, and updates GitHub with: 
- All songs in my library on a given day
- Average popularity score for 2 categories: All songs in library & Top 100 most listened songs

Since its creation, my average popularity index has risen from 59 to 61 for all songs in my library. I am looking forward to see how this trend changes over time (I expect the number to increase steadily, if I am being completely honest). 

The resulting dataset is placed in an interactive line chart, and deployed via `streamlit`. The final product can be viewed here. 
## What kind of music do I *truly* like? 
## Do popular songs have something that guarantees they will be popular? 
## Do songs I *truly* like have something that guarantees I will like them? 
## What do my favourite songs look like? 
