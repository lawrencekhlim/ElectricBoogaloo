# Beat tracking example
from __future__ import print_function
import librosa

# 1. Get the file path to the included audio example
filename = "test.mp3"

# 2. Load the audio as a waveform `y`
#    Store the sampling rate as `sr`
y, sr = librosa.load(filename)

# 3. Run the default beat tracker
tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)


print('Estimated tempo: {:.2f} beats per minute'.format(tempo))



# 4. Convert the frame indices of beat events into timestamps
beat_times = librosa.frames_to_time(beat_frames, sr=sr)



print('Saving output to beat_times.csv')
librosa.output.times_csv('beat_times.csv', beat_times)



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

#####

s.run()
print (time.time())
