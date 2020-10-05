import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

PATHS = os.path.join(BASE_DIR.__str__(), 'media')

files = os.listdir(PATHS)

for item in files:
    print(item)

# import detection_music, os, system
#
# song_data = musiq_detect_song(Detection.AUDIO_FINGERPRINT, Database.MUSICBRAINZ, "./media/")
#
# for i in song_data:
#     print(f'{i[0]} - {i[1]} - {i[2]} - {i[3]}')
