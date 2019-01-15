# import config
import requests
import pandas as pd

# songs = pd.read_csv('lyrics.csv')


# spotifyapi = config.spotify_api - update spotify api before running (expires)
spotifyapi = 'Bearer BQDS-AwWxW6ZbawlrBZgd5fcpiEz3vRQtFRWQkJnkgOXiHywUH5REvrjO_6xf0LPfGojkv7JATy4gqW3_BFTWX-s-psHM887ObzHPT3A69U5zivZgf1viQkCpVsaatZ6AZB4nP786xE0EXYFnfWz'

def get_spotify_track_id(artist, song):
    artist = artist.lower()
    artist = artist.replace(' ', '%20')
    song = song.lower()
    song = song.replace(' ', '%20')
    url = f'https://api.spotify.com/v1/search?q=track:{song}%20artist:{artist}%20&type=track&limit=1'
    headers = {"Authorization": f'{spotifyapi}',
                "Accept": "application/json", "Content-Type": "application/json"}
    req = requests.get(url, headers=headers)
    id = req.json()['tracks']['items'][0]['id']
    print(song, id)
    return id

def get_spotify_track_info(id):
    url = f'https://api.spotify.com/v1/audio-features/{id}'
    url_info = f'https://api.spotify.com/v1/tracks/{id}'
    headers = {"Authorization": f'{spotifyapi}',
                "Accept": "application/json", "Content-Type": "application/json"}
    req = requests.get(url, headers=headers)
    req_info = requests.get(url_info, headers=headers)
    isrc = req_info.json()['external_ids']['isrc']
    date = req_info.json()['album']['release_date']
    all_artists = req_info.json()['artists']
    featured_artists = [artist['name'] for artist in all_artists[1:]]
    json = req.json()
    json['isrc'] = isrc
    json['release_date'] = date
    json['featured'] = featured_artists
    return(json)

def add_spotify_to_df(songs):
    for idx, row in songs.iterrows():
        #test if api is not expired
        url = f'https://api.spotify.com/v1/audio-features/7yNK27ZTpHew0c55VvIJgm'
        headers = {"Authorization": f'{spotifyapi}',
                    "Accept": "application/json", "Content-Type": "application/json"}
        req = requests.get(url, headers=headers)
        try:
            req.json()['error']['status'] == 401
            #if expired
            print( 'Token Expired')
            break
        except:
            try:
                id = get_spotify_track_id(row['artist'],row['song'])
            except:
                id = 'failed'
            if id != 'failed':
                info = get_spotify_track_info(id)
                songs.loc[idx, 'danceability'] = info['danceability']
                songs.loc[idx, 'energy'] = info['energy']
                songs.loc[idx, 'loudness'] = info['loudness']
                songs.loc[idx, 'speechiness'] = info['speechiness']
                songs.loc[idx, 'liveness'] = info['liveness']
                songs.loc[idx, 'tempo'] = info['tempo']
                songs.loc[idx, 'valence']= info['valence']
                songs.loc[idx, 'isrc'] = info['isrc']
                songs.loc[idx, 'release_date'] = info['release_date']

            else:
                row['danceability'] = None
                row['energy'] = None
                row['loudness'] = None
                row['speechiness'] = None
                row['liveness'] = None
                row['tempo'] = None
                row['valence']= None
                row['isrc'] = None
                row['realease_date'] = None
                print(row['song'])
                print('failed')
    return songs

#to run 
#songs = pd.read_csv('lyrics.csv')
#songs = add_spotify_to_df(songs)
#songs.to_csv('./lyricspotify.csv')
