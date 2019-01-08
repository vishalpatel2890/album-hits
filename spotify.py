import config
import requests
import pandas as pd

# songs = pd.read_csv('lyrics.csv')


# spotifyapi = config.spotify_api
spotifyapi = 'Bearer BQAiZZWB4TYwfTHgFlolqUVo2FkhIJAH22hz2QXd9lJwMlsbh5Rq5r_0-RmlOBgmA1A3S-avnKv76P0NagMxRtXEFxDmyl31g9a49O8WfAGqvkFuauptGcT2gpzR7ih43Vmab9swpVbuTcrdfaKY'

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
        url = f'https://api.spotify.com/v1/audio-features/7yNK27ZTpHew0c55VvIJgm'
        headers = {"Authorization": f'{spotifyapi}',
                    "Accept": "application/json", "Content-Type": "application/json"}
        req = requests.get(url, headers=headers)
        try:
            req.json()['error']['status'] == 401
            print( 'Token Expired')
            break
        except:
            try:
                id = get_spotify_track_id(row['artist'],row['song'])
            except:
                id = 'failed'
            if id != 'failed':
                info = get_spotify_track_info(id)
                row['danceability'] = info['danceability']
                row['energy'] = info['energy']
                row['loudness'] = info['loudness']
                row['speechiness'] = info['speechiness']
                row['liveness'] = info['liveness']
                row['tempo'] = info['tempo']
                row['valence']= info['valence']
                row['isrc'] = info['isrc']
                row['release_date'] = info['release_date']
                print(row)
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
                print('failed')
    return songs
