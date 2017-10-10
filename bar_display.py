import tkinter
import time
import pygame as pg
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib as mpl
import librosa
import librosa.display
import os
import csv
import matplotlib.backends.tkagg as tkagg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg

class SimpleLayoutApplication:


    def __init__(self, filename):
        
        self.testdelay = 0
        
        self.filename = filename
	
        self.height = 600
        self.width = 80
        self.delay = 17
        
        self._root_window = tkinter.Tk()

        self._canvas = tkinter.Canvas(
            master = self._root_window,width = self.width, height=self.height, background = '#%02x%02x%02x' % (127, 128, 0))

        self._pauseButton = tkinter.Button(text = 'Pause/Unpause', font = ('Comic Sans MS',20), command = self._on_pause_button_clicked)

        self._canvas.grid(
        row = 0, column = 0, padx = 5, pady = 5,
        sticky = tkinter.N + tkinter.S + tkinter.W + tkinter.E)

        self._pauseButton.grid(row = 1, column = 0, sticky = tkinter.N + tkinter.S + tkinter.W + tkinter.E)
        self._canvas.bind('<Configure>', self._on_canvas_resized)

        self._root_window.rowconfigure(0, weight = 1)
        self._root_window.columnconfigure(0, weight = 1)


        # Deals with the spectrogram
        f = open(os.getcwd() + '/SpectroInfo/' + self.filename + '.csv', 'r')
        reader = csv.reader(f)
        self.transposed = []
        
        for row in reader:
            self.transposed.append([float(val) for val in row])
        f.close()
        
        self.minimumVol = float(min([min(l) for l in self.transposed]))
        self.maximumVol = float(max([max(l) for l in self.transposed])) - self.minimumVol
        print(len(self.transposed[0]))
        
        # All objects the canvas is animating
        self._num_objects = 2
        self._objects = []
        length = self.width/self._num_objects
        for i in range (0, self._num_objects):
            maxheight = self.height
            xTopLeft = length*i
            yTopLeft = 0
            
            self._objects.append (SmallerRectangle (xTopLeft, yTopLeft, length, maxheight, i, self.maximumVol))

    def _on_canvas_resized(self, event: tkinter.Event) -> None:
        canvas_width = self._canvas.winfo_width()
        for obj in self._objects:
            obj.coordinates['botRightX'] = canvas_width

        self.redrawAll()

    def _on_pause_button_clicked(self) -> None:
        print("--------------------------PAUSE PRESSED----------------------------------")
        self.sounds.pause()

    
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
        
        samplesize = len ( self.transposed [framenumber] )
        
        for anobject in self._objects:
            startindex = samplesize*anobject (frequencynum)
            endindex = samplesize*anobject(frequencynum)+samplesize
            sum = 0
            for i in range (startindex, endindex):
                sum += self.transpoded [framenumber][i]
            ave = sum / (endindex-startindex) - self.minimumVol
            
            
            anobject.update(ave)
        
        self.redrawAll ()

         
        #self._root_window.after (self.delay, self.timerFired)
    
    def redrawAll (self):
        #self._canvas.delete("all")
        
        for object in self._objects:
            object.draw(self._canvas)


class Sound:
    def __init__(self):
       self.isPaused = False
    
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

    def pause(self):
        if not self.isPaused:
            pg.mixer.music.pause()
            self.isPaused = True
        else:
            pg.mixer.music.unpause()
            self.isPaused = False
    
    def get_position (self):
        return pg.mixer.music.get_pos()

    def isBusy(self):
        return pg.mixer.music.get_busy()



class SmallerRectangle:
    def __init__ (self, xTopLeft, yTopLeft, width, canvasheight, frequencynum, maxvolume):
        self.frequencynum = frequencynum
        self.width = width
        self.maxheight = canvasheight
        self.maxvolume = maxvolume
        self.currentvolume = 0
        
        self.x1 = xTopLeft
        self.y1 = yTopLeft
        self.x2 = self.x1+width
        self.y2 = self.y1 + (self.currentvolume /self.maxvolume) * self.maxheight
        self.color = 'blue'

    def update(volume):
        self.currentvolume = volume
        self.y2 = self.y1 + self.maxheight*(self.currentvolume/self.maxvolume)

    def draw (self, canvas):
        canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, fill=self.color)

    def get_frequency_num (self):
        return self.frequencynum
    

        





#####################################


if __name__ == '__main__':
    
    filename = "test.mp3"
    #filename = "lithium.flac"
    
    current_working_dir = os.getcwd()

    
    if not os.path.exists(current_working_dir + '/SpectroInfo/'):
        os.makedirs(current_working_dir + '/SpectroInfo/')
    
    if not os.path.exists(current_working_dir + '/SpectroInfo/'+filename+'.csv'):
        y, sr = librosa.load (filename)
        S = np.abs (librosa.stft(y))
        
        arr = librosa.power_to_db(S**2)
        transposearr = [list(i) for i in zip(*arr)]

        with open(current_working_dir + '/SpectroInfo/'+filename+'.csv', "w") as f:
            writer = csv.writer(f)
            writer.writerows(transposearr)


    print("Running gui")
    app = SimpleLayoutApplication(filename)
    app.run()

