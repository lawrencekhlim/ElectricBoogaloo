import tkinter
import time
import pygame as pg
import numpy as np
import librosa
import os
import csv

import soundanalysis

class SimpleLayoutApplication:

    def initSoundAnalysis (self):
        self.soundanalysis = soundanalysis.SoundAnalysis()
        self.soundanalysis.analyze_sound(self.filename)
        self.initSpectro()
        self.initOnset()
        self.initBeat()
    
    
    
    
    def initOnset (self):
        f = self.soundanalysis.get_onset (self.filename)
        for line in f:
            self.addOnsetToRail(line)
    
    def addOnsetToRail(self, onset):
        # This function is called inside initOnset, and requires and onset
        # time and chooses which Rail(s) to add a rectangle to,
        # It needs to pick which Rail, and call the addRectangle function
        
        framenumber = librosa.time_to_frames([onset/1000]) [0]
        
        railAdded = False
        for rail in self._rails:
            total = 0
            ave = 0
            startFreq, endFreq = rail.getFrequencyRange()
            total += sum(self.transposed[framenumber][startFreq:endFreq])
            ave = total/(endFreq-startFreq)

            if ave > rail.getMedianVolume():
                if not railAdded:
                    rail.addRectangle(onset)
                    railAdded = True
                else:
                    if ave > rail.getMedianVolume() + (rail.getMaximumVolume() - rail.getMedianVolume())/5:
                        rail.addRectangle(onset)
                



    def partitionFrequencies(self):
        # This function is called inside initSpectro
        # It initializes each of the rails arrays with the correct parameters
        # The parameters it needs to calculate are:
        # width and x position
        # equally divided frequency ranges
        self.frequency_range = len (self.transposed [0])
        
        frequency_length = (int)(self.frequency_range/self.num_rails)
        
        rect_width = (int)(self.width/self.num_rails)
        for i in range (0, self.num_rails):
            self._rails.append (Rail (i*frequency_length, i*frequency_length+frequency_length, i*rect_width, rect_width, self.height, 4000))
            self._rails[i].calculateMedianVolume (self.transposed)

            self._rails[i].calculateMaxVolume(self.transposed)



    def initSpectro (self):
        #Deals with the spectrogram
        self.transposed = self.soundanalysis.get_spectro (self.filename)
        

        self.minimumVol = float(min([min(l) for l in self.transposed]))
        self.maximumVol = float(max([max(l) for l in self.transposed])) - self.minimumVol
        
        self.averageVol = 0
        noVolumeCount = 0
        for row in self.transposed:
            for val in row:
                if val != self.minimumVol:
                    self.averageVol += (val - self.minimumVol)
                else:
                    noVolumeCount += 1

        self.averageVol /= (len(self.transposed)*1025 - noVolumeCount)
        self.averageVol -= self.minimumVol
        self.averagepercent = int(100*(self.averageVol-self.minimumVol)/self.maximumVol)
        
        print(self.maximumVol)
        print(self.averageVol)
        print(self.averagepercent)
                    
        self.partitionFrequencies ()
    
    

    def initBeat (self):
        self._beat_times = self.soundanalysis.get_beat(self.filename)

    def __init__(self, filename):
        self.num_rails = 7
        self._rails = []
        
        self.testdelay = 0
        
        self.filename = filename
	
        self.height = 600
        self.width = 300
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

        self.initSoundAnalysis ()
    
    
    def _on_canvas_resized(self, event: tkinter.Event) -> None:
        '''
        canvas_width = self._canvas.winfo_width()
        for obj in self._rails:
            obj.coordinates['botRightX'] = canvas_width

        self.redrawAll()
        '''
        pass
    

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
        
        self.updateBackground(currenttime)

        for rail in self._rails:
            rail.moveRectangles(currenttime)
        
        self.redrawAll ()


        #self._root_window.after (self.delay, self.timerFired)
    
    def redrawAll (self):
        #self._canvas.delete("all")
        
        for rail in self._rails:
            rail.drawRectangles(self._canvas)

    def updateBackground (self, currenttime):
        framenumber = librosa.time_to_frames([currenttime/1000])
        
        currentmaximumvolume = max(self.transposed [framenumber[0]]) - self.minimumVol
        
        if currentmaximumvolume < self.averageVol:
            percentmaxvolume = int(50*(currentmaximumvolume/self.averageVol))
        else:
            percentmaxvolume = int(50 + (50*((currentmaximumvolume-self.averageVol)/(self.maximumVol-self.averageVol))))
        
        print("Vol    :", currentmaximumvolume)
        print("Ave Vol:", self.averageVol)
        print("Per Vol:", percentmaxvolume, "%")
        
        if percentmaxvolume <= 50:
            rgb = int(255*percentmaxvolume/50)
            rgbtuple = (rgb, 255, 0)
            #self._canvas.configure (background = '#%02x%02x%02x' % (rgb, 255, 0))
            #print("RGB    :", "(" + str(rgb) + ", " + str(255) + ", " + "0)")
        else:
            rgb = int(255*(percentmaxvolume-50)/50)
            rgbtuple = (255, 255-rgb, 0)
            #  self._canvas.configure (background = '#%02x%02x%02x' % (255, 255-rgb, 0))
            #print("RGB    :", "(" + str(255) + ", " + str(255-rgb) + ", " + "0)")
        
        closebeat = self.getClosestBeats (currenttime)
        percentage = self.scaleBetween (self.getPercentCloseToBeat(currenttime, closebeat), 0.25, 1)
        
        #rgbtuple = (255,0,0)
        rgbtuple = (int (rgbtuple[0]*percentage), int (rgbtuple [1] * percentage), int (rgbtuple[2]*percentage))
        
        self._canvas.configure (background = '#%02x%02x%02x' % (rgbtuple))

    def getClosestBeats (self, currenttime):
        i = 1
        arr = []
        while i < len(self._beat_times) and self._beat_times[i] < currenttime:
            i+=1
        if not (i < len (self._beat_times)):
            i-=1
        arr.append(self._beat_times[i-1])
        arr.append(self._beat_times[i])
        return arr

    def getPercentCloseToBeat (self, currenttime, closebeats):
        #halftime = (closebeats [1] - closebeats[0])/2
        halftime = (closebeats [1] - closebeats[0])
        return 1- np.abs(((currenttime-closebeats[0])%halftime)/halftime)
        #return np.abs(((currenttime-closebeats[0])%halftime)/halftime)

    def scaleBetween (self,percent, smaller, larger):
        diff = larger-smaller
        return smaller + diff * percent


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

class MovingRectangle:
    def __init__ (self, endtime, startingX, width, canvasheight, timetoReachBottom=1000):
        self.coordinates = {}
        self.coordinates ['topLeftX'] = startingX
        self.coordinates ['topLeftY'] = 0
        self.coordinates ['botRightX'] = width+startingX
        self.coordinates ['botRightY'] = 2
        
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
    

class Rail:
    def __init__(self, startFrequency, endFrequency, startX, width, canvasheight, timeToReachBottom):
        self.startFrequency = startFrequency # Index values of the array
        self.endFrequency = endFrequency
        self.medianVol = 0
        self.startX = startX
        self.width = width
        self.canvasheight = canvasheight
        self.timeToReachBottom = timeToReachBottom
        
        self.maxVolume = 0
        
        self.rectangles = []
    
    def calculateMedianVolume (self, spectroArray):
        total = 0
        frequencies = 0
        
        for frame in spectroArray:
            total += sum(frame)
            frequencies += len(frame)
        
        self.medianVol = total/frequencies

    def calculateMaxVolume(self, spectroArray):
        maximum = 0
        for frame in spectroArray:
            localmax = max(frame)
            if localmax > maximum:
                maximum = localmax

        self.maxVolume = maximum
        
    
    def addRectangle (self, onset):
        self.rectangles.append(MovingRectangle (onset, self.startX, self.width, self.canvasheight, self.timeToReachBottom))
    
    def moveRectangles (self, currenttime):
        for i in range (0, len (self.rectangles)):
            self.rectangles [i].move (currenttime)
    
    def drawRectangles (self, canvas):
        for i in range (0, len (self.rectangles)):
            self.rectangles [i].draw (canvas)

    def getMedianVolume (self):
        return self.medianVol
    
    def getMaximumVolume(self):
        return self.maxVolume
    
    def getFrequencyRange (self):
        return (self.startFrequency, self.endFrequency)





#####################################


if __name__ == '__main__':
    
    #filename = "KoiNoShirushi.mp3"
    #filename = "test.mp3"
     filename = "lithium.flac"
    

    app = SimpleLayoutApplication(filename)
    app.run()
