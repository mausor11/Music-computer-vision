import base64
import json
import webbrowser

from flask import Flask, request, url_for, session, redirect
import time

from requests import post
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

load_dotenv()


class SpotifyAPI:
    def __init__(self, client_id, client_secret, redirect_uri):

        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.sp_oauth = SpotifyOAuth(client_id=self.client_id,
                                     client_secret=self.client_secret,
                                     redirect_uri=self.redirect_uri,
                                     scope="user-library-read, "
                                           "user-top-read, "
                                           "user-read-playback-state, "
                                           "user-modify-playback-state,"
                                           "user-read-recently-played,"
                                           "user-follow-read")
        self.token_info = self.sp_oauth.get_cached_token()
        if not self.token_info:
            self.authorize()
        self.sp = spotipy.Spotify(auth=self.token_info['access_token'])

    def authorize(self):
        auth_url = self.sp_oauth.get_authorize_url()
        webbrowser.open(auth_url)
        response = input("Paste the above link into your browser, then paste the redirect url here: ")
        code = self.sp_oauth.parse_response_code(response)
        self.token_info = self.sp_oauth.get_access_token(code)

    def get_token(self):
        auth_string = self.client_id + ":" + self.client_secret
        auth_bytes = auth_string.encode('utf-8')
        auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": "Basic " + auth_base64,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}
        result = post(url, headers=headers, data=data)
        json_result = json.loads(result.content)
        token = json_result["access_token"]
        return token

    def get_auth_headers(self, token):
        return {
            "Authorization": "Bearer " + token
        }

    def reset_authorization(self):
        self.sp_oauth.cache_handler.clear()
        self.token_info = None
        self.authorize()

    #   PLAYBACK FUNCTIONS
    def play_song(self, song_uri):
        self.sp.start_playback(uris=[song_uri])

    def pause_song(self):
        self.sp.pause_playback()

    def resume_song(self):
        self.sp.start_playback()

    def skip_song(self):
        self.sp.next_track()

    def previous_song(self):
        self.sp.previous_track()

    def get_current_song(self):
        return self.sp.current_playback()

    def playback_volume(self, volume):
        self.sp.volume(volume)

    #   ITEM FUNCTIONS
    def get_item_uri(self, type=None, item_name=None, limit=1):
        if type == 'track' or type == 'album' or type == 'artist' or type == 'playlist':
            results = self.sp.search(q=f'{type}:' + item_name, type=f'{type}', limit=limit)
            return results[f'{type}s']['items'][0]['uri']
        else:
            return None

    def get_item_json(self, type=None, item_uri=None, item_name=None):
        type_to_func = {
            'track': self.sp.track,
            'album': self.sp.album,
            'artist': self.sp.artist,
            'playlist': self.sp.playlist
        }

        if type in type_to_func:
            if item_uri is None:
                item_uri = self.get_item_uri(type, item_name)
            return type_to_func[type](item_uri)
        else:
            return None

    def get_item_name(self, type=None, item_uri=None):
        type_to_func = {
            'track': self.sp.track,
            'album': self.sp.album,
            'artist': self.sp.artist,
            'playlist': self.sp.playlist
        }

        if type in type_to_func:
            return type_to_func[type](item_uri)['name']
        else:
            return None

    def get_item_artist(self, type=None, item_uri=None):
        type_to_func = {
            'track': self.sp.track,
            'album': self.sp.album,
        }

        if type in type_to_func:
            return type_to_func[type](item_uri)['artists'][0]
        elif type == 'playlist':
            return self.sp.playlist(item_uri)['owner']
        else:
            return None

    def get_item_features(self, type=None, item_uri=None):
        type_to_func = {
            'track': self.sp.track,
            'album': self.sp.album,
        }

        if type in type_to_func:
            return type_to_func[type](item_uri)['artists'][1:]
        else:
            return None

    def get_item_duration(self, type=None, item_uri=None):

        if type == 'track':
            return self.sp.track(item_uri)['duration_ms']
        elif type == 'album':
            total_duration = 0
            for track in self.get_album_tracks(item_uri):
                total_duration += track['duration_ms']
            return total_duration
        else:
            return None

    def get_item_cover(self, type=None, item_uri=None):
        if type == 'track':
            return self.sp.track(item_uri)['album']['images'][0]['url']
        elif type == 'album':
            return self.sp.album(item_uri)['images'][0]['url']
        elif type == 'artist':
            return self.sp.artist(item_uri)['images'][0]['url']
        elif type == 'playlist':
            return self.sp.playlist(item_uri)['images'][0]['url']
        else:
            return None

    #   ALBUM FUNCTIONS
    def get_album_tracks(self, album_uri):
        return self.sp.album_tracks(album_uri)['items']

    #   SEARCH FUNCTIONS
    def get_recently_played(self, limit):
        return self.sp.current_user_recently_played(limit=limit)

    def get_liked_albums(self, limit):
        return self.sp.current_user_saved_albums(limit=limit)

    def get_playlists(self, limit):
        return self.sp.current_user_playlists(limit=limit)

    def get_liked_artists(self, limit):
        return self.sp.current_user_followed_artists(limit=limit)

    def play_song_name(self, song_name):
        results = self.sp.search(q='track:' + song_name, type='track', limit=1)
        track_uri = results['tracks']['items'][0]['uri']
        self.sp.start_playback(uris=[track_uri])

    def play_album_name(self, album_name):
        results = self.sp.search(q='album:' + album_name, type='album', limit=1)
        if 'albums' in results and results['albums']['items']:
            album_uri = results['albums']['items'][0]['uri']
            self.sp.start_playback(context_uri=album_uri)
        else:
            print(f"No albums found for '{album_name}'")

    # recently_played = spotifyApi.get_recently_played(5)['items']
    # for song in recently_played:
    #     print(song['track']['name'])

    # liked_albums = spotifyApi.get_liked_albums(5)['items']
    # for album in liked_albums:
    #     print(album['album']['name'])

    # playlists = spotifyApi.get_playlists(5)['items']
    # for playlist in playlists:
    #     print(playlist['name'])

    # liked_artists = spotifyApi.get_liked_artists(5)['artists']['items']
    # for artist in liked_artists:
    #     print(artist['name'])


spotifyApi = SpotifyAPI(os.getenv("CLIENT_ID"), os.getenv("CLIENT_SECRET"), os.getenv("REDIRECT_URI"))