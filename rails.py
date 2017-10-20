import tkinter
import time
import pygame as pg
import numpy as np
import librosa
import os
import csv

class SimpleLayoutApplication:

    def initOnset (self):
        # All objects the canvas is animating
        self._objects = []
        
        
        self._times = []
        f = open(os.getcwd() + '/OnsetTimes/' + self.filename + '.csv', 'r')
        for line in f:
            self._times.append(int(float(line.strip())*1000))
            rect = MovingRectangle (int (float(line.strip())*1000) , 0, self.width, self.height,timetoReachBottom=4000)
            self._objects.append (rect)
    
        f.close()
    
    def setOnsetWidths(self):
        pass

    def partitionFrequencies(self):
        for i in range (0, self.num_rails):
            self.rails (Rail ( ))#stub

    def initSpectro (self):
        #Deals with the spectrogram
        f = open(os.getcwd() + '/SpectroInfo/' + self.filename + '.csv', 'r')
        reader = csv.reader(f)
        self.transposed = []
        
        for row in reader:
            self.transposed.append([float(val) for val in row])

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
        f.close()

    def initBeat (self):

        self._beat_times = []
        f = open(os.getcwd() + '/BeatInfo/' + self.filename + '.csv', 'r')
        for line in f:
            self._beat_times.append(int(float(line.strip())*1000))
        
        f.close()

    def __init__(self, filename):
        self.num_rails = 4
        self.rails = []
        
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

        self.initSpectro()


        self.initOnset()


        self.initBeat()
    
    
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
        
        self.updateBackground(currenttime)

        for anobject in self._objects:
            anobject.move(currenttime)
        
        self.redrawAll ()


        #self._root_window.after (self.delay, self.timerFired)
    
    def redrawAll (self):
        #self._canvas.delete("all")
        
        for object in self._objects:
            object.draw(self._canvas)

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
    def __init__(self, startFrequency, endFrequency, medianVol, startX, width, canvasheight, timeToReachBottom):
        self.startFrequency = startFrequency
        self.endFrequency = endFrequency
        self.medianVol = medianVol
        self.startX = startX
        self.width = width
        self.canvasheight = canvasheight
        self.timeToReachBottom = timeToReachBottom
        
        rectangles = []

    def addRectangle (self, onset):
        rectangles.append(MovingRectangle (onset, self.startX, self.width, self.canvasheight, self.timeToReachBottom))
    
    def moveRectangles (self, currenttime):
        for i in range (0, len (rectangles)):
            rectangles [i].move (currenttime)
    
    def drawRectangles (self, canvas):
        for i in range (0, len (rectangles)):
            rectangles [i].draw (canvas)

    def get_median_Volume (self):
        return self.medianVol




#####################################


if __name__ == '__main__':
    
    filename = "KoiNoShirushi.mp3"
    #filename = "test.mp3"
    #filename = "lithium.flac"
    
    current_working_dir = os.getcwd()
    if not os.path.exists(current_working_dir + '/OnsetTimes/'):
        os.makedirs(current_working_dir + '/OnsetTimes/')
    
    if not os.path.exists(current_working_dir + '/SpectroInfo/'):
        os.makedirs(current_working_dir + '/SpectroInfo/')

    if not os.path.exists(current_working_dir + '/BeatInfo/'):
        os.makedirs(current_working_dir + '/BeatInfo/')


    if not os.path.exists(current_working_dir + '/OnsetTimes/' + filename + '.csv'):
        y, sr = librosa.load(filename)
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
        onset_times = librosa.frames_to_time(onset_frames, sr=sr) 
        librosa.output.times_csv(current_working_dir + '/OnsetTimes/' + filename +'.csv', onset_times)
    
    if not os.path.exists(current_working_dir + '/SpectroInfo/'+filename+'.csv'):
        y, sr = librosa.load (filename)
        S = np.abs (librosa.stft(y))
        
        arr = librosa.power_to_db(S**2)
        transposearr = [list(i) for i in zip(*arr)]

        with open(current_working_dir + '/SpectroInfo/'+filename+'.csv', "w") as f:
            writer = csv.writer(f)
            writer.writerows(transposearr)

    if not os.path.exists(current_working_dir + '/BeatInfo/'+filename+'.csv'):
        y, sr = librosa.load (filename)
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        librosa.output.times_csv(current_working_dir + '/BeatInfo/' + filename +'.csv', beat_times)


    print("Running gui")
    app = SimpleLayoutApplication(filename)
    app.run()
