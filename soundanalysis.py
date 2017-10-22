import os
import csv
import librosa
import numpy as np

class SoundAnalysis:
    
    def __init__ (self):
        self.current_working_dir = os.getcwd()
    
    def setup_dir (self):
        if not os.path.exists(self.current_working_dir + '/OnsetTimes/'):
            os.makedirs(self.current_working_dir + '/OnsetTimes/')

        if not os.path.exists(self.current_working_dir + '/SpectroInfo/'):
            os.makedirs(self.current_working_dir + '/SpectroInfo/')
    
        if not os.path.exists(self.current_working_dir + '/BeatInfo/'):
            os.makedirs(self.current_working_dir + '/BeatInfo/')



    def analyze_sound (self, filename):
        self.analyze_onsets (filename)
        self.analyze_spectrogram (filename)
        self.analyze_beat_times (filename)
    
    def analyze_onsets (self, filename):
        if not os.path.exists(self.current_working_dir + '/OnsetTimes/' + filename + '.csv'):
            y, sr = librosa.load(filename)
            onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
            onset_times = librosa.frames_to_time(onset_frames, sr=sr)
            librosa.output.times_csv(self.current_working_dir + '/OnsetTimes/' + filename +'.csv', onset_times)

    def analyze_spectrogram (self, filename):
        if not os.path.exists(self.current_working_dir + '/SpectroInfo/'+filename+'.csv'):
            y, sr = librosa.load (filename)
            S = np.abs (librosa.stft(y))
        
            arr = librosa.power_to_db(S**2)
            transposearr = [list(i) for i in zip(*arr)]
            
            with open(self.current_working_dir + '/SpectroInfo/'+filename+'.csv', "w") as f:
                writer = csv.writer(f)
                writer.writerows(transposearr)

    def analyze_beat_times (self, filename):
        if not os.path.exists(self.current_working_dir + '/BeatInfo/'+filename+'.csv'):
            y, sr = librosa.load (filename)
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
            beat_times = librosa.frames_to_time(beat_frames, sr=sr)
            librosa.output.times_csv(self.current_working_dir + '/BeatInfo/' + filename +'.csv', beat_times)

    def get_onset (self, filename):
        # All objects the canvas is animating

        self.onset_times = []
        f = open(os.getcwd() + '/OnsetTimes/' + filename + '.csv', 'r')
        for line in f:
            self.onset_times.append (int(float(line.strip())*1000))
        f.close()
        return self.onset_times
        

    def get_spectro (self, filename):
        #Deals with the spectrogram
        f = open(os.getcwd() + '/SpectroInfo/' + filename + '.csv', 'r')
        reader = csv.reader(f)
        self.transposed = []
    
        for row in reader:
            self.transposed.append([float(val) for val in row])
        f.close()
        return self.transposed

    def get_beat (self, filename):

        self.beat_times = []
        f = open(os.getcwd() + '/BeatInfo/' + filename + '.csv', 'r')
        for line in f:
            self.beat_times.append(int(float(line.strip())*1000))
        
        f.close()
        return self.beat_times

