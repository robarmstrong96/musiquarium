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
PATHS = os.path.join(BASE_DIR.__str__(), 'media\\01 The Downfall Of Us All.mp3')

print(PATHS)

#file = open(PATHS.__str__())

#os.chmod("./media/01 The Downfall Of Us All.mp3", stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
subprocess.call(["attrib", "-r", PATHS])
if (os.path.isfile(PATHS)):
    song_data = musiq_detect_song(Detection.AUDIO_FINGERPRINT, Database.MUSICBRAINZ, PATHS)
else:
    print ("File not exist")

#for i in song_data:
#    print(f'{i[0]} - {i[1]} - {i[2]} - {i[3]}')
