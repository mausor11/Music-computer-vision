import speech_recognition as sr
from music_player_app import MusicPlayer, load_music

class GestureVoiceController:
    def __init__(self):
        self.music_player = MusicPlayer()

    def play_pause_music_by_gesture(self, gesture):
        if gesture == 'OPEN':
            self.music_player.play_music('PLAY')
        elif gesture == 'CLOSE':
            self.music_player.play_music('PAUSE')

    def set_music_by_saying_title(self, spotifyApi):
        recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source)

        try:
            print("Recognizing...")
            title = recognizer.recognize_google(audio)
            title = title.lower()

            title = title.split()
            print(f"You said: {title}")
            if title[0] == 'play':
                if title[1] == 'song':
                    title = ' '.join(title[2:])
                    spotifyApi.play_song_name(title)
                elif title[1] == 'album':
                    title = ' '.join(title[2:])
                    spotifyApi.play_album_name(title)
            else:
                print("Sorry, I did not understand that.")

        except Exception as e:
            print("Sorry, I did not understand that.")
            print(f"Exception: {e}")
