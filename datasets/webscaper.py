import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from pytube import YouTube
import re
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
HOME = "https://www.youtube.com/user/theneedledrop/videos"
GENRE_PATTERN = re.compile("[^\/](19|20)\d{2}\s\/.*")


def scroll():
    SCROLL_PAUSE_TIME = 1
    last_height = driver.execute_script(
        "return document.documentElement.scrollHeight")

    while True:
        driver.execute_script(
            "window.scrollTo(0,document.documentElement.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script(
            "return document.documentElement.scrollHeight")
        if new_height == last_height:
            time.sleep(3)
            break
        last_height = new_height


# Webdriver to scrape youtube video
data = []

# Options
options = webdriver.ChromeOptions()
options.add_argument("--disable-extensions")
options.add_argument("--disable-notifications")
options.add_argument("--disable-Advertisement")
options.add_argument("--disable-popup-blocking")
options.add_argument("start-maximized")
s=Service(r"C:\webdriver\chromedriver.exe")
driver= webdriver.Chrome(service=s,options=options)
driver.get(HOME)

time.sleep(3)
scroll()

try:
    for e in WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div#details'))):
        vurl = e.find_element(
            By.CSS_SELECTOR, 'a#video-title-link').get_attribute('href')
        data.append({
            'video_url': vurl,
        })
except:
    pass
df = pd.DataFrame(data).drop_duplicates()
df.to_csv('./ytlinks.csv')

print("Starting to scrape Youtube videos...")
# Creation of the data
# WARNING: Takes long time
musicdataDF = pd.DataFrame(columns=["Title", "Description", "VidLength", "Views", "PublishDate","Genre"])
df = pd.read_csv('./ytlinks.csv')
link_list = df['video_url']
KEYWORDS = ['track review', 'yunoreview', 'weekly track']
for link in link_list:
    try:
        video = YouTube(link)
        title = video.title.lower()
        if title not in KEYWORDS and "review" in title:
            description = video.description
            row = {"Title": title, "Description": description, "VidLength": video.length, "Views": video.views,"PublishDate": video.publish_date, "Genre": GENRE_PATTERN.search(description).group()}
            musicdataDF = musicdataDF.append(row, ignore_index=True)
    except Exception:
        pass

musicdataDF.to_csv('./reviews_videos.csv')
