import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO
import requests

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

        self.sp = spotipy.Spotify(auth_manager=self.sp_oauth)

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
            if results[f'{type}s']['items']:
                return results[f'{type}s']['items'][0]['uri']
            else:
                return None
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

    #   ARTIST FUNCTIONS - todo: limit top tracks in function arguments
    def get_artist_top_tracks(self, artist_uri):
        if artist_uri:
            return self.sp.artist_top_tracks(artist_uri)['tracks'][:5]
        else:
            return None

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

    # GUI FUNCTIONS - todo: now working how i want it to
    def get_album_tile(self, album_name):
        album_uri = self.get_item_uri('album', album_name)
        if album_uri:
            album_title = self.get_item_name('album', album_uri)
            album_cover = self.get_item_cover('album', album_uri)
            album_artist = self.get_item_artist('album', album_uri)
            album_features = self.get_item_features('album', album_uri)

            window = tk.Tk()
            window.title(album_title)
            response = requests.get(album_cover)
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            img_tk = ImageTk.PhotoImage(img)

            img_label = tk.Label(window, image=img_tk)
            img_label.image = img_tk
            img_label.pack()

            title_label = tk.Label(window, text=album_title)
            title_label.pack()

            if album_features:
                artists = album_artist['name']

                for feat in album_features:
                    artists += f", {feat['name']}"
                artist_label = tk.Label(window, text=artists)
            else:
                artist_label = tk.Label(window, text=album_artist['name'])

            artist_label.pack()

            window.mainloop()

    def get_artist_tile(self, artist_name):
        artist_uri = self.get_item_uri('artist', artist_name)
        if artist_uri:
            artist_name = self.get_item_name('artist', artist_uri)
            artist_cover = self.get_item_cover('artist', artist_uri)

            window = tk.Tk()
            window.title(artist_name)
            response = requests.get(artist_cover)
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            img_tk = ImageTk.PhotoImage(img)

            img_label = tk.Label(window, image=img_tk)
            img_label.image = img_tk
            img_label.pack()

            title_label = tk.Label(window, text=artist_name)
            title_label.pack()

            artist_label = tk.Label(window, text="Artist")
            artist_label.pack()
            for track in self.get_artist_top_tracks(artist_uri):
                track_uri = track['uri']
                track_name = track['name']
                track_artist = track['artists'][0]['name']
                track_button = tk.Button(window, text=f'{track_name}: {track_artist}',
                                         command=lambda track_u=track_uri: self.play_song(track_u))
                track_button.pack()
            window.mainloop()

    def get_playlist_tile(self, playlist_name='', playlist_uri=''):
        if not playlist_uri:
            playlist_uri = self.get_item_uri('playlist', playlist_name)

        if playlist_uri:
            playlist_name = self.get_item_name('playlist', playlist_uri)
            playlist_cover = self.get_item_cover('playlist', playlist_uri)
            playlist_owner = self.get_item_artist('playlist', playlist_uri)

            window = tk.Tk()
            window.title(playlist_name)
            response = requests.get(playlist_cover)
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            img_tk = ImageTk.PhotoImage(img)

            img_label = tk.Label(window, image=img_tk)
            img_label.image = img_tk
            img_label.pack()

            title_label = tk.Label(window, text=playlist_name)
            title_label.pack()

            owner_label = tk.Label(window, text=playlist_owner['display_name'])
            owner_label.pack()

            window.mainloop()

    def get_search_tile(self, name):
        if self.get_item_uri('artist', name):
            self.get_artist_tile(name)
        elif self.get_item_uri('album', name):
            self.get_album_tile(name)
        elif self.get_item_uri('playlist', name):
            self.get_playlist_tile(name)
        else:
            print('No search results found')
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


# spotifyApi = SpotifyAPI(os.getenv("CLIENT_ID"), os.getenv("CLIENT_SECRET"), os.getenv("REDIRECT_URI2"))
#
# spotifyApi.get_search_tile('CBW MIXTAPE 2')
