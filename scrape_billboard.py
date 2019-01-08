import requests
import re
from bs4 import BeautifulSoup

billboard_url = 'https://www.billboard.com/charts/year-end/2018/top-billboard-200-albums'

def scrape_billboard_albums(url):
    req = requests.get(url)
    html = BeautifulSoup(req.content, 'html.parser')

    artists_albums = html.findAll('div', {'class':'ye-chart-item__text'})

    albums = [album.find('div', {'class': 'ye-chart-item__title'}).text for album in artists_albums]
    artists = [artist.find('div', {'class': 'ye-chart-item__artist'}).text for artist in artists_albums]

    regex = re.compile('\n+')

    albums_clean = [re.sub(regex, '', album) for album in albums]
    artists_clean = [re.sub(regex, '', artist) for artist in artists]

    artists_albums_clean = list(zip(artists_clean,albums_clean))

    return artists_albums_clean
