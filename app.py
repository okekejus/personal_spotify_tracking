import streamlit as st 
import pandas as pd 
import datetime as dt

my_songs = pd.read_csv("https://raw.githubusercontent.com/okekejus/personal_spotify_tracking/refs/heads/main/daily_dumps/song_stats.csv")
rundate = dt.date.today()
my_songs["popularity_score"] = round(my_songs["popularity_score"], 4)

header = st.container()
mstrm_over_time = st.container()


with header: 
    h_col1, h_col2, h_col3 = st.columns(3)
    h_col2.write(f"#Personal Mainstream Score - Updated {rundate}")



with mstrm_over_time: 
    st.line_chart(data=my_songs, x="run_date", y=["popularity_score", "most_listened_pop_score"], x_label = "Date", y_label = "Mainstream Score")