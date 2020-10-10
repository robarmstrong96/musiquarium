# import os
# from pathlib import Path
#
# BASE_DIR = Path(__file__).resolve().parent.parent
#
# STATIC_URL = '/static/'
# STATICFILES_DIRS = (
#     os.path.join(BASE_DIR.__str__(), 'static'),
# )
# STATIC_ROOT = os.path.join(BASE_DIR.__str__(), 'staticfiles')
#
# print(STATICFILES_DIRS)

import os, sys, stat, subprocess
import pathlib
from detection_music import Detection, Database, musiq_detect_song

BASE_DIR = pathlib.Path(__file__).parent.absolute()
PATHS = os.path.join(BASE_DIR.__str__(), 'media/')

print(PATHS)

songs = []

for subdir, dirs, files in os.walk('media'):
     for file in files:
         if ( (os.path.join(subdir, file)).__str__().find(".mp3") != -1 ):
              songs.append(os.path.join(subdir, file))
              print((os.path.join(subdir, file)))
#file = open(PATHS.__str__())

#os.chmod("./media/01 The Downfall Of Us All.mp3", stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
#subprocess.call(["attrib", "-r", PATHS])
for file_path in songs:
    if (os.path.isfile(file_path)):
        song_data = musiq_detect_song(Detection.AUDIO_FINGERPRINT, Database.MUSICBRAINZ, file_path)
    else:
        print ("File not exist")

#for i in song_data:
#    print(f'{i[0]} - {i[1]} - {i[2]} - {i[3]}')
