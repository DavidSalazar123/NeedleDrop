import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import math
from selenium import webdriver
import re
HOME = "https://www.youtube.com/user/theneedledrop/videos"


def scroll():
    """
    scrolls to the bottom of the page
    code taken from https://stackoverflow.com/questions/20986631/how-can-i-scroll-a-web-page-using-selenium-webdriver-in-python
    modified slightly for YouTube
    """
    SCROLL_PAUSE_TIME = 0.5

    last_height = driver.execute_script("return window.scrollY")

    tries = 0
    while True:
        down_height = last_height + 1000
        driver.execute_script("window.scrollTo(0," + str(down_height) + ")")

        time.sleep(SCROLL_PAUSE_TIME)

        new_height = driver.execute_script("return window.scrollY")
        if new_height == last_height:
            tries += 1
            time.sleep(SCROLL_PAUSE_TIME)
            if tries == 50:
                break
        else:
            tries = 0
        last_height = new_height


# Scrape for videos
driver = webdriver.Chrome("C:\webdriver\chromedriver.exe")
driver.get(HOME)

scroll()
element_titles = driver.find_elements_by_id("video-title")

# Creation of the data
row = []
GENRE_PATTERN = re.compile("[^\/](19|20)\d{2}\s\/.*")
PATTERN = re.compile('(?<=shortDescription":").*(?=","isCrawlable)')
for element in element_titles:
    title = element.text

# Not Good and Classics are included within this data
# Change code to get the description of video instead
    try:
        if "review" in title.lower() and "track review" not in title.lower() and "yunoreview" not in title.lower() and "weekly track" not in title.lower():

            # Get Description of video
            soup = BeautifulSoup(requests.get(
                element.get_attribute("href")).content)
            description = PATTERN.findall(
                str(soup))[0].replace('\\n', '\n').lower()

            # Get Score of the video
            # Prevents word classification to not be included (Classic, meh, Not Good)
            score = re.search(
                "[^201]\n\d{0,2}\/10", description).group().strip("\n").split("/")[0]

            # Get the Genre
            genre = GENRE_PATTERN.search(description).group()

            # Get the year the album dropped
            album_date = GENRE_PATTERN.search(
                description).group().split("/")[0].strip()

            # Date of when the video was published
            video_date = soup.find("meta", itemprop="datePublished")['content']

            row.append([title, genre, album_date, video_date, score])
            print([title, genre, album_date, video_date, score])
    except Exception:
        pass

music_data = pd.DataFrame(
    row, columns=["Title", "Genre", "Album_Date", "Video_Date", "Score"])

# Save the music data to csv
music_data.to_csv("..\NeedleDrop\music_data.csv")
