# Beat tracking example
from __future__ import print_function
import librosa
import IPython.lib.display as player 
import pygame as pg


# 1. Get the file path to the included audio example
filename = "test.mp3"

# 2. Load the audio as a waveform `y`
#    Store the sampling rate as `sr`
y, sr = librosa.load(filename)
player.Audio(filename = filename)
# 3. Run the default beat tracker
tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)


print('Estimated tempo: {:.2f} beats per minute'.format(tempo))



# 4. Convert the frame indices of beat events into timestamps
beat_times = librosa.frames_to_time(beat_frames, sr=sr)



print('Saving output to beat_times.csv')
librosa.output.times_csv('beat_times.csv', beat_times)


################################################
# This code will play the music
def play_music(music_file, volume=0.8):
    '''
    stream music with mixer.music module in a blocking manner
    this will stream the sound from disk while playing
    '''
    # set up the mixer
    freq = 44100     # audio CD quality
    bitsize = -16    # unsigned 16 bit
    channels = 2     # 1 is mono, 2 is stereo
    buffer = 2048    # number of samples (experiment to get best sound)
    pg.mixer.init(freq, bitsize, channels, buffer)
    # volume value 0.0 to 1.0
    pg.mixer.music.set_volume(volume)
    clock = pg.time.Clock()
    try:
        pg.mixer.music.load(music_file)
        print("Music file {} loaded!".format(music_file))
    except pg.error:
        print("File {} not found! ({})".format(music_file, pg.get_error()))
        return
    pg.mixer.music.play()
    while pg.mixer.music.get_busy():
        # check if playback has finished
        clock.tick(30)
#play_music(filename)



#####################################
# This code will schedule beats

import sched, time
s = sched.scheduler (time.time, time.sleep)


def beat_time (param="default parameter"):
     print ("From beat_time", time.time(), param)

f = open ("beat_times.csv", "r")
for line in f:
     s.enter (float(line), 1, beat_time, argument=("Beat",))
     print ("Entered into scheduler ", float (line))

f.close()

##### Testing ways of playing sound


#from playsound import playsound

#import subprocess

#sound_program = "/Applications/iTunes.app"

#import webbrowser

#import vlc
#p = vlc.MediaPlayer (filename)


##### 


print (time.time())

p.play()

##### Testing ways of playing sound 2

#playsound (filename, block =False)
#subprocess.call ( [ sound_program, filename] )
#webbrower.open (filename)

play_music(filename)

#####

s.run()
print (time.time())
