import tkinter
import time
import pygame as pg
import numpy as np
import librosa
import os
import csv

class SimpleLayoutApplication:


    def __init__(self, filename):
        self.testdelay = 0
        
        self.filename = filename
	
        self.height = 600
        self.width = 80
        self.delay = 17
        
        self._root_window = tkinter.Tk()

        self._canvas = tkinter.Canvas(
            master = self._root_window,width = self.width, height=self.height, background = 'yellow')
        #self._canvas.pack()

        self._canvas.grid(
        row = 0, column = 0, padx = 5, pady = 5,
        sticky = tkinter.N + tkinter.S + tkinter.W + tkinter.E)

        self._canvas.bind('<Configure>', self._on_canvas_resized)

        self._root_window.rowconfigure(0, weight = 1)
        self._root_window.columnconfigure(0, weight = 1)

        # All objects the canvas is animating
        self._objects = []
        
        
        self._times = []
        f = open(os.getcwd() + '/OnsetTimes/' + self.filename + '.csv', 'r')
        for line in f:
            self._times.append(int(float(line.strip())*1000))
            rect = MovingRectangle (int (float(line.strip())*1000) , self.width, self.height,timetoReachBottom=4000)
            self._objects.append (rect)
        
        
        # Deals with the spectrogram
        y, sr = librosa.load(self.filename)
        S = np.abs(librosa.stft(y))
        arr = librosa.power_to_db(S**2)
        self.transposed = [list(i) for i in zip(*arr)]
        self.minimumVol = min(min(self.transposed))
        self.maximumVol = max(max(self.transposed))-self.minimumVol

        
    def _on_canvas_resized(self, event: tkinter.Event) -> None:
        canvas_width = self._canvas.winfo_width()
        for obj in self._objects:
            obj.coordinates['botRightX'] = canvas_width

        self.redrawAll() 

    def run(self):
        self.sounds = Sound ()
        self.sounds.play_music (self.filename)
        
        #play_music(self.filename)
        
        self._root_window.after(self.delay, self.timerFired)
        self._root_window.mainloop()


    
    def timerFired (self):
        
        self._canvas.delete("all")
        self._root_window.after (self.delay, self.timerFired)
        
        currenttime = self.sounds.get_position()
        #currenttime = get_position()
        print (currenttime)
        framenumber = librosa.time_to_frames([currenttime/1000])
        
        currentmaximumvolume = max(self.transposed [framenumber[0]])
        percentmaxvolume = int(100*((currentmaximumvolume-self.minimumVol)/self.maximumVol))
        print ((currentmaximumvolume-self.minimumVol))
        print (self.maximumVol)
        #print (percentmaxvolume)
        
        if (percentmaxvolume > 100):
            print ("------------------------------------------")
        
        self._canvas.configure (background = '#%02x%02x%02x' % (150, percentmaxvolume, percentmaxvolume))
        
        for anobject in self._objects:
            anobject.move(currenttime)
        
        self.redrawAll ()

         
        #self._root_window.after (self.delay, self.timerFired)
    
    def redrawAll (self):
        #self._canvas.delete("all")
        
        for object in self._objects:
            object.draw(self._canvas)


class Sound:
    def play_music(self, music_file, volume=0.5):
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
        pg.mixer.music.play(0)
        '''
        if not pg.mixer.music.get_busy():
            # check if playback has finished
            pg.mixer.music.play(0)
        '''
        '''
        pg.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag
    
        pg.init()

        pg.mixer.init()
    
        pg.mixer.music.load(music_file)
    
        pg.mixer.music.play(0)
        
        '''
            
    def get_position (self):
        return pg.mixer.music.get_pos()

    def isBusy(self):
        return pg.mixer.music.get_busy()

'''
    I am testing why some mp3 files work and others not with the following commented out code.

'''
'''
def play_music(music_file, volume=0.8):
    pg.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag
    
    pg.init()
    
    pg.mixer.init()
    
    pg.mixer.music.load(music_file)
    
    pg.mixer.music.play(0)

def get_position ():
    return pg.mixer.music.get_pos()

def isBusy():
    return pg.mixer.music.get_busy()
'''


class MovingRectangle:
    def __init__ (self, endtime, canvaswidth, canvasheight, timetoReachBottom=1000):
        self.coordinates = {}
        self.coordinates ['topLeftX'] = 0
        self.coordinates ['topLeftY'] = 0
        self.coordinates ['botRightX'] = 2
        self.coordinates ['botRightY'] = canvaswidth
        
        self.canvaswidth = canvaswidth
        self.canvasheight = canvasheight
        
        self.visibility = False
        
        self.color = 'blue'
        self.timeToReachBottom = timetoReachBottom
    
        self.endVisibility = endtime # In milliseconds
        self.startVisibility = endtime - timetoReachBottom # In millliseconds
    
        
    def setVisibility (self, flag):
        self.visibility = flag
    

    def move (self, currenttime):
        
        if (self.endVisibility-currenttime > self.timeToReachBottom or self.endVisibility-currenttime < 0):
            self.setVisibility(False)
        else:
            #print ("I am visible!")
            
            self.setVisibility (True)
            self.coordinates ['topLeftX'] = self.coordinates ['topLeftX']
            self.coordinates ['botRightX'] = self.coordinates ['botRightX']
        
        
            self.coordinates ['topLeftY'] = self.canvasheight - self.canvasheight * (self.endVisibility-currenttime)/self.timeToReachBottom
            self.coordinates ['botRightY'] = self.coordinates ['topLeftY'] + 2
    
    def draw (self, canvas):
        if (self.visibility):
            canvas.create_rectangle(self.coordinates['topLeftX'], self.coordinates ['topLeftY'], self.coordinates['botRightX'], self.coordinates ['botRightY'], fill=self.color)
    

        





#####################################


if __name__ == '__main__':
    
    #filename = "KoiNoShirushi.mp3"
    #filename = "test.mp3"
    filename = "discord.mp3"
    # For whatever reason, on betteranimation.py it can not play test2.py or test3.py, but can play test.py and other mp3 files.
    # Currently investigating this.
    
    current_working_dir = os.getcwd()
    if not os.path.exists(current_working_dir + '/OnsetTimes/'):
        os.makedirs(current_working_dir + '/OnsetTimes/')
    '''
    if not os.path.exists(current_working_dir + '/SpectroInfo/'):
        os.makedirs(current_working_dir + '/SpectroInfo/')
    '''
    if not os.path.exists(current_working_dir + '/OnsetTimes/' + filename + '.csv'):
        y, sr = librosa.load(filename)
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
        onset_times = librosa.frames_to_time(onset_frames, sr=sr) 
        librosa.output.times_csv(current_working_dir + '/OnsetTimes/' + filename +'.csv', onset_times)
    '''
    if not os.path.exists(current_working_dir + '/SpectroInfo/'+filename+'.csv'):
        y, sr = librosa.load (filename)
        S = np.abs (librosa.stft(y))
        
        arr = librosa.power_to_db(S**2)
        transposearr = [list(i) for i in zip(*arr)]
        
        
        os.makedirs(current_working_dir + '/SpectroInfo/')
    '''
    print('Starting to run the gui')
    app = SimpleLayoutApplication(filename)
    app.run()
