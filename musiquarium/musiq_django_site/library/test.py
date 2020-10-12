import os, sys, stat, subprocess
import pathlib
from detection_music import Detection, Database, musiq_detect_song
from add_songs import add_songs_to_database

BASE_DIR = pathlib.Path(__file__).resolve()
print(BASE_DIR.parents[1])
PATHS = os.path.join(BASE_DIR.parents[1].__str__(), 'media/')

print(PATHS)

songs = []

for subdir, dirs, files in os.walk('../media'):
     for file in files:
         print(file)
         if ( (os.path.join(subdir, file)).__str__().find(".mp3") != -1 ):
              songs.append(os.path.join(subdir, file))
              print((os.path.join(subdir, file)))
         else:
              print(f'Does not exist!')
#file = open(PATHS.__str__())

#os.chmod("./media/01 The Downfall Of Us All.mp3", stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
#subprocess.call(["attrib", "-r", PATHS])
for file_path in songs:
    if (os.path.isfile(file_path)):
        song_data = musiq_detect_song(Detection.AUDIO_FINGERPRINT, Database.MUSICBRAINZ, file_path)
        add_songs_to_database(song_data)
    else:
        print ("File not exist")

#for i in song_data:
#    print(f'{i[0]} - {i[1]} - {i[2]} - {i[3]}')
