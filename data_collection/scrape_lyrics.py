from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import csv

#function to scrape song names, artists featured on song, song url
def scrape_album_songs(artist, album):
    #url of album page
    url = f'https://genius.com/albums/{artist}/{album}'
    #request, parse html
    req = requests.get(url)
    html = BeautifulSoup(req.content, 'html.parser')
    #find all song names
    song_names = html.findAll('h3', {'class': "chart_row-content-title"})
    #find all song urls (for scraping lyrics)
    song_urls = html.findAll('a', {'class': 'u-display_block'})
    #list of song urls
    song_urls = [song['href'] for song in song_urls]
    #list of song names from HTML - includes featured artists
    song_names = [song.text for song in song_names]
    #cleanup song text - separate title and artists featured on track - returns (song_name, list of features)
    song_names = [(clean_song_name(song)) for song in song_names]
    #zip together (song_name, features) with song_url
    songs = list(zip(song_names, song_urls))
    #final list of artist, song_name, features, song_url
    songs = [(artist, song[0][0], song[0][1], song[1]) for song in songs]

    return songs

#function to clean HTML text from song name
def clean_song_name(song):
    features = None
    #clean new lines characters, Lyrics text, and Ft. text
    regex_first = re.compile('^(\n)( )*')
    regex_second = re.compile('(\n)( )*(Lyrics)(\n)*')
    regex_third = re.compile('(\(Ft.*)')

    #replace matching patterns from above with nothing
    song = re.sub(regex_first, '', song)
    song = re.sub(regex_second, '', song)
    song = re.sub(regex_third, '', song)
    #strip right whitespace
    song = song.rstrip()
    #search to find song containing (Ft. ...)
    feature_match = re.search(regex_third, song)

    if feature_match:
        #pullout matching (Ft....)
        features = feature_match.group(0)
        #remove (Ft, extra punctuation, whitespace and split into list)
        features = features.replace('Ft.','')
        features = features.replace('&', ',')
        features = features.replace(')','')
        features = features.replace('(','')
        features = features.split(',')
        features = [feature.replace('\xa0', ' ') for feature in features]
        features = [feature.strip() for feature in features]

    return (song, features)

#function to scrape lyrics into a csv
def scrape_lyrics_to_csv(artist, song_name, features, url):
    #request lyric page url
    req = requests.get(url)
    html = BeautifulSoup(req.content, 'html.parser')
    #get lyrics
    all_text = html.find('div', {'class': 'lyrics'}).text
    #split lyrics on new line
    lines = all_text.split('\n')
    #regex to find lines containing [] indicating unncessary information
    regex = re.compile('([\][])')
    #keep lines that do match regex and have len > 0
    lyrics = [line  for line in lines if len(line)> 0 and not regex.search(line)]
    #join lyrics into str
    lyrics_str = ' '.join(lyrics)
    #row to write to csv
    row = [[artist, song_name, lyrics_str, features]]
    #write to csv
    with open('lyrics.csv', 'a') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(row)

#function to run for multiple artist and album names
def scrape_all(list_of_artists_albums):
    #(artist, album_name)
    for artist_album in list_of_artists_albums:
        #prepare artist and album name for url on genius
        artist = artist_album[0].lower()
        artist = artist.replace(' ', '-')
        album = artist_album[1].lower()
        album = album.replace(' ', '-')
        songs = scrape_album_songs(artist, album)
        for song in songs:
            scrape_lyrics_to_csv(song[0], song[1], song[2], song[3])
