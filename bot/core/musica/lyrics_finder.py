from lyricsgenius import Genius
import os

GENIUS_API_TOKEN = os.getenv('GENIUS_API_TOKEN')

genius = Genius(GENIUS_API_TOKEN)

def get_song_lyrics(song_title):

    song = genius.search_song(song_title)

    if not song:
        return "Nenhuma música encontrada."

    lyrics = song.lyrics

    return song.title, lyrics

def split_lyrics(lyrics_text, max_length=4096):

    return [lyrics_text[i:i + max_length] for i in range(0, len(lyrics_text), max_length)]