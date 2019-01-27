# file to mearge all data sets and create new features
import pandas as pd
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import datetime
from datetime import date
import re
from zopfli.zlib import compress
from zlib import decompress

spotify_lyrics = pd.read_csv('./data/lyrics_spotify.csv')
missed = pd.read_csv('./data/lastfmmissed.csv')
lastfm = pd.read_csv('./data/lastfm.csv')

#remove extra columns
missed = missed[missed.columns[-8:]]


lastfm = lastfm[lastfm.columns[1:]]
last_fm_total = pd.concat([lastfm,missed])

#rename track-title to song for easy merging
last_fm_total = last_fm_total.rename(columns={'track-title':'song'})

#reformat artist name for merging
last_fm_total['artist'] = last_fm_total['artist'].apply(lambda x: x.lower())
last_fm_total['artist'] = last_fm_total['artist'].apply(lambda x: x.replace(' ', '-'))

spotify_lyrics.drop_duplicates(subset=['song'], keep='first', inplace=True)

#calc percentage of plays each song accounts for in album
final = spotify_lyrics.merge(last_fm_total, on=['song', 'artist'])
final['playcount_percentage'] = final.groupby('album')['playcount'].apply(lambda x: x/(x.sum()))
#if greater than 15% song is categorized as a hit
final['is_hit'] = final['playcount_percentage'] >= .15

#drop nans
final = final[~final['danceability'].isna()]
final = final[~final['lyrics'].isna()]

#drop albums that do not apply
final = final[~final.album.str.contains("Hits")]
final = final[~final.artist.str.contains("the-beatles")]
final = final[~final.artist.str.contains('michael-jackson')]

#function to count unique words in lyrics
def count_unique_words(lyrics):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(lyrics)
    no_stop_words_lyrics = [w for w in word_tokens if not w in stop_words]
    unique = set(no_stop_words_lyrics)
    return len(unique)

#add unique words column
for idx, row in final.iterrows():
  final.loc[idx, 'unique-words'] = count_unique_words(row['lyrics'])

#function calculates how much a song is compressed - 0 - least compressed 1 - most compreseed
def zopfli_compress(lyrics):
    return 1-len(compress(lyrics))/len(lyrics)

#add song repetetivness column
for idx, row in final.iterrows():
  final.loc[idx, 'repetetivness'] = zopfli_compress(row['lyrics'])


# #GET RID OF NULL DATES
# final = final[final.release_date.notnull()]
# for idx, row in final.iterrows():
#     final['today']=datetime.datetime.today().strftime('%Y-%m-%d')
# #calculate age of single
# final['age']=np.nan
# for idx, row in final.iterrows():
#     date=None
#     today=None
#     try:
#         date = datetime.datetime.strptime(final.loc[idx,'release_date'],"%Y-%m-%d")
#         today = datetime.datetime.strptime(final.loc[idx,'today'],"%Y-%m-%d")
#         final.loc[idx,'age']=abs((today-date).days)
#     except:
#         pass
# #calculate listeners/day
# final['list_day']=np.nan
# for idx,row in final.iterrows():
#     days=None
#     listnr=None
#     days=final.loc[idx,'age']
#     listnr=final.loc[idx, 'listeners']
#     final.loc[idx,'list_day']=listnr/days

#drop rows with null ages
# final = final[~final['age'].isna()]

feature_nums = final.drop(columns=['Unnamed: 0', 'artist', 'album', 'song','features',
                                   'lyrics', 'isrc', 'release_date',
                                   'single_release', 'is_hit', 'listeners', 'playcount', 'unique-words', 'track_no', 'playcount_percentage'])

target = final['is_hit']

#drop columns with a lot of correlation
 #Creating a correlation matrix
corr_matrix = feature_nums.corr().abs()

upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape),k=1).astype(np.bool))

#Creating a list of columns to drop with correlation > .95
to_drop = [column for column in upper.columns if any(upper[column]>0.95)]
feature_nums = feature_nums.drop(columns=to_drop)
