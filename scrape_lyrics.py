from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import csv

def scrape_album_songs(artist, album):

    url = f'https://genius.com/albums/{artist}/{album}'
    req = requests.get(url)
    html = BeautifulSoup(req.content, 'html.parser')
    song_names = html.findAll('h3', {'class': "chart_row-content-title"})
    song_urls = html.findAll('a', {'class': 'u-display_block'})
    song_urls = [song['href'] for song in song_urls]
    song_names = [song.text for song in song_names]
    song_names = [(clean_song_name(song)) for song in song_names]
    songs = list(zip(song_names, song_urls))
    songs = [(artist, song[0][0], song[0][1], song[1]) for song in songs]

    return songs

def clean_song_name(song):
    features = None
    regex_first = re.compile('^(\n)( )*')
    regex_second = re.compile('(\n)( )*(Lyrics)(\n)*')
    regex_third = re.compile('(\(Ft.*)')
    feature_match = re.search(regex_third, song)
    if feature_match:
        features = feature_match.group(0)
        features = features.replace('Ft.','')
        features = features.replace('&', ',')
        features = features.replace(')','')
        features = features.replace('(','')
        features = features.split(',')
        features = [feature.replace('\xa0', ' ') for feature in features]
        features = [feature.strip() for feature in features]

    song = re.sub(regex_first, '', song)
    song = re.sub(regex_second, '', song)
    song = re.sub(regex_third, '', song)
    song = song.rstrip()
    return (song, features)

def scrape_lyrics_to_csv(artist, song_name, features, url):
    req = requests.get(url)
    html = BeautifulSoup(req.content, 'html.parser')
    all_text = html.find('div', {'class': 'lyrics'}).text
    lines = all_text.split('\n')
    regex = re.compile('([\][])')
    lyrics = [line  for line in lines if len(line)> 0 and not regex.search(line)]

    lyrics_str = ' '.join(lyrics)
    row = [[artist, song_name, lyrics_str, features]]
    with open('lyrics.csv', 'a') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(row)

def scrape_all(list_of_artists_albums):
    for artist_album in list_of_artists_albums:
        artist = artist_album[0].lower()
        artist = artist.replace(' ', '-')
        album = artist_album[1].lower()
        album = album.replace(' ', '-')
        songs = scrape_album_songs(artist, album)
        for song in songs:
            scrape_lyrics_to_csv(song[0], song[1], song[2], song[3])
