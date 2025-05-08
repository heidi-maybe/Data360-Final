# same code as the jupyter notebook just in a python file

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import pandas as pd


driver = webdriver.Safari()
driver.get("https://www.imdb.com/chart/moviemeter/?ref_=nv_mv_mpm")


last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
    time.sleep(2)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height


soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

results = soup.find('ul', class_='ipc-metadata-list ipc-metadata-list--dividers-between sc-e22973a9-0 khSCXM compact-list-view ipc-metadata-list--base')
movie_elements = results.find_all('li', class_="ipc-metadata-list-summary-item")

movie = []

for movie_element in movie_elements:
    genre = []
    title_element = movie_element.find("h3").text.strip()
    
    descr_elements = movie_element.find_all("span", class_="sc-4b408797-8 iurwGb cli-title-metadata-item") # If the release, time, and movie elements are returning none check the class name. It could have updated on the website.
    star_element = movie_element.find("span", class_="ipc-rating-star--rating")
    star_element = star_element.text.strip() if star_element else None
    link_element = movie_element.find("a")["href"]
    movie_url = "https://www.imdb.com" + link_element

    release_element = descr_elements[0].text.strip() if len(descr_elements) > 0 else None
    time_element = descr_elements[1].text.strip() if len(descr_elements) > 1 else None
    movie_element = descr_elements[2].text.strip() if len(descr_elements) > 2 else None

    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",}
        movie_page = requests.get(movie_url, headers=headers)
        movie_soup = BeautifulSoup(movie_page.content, "html.parser")

    
        genre_elements = movie_soup.find_all('a', class_="ipc-chip ipc-chip--on-baseAlt")
        for genre_element in genre_elements:
            genre_name = genre_element.find('span', class_="ipc-chip__text").text.strip()

            genre.append(genre_name)

    except:
        genre.append(None)
     
    movie.append([title_element, release_element, time_element, movie_element, star_element, genre, movie_url])

imdb_ranking = pd.DataFrame(movie, columns=["Title", "Release Date", "Run Time", "MPAA Film Rating", "Rating", "Genres", "Webpage"])
imdb_ranking_exploded = imdb_ranking.explode('Genres')

imdb_ranking.to_csv('imdb_ranking.csv', index=False)
imdb_ranking_exploded.to_csv('imdb_ranking_genres.csv', index=False)
