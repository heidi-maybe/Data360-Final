import streamlit as st
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import re 

st.set_page_config(page_title="IMDb 100", layout="wide")

st.title("IMDb 100 Most Popular Movies")
st.write("Information from May 4, 2025.") # When the csv's were made.

data = pd.read_csv('imdb_ranking.csv', dtype={'Release Date': str, 'Rating': float}) # Original data
data2 = pd.read_csv('imdb_ranking_genres.csv', dtype={'Release Date': str, 'Rating': float}) # Same data just with Genres column exploded.

tab1, tab2 = st.tabs(["Data Table and Filter", "Data Visualization"])
with tab1:
    # Genre Search Toggle
    st.header("Filter movies with genre information or without information.")
    col1, col2, col3 = st.columns([0.2,0.2,0.4])
    with col1:
        st.text("Genre Selector:") # add a text 
    with col2:
        toggleGenre = st.checkbox('Toggle Genre Search', value=0)

    if toggleGenre:
        st.subheader("Either search for a title or choose a genre to see movies.")

    # Checkboxs to filter the MPAA Film Rating
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([0.3,0.2,0.2,0.2,0.2,0.2,0.3,0.4])
    with col1:
        st.text("MPAA Film Rating:") # add a text 
    with col2:
        pg = st.checkbox('PG', value=1)
    with col3:
        pg_13 = st.checkbox('PG-13', value=1)
    with col4:
        r = st.checkbox('R', value=1)
    with col5:
        tv_14 = st.checkbox('TV-14', value=1)
    with col6:
        tv_ma = st.checkbox('TV-MA', value=1)
    with col7:
        missing = st.checkbox('Not Rated Yet', value=1)

    if not pg:
        data = data.query("`MPAA Film Rating` != 'PG'")
    if not pg_13:
        data = data.query("`MPAA Film Rating` != 'PG-13'")
    if not r:
        data = data.query("`MPAA Film Rating` != 'R'")
    if not tv_14:
        data = data.query("`MPAA Film Rating` != 'TV-14'")
    if not tv_ma:
        data = data.query("`MPAA Film Rating` != 'TV-MA'")
    if not missing:
        data = data.dropna(subset=['MPAA Film Rating'])

    # Selector for Release Date and Slider for Rating with toggle turn on
    col1, col2, col3, col4 = st.columns([0.2,0.2,0.2,0.4])
    with col1:
        release_list = data['Release Date'].unique()
        release_list = np.sort(release_list)[::-1]
        release_list = np.insert(release_list, 0, "All Release Dates")
        release = st.selectbox(label="Choose a release date:", options=release_list)
    with col2:
        st.text("Rating Slider:") # add a text 
    with col3:
        toggle = st.checkbox('Toggle Rating Slider', value=0)

    if release != "All Release Dates":
        data = data.query("`Release Date` == '{}'".format(release))

    if toggle:
        rating = st.slider('Rating', min_value=0.0, max_value=10.0, value=(0.0,10.0))
        data = data.query(f'{rating[0]} <= Rating <= {rating[1]}')

    # Search box for Title
    col1, col2 = st.columns([0.4,0.4])
    with col1:
        text_box = st.text_input('Search for a title')

    if text_box != "":
        data = data.query("Title == '{}'".format(text_box))

    if toggleGenre:
        # MPAA Film Rating with genre
        if not pg:
            data2 = data2.query("`MPAA Film Rating` != 'PG'")
        if not pg_13:
            data2 = data2.query("`MPAA Film Rating` != 'PG-13'")
        if not r:
            data2 = data2.query("`MPAA Film Rating` != 'R'")
        if not tv_14:
            data2 = data2.query("`MPAA Film Rating` != 'TV-14'")
        if not tv_ma:
            data2 = data2.query("`MPAA Film Rating` != 'TV-MA'")
        if not missing:
            data2 = data2.dropna(subset=['MPAA Film Rating'])

        # Release Date with genre
        if release != "All Release Dates":
            data2 = data2.query("`Release Date` == '{}'".format(release))

        # Release Date with genre 
        if toggle:
            rating = st.slider('Rating', min_value=0.0, max_value=10.0, value=(0.0,10.0))
            data2 = data2.query(f'{rating[0]} <= Rating <= {rating[1]}')

        # Title Search with genre
        if text_box != "":
            data2 = data2.query("Title == '{}'".format(text_box))["Genres"]
            st.dataframe(data2, hide_index=True, column_config={"Webpage": st.column_config.LinkColumn(display_text="Read More")})
        else:
            # Search per Genre
            col1, col2 = st.columns([0.2,0.4])
            with col1:
                genre_list = data2['Genres'].unique()
                genre_list = np.sort(genre_list)
                genre_list = np.insert(genre_list, 0, "Choose a Genre")
                genre = st.selectbox(label="Choose a genre:", options=genre_list)
            if genre:
                data2 = data2.query("Genres == '{}'".format(genre))
            st.write("Missing information inside of the \"Run Time\", \"MPAA Film Rating\", or \"Rating\" columns mean the movie has yet to be release.")
            st.dataframe(data2, hide_index=True, column_config={"Webpage": st.column_config.LinkColumn(display_text="Read More")})
    else:
        st.write("Missing information inside of the \"Run Time\", \"MPAA Film Rating\", or \"Rating\" columns mean the movie has yet to be release.")
        # displaying Original data without the genre column and clickable URL link to each movies page.
        df = pd.DataFrame(data, columns=["Title", "Release Date", "Run Time", "MPAA Film Rating", "Rating", "Webpage"])
        st.dataframe(df, hide_index=True, column_config={"Webpage": st.column_config.LinkColumn(display_text="Read More")})

with tab2:
    # Trend of popular movies vs their release date
    st.subheader("View the trend of number of popular movies per release date.")

    df_graph2 = data.groupby('Release Date')['Title'].count().sort_index()

    fig = plt.figure(figsize=(8,3))
    plt.plot(df_graph2.index, df_graph2.values, marker='o', linestyle='-')
    plt.xticks(rotation=45, ha='right')
    plt.xlabel('Release Date')
    plt.ylabel('Total Popular Movies')
    plt.title('Total Popular Movies per Release Date')
    st.pyplot(fig)

    # Viewing average rating of each genre by release year
    st.subheader("View movie genre average rating by year.")

    df_graph = data2.groupby(['Release Date', 'Genres'])['Rating'].mean().reset_index().dropna(subset="Rating")
    df_graph = df_graph.sort_values(by="Release Date", ascending=True)

    release_list_graph = data['Release Date'].unique()
    release_list_graph = np.sort(release_list_graph)

    release_graph = st.selectbox(label="Select release date:", options=release_list_graph)
    
    
    mask = df_graph['Release Date'] == release_graph

    fig = plt.figure(figsize=(8,3))
    plt.bar(df_graph[mask]['Genres'], df_graph[mask]['Rating'], width=0.4)
    plt.xticks(rotation=45, ha='right', fontsize=5)
    plt.ylim(0, 10)
    plt.xlabel('Genres')
    plt.ylabel('Average Rating')
    plt.title('Average Rating of Movie Genres per Release Date')
    st.pyplot(fig)
