import tkinter
import sched, time
import pygame as pg
import librosa
import os

class SimpleLayoutApplication:
    def beat_time(self, param="default parameter"):
        print("From beat_time", time.time(), param)

    def __init__(self, filename):
        self.filename = filename
	
        self.height = 600
        self.width = 80
        self.delay = 50
        
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
            rect = ScheduledRectangle (int (float(line.strip())*1000) , self.delay, self.width, self.height,20)
            self._objects.append (rect)

        
        self._current_time = self._times.pop(0)	
        
    def _on_canvas_resized(self, event: tkinter.Event) -> None:
        canvas_width = self._canvas.winfo_width()
        for obj in self._objects:
            obj.coordinates['botRightX'] = canvas_width

        self.redrawAll() 

    def run(self):
        play_music (self.filename)
        self._root_window.after(self.delay, self.timerFired)
        self._root_window.mainloop()
    
    def test(self):
        print("Beat")
        old_time = self._current_time
        
        if len(self._times) != 0:
            self._current_time = self._times.pop(0)
            self._root_window.after(self._current_time - old_time, self.test)
    
    def timerFired (self):
        
        self._root_window.after (self.delay, self.timerFired)
        
        for object in self._objects:
            object.move()
        
        self.redrawAll ()

         
        #self._root_window.after (self.delay, self.timerFired)
    
    def redrawAll (self):
        self._canvas.delete("all")
        
        for object in self._objects:
            object.draw(self._canvas)
        
class MovingRectangle:
    def __init__ (self):
        self.coordinates = {}
        self.coordinates ['topLeftX'] = 0
        self.coordinates ['topLeftY'] = 0
        self.coordinates ['botRightX'] = 0
        self.coordinates ['botRightY'] = 0
        
        self.visibility = False
        
        self.color = 'blue'
        
        self.xSpeed = 0
        self.ySpeed = 10
        
    def setVisibility (self, flag):
        self.visibility = flag
    
    def setXSpeed (self, speed):
        self.xSpeed = speed
    def setYSpeed (self, speed):
        self.ySpeed = speed

    def move (self):
        self.coordinates ['topLeftX'] = self.coordinates ['topLeftX'] + self.xSpeed
        self.coordinates ['botRightX'] = self.coordinates ['botRightX'] + self.xSpeed
        
        self.coordinates ['topLeftY'] = self.coordinates ['topLeftY'] + self.ySpeed
        self.coordinates ['botRightY'] = self.coordinates ['botRightY'] + self.ySpeed
    
    def draw (self, canvas):
        if (self.visibility):
            canvas.create_rectangle(self.coordinates['topLeftX'], self.coordinates ['topLeftY'], self.coordinates['botRightX'], self.coordinates ['botRightY'], fill=self.color)
    

class ScheduledRectangle (MovingRectangle):
    def __init__ (self, endtime, delay, canvaswidth, canvasheight, ySpeed):
        MovingRectangle.__init__(self)
        self.coordinates ['topLeftY'] = 0
        self.coordinates ['botRightY'] = 1
        self.coordinates ['topLeftX'] = 0
        self.coordinates ['botRightX'] = canvaswidth
        
        self.setYSpeed (ySpeed)
        self.setXSpeed (0)
        
        self.startVisibility = (endtime - canvasheight *delay / self.ySpeed) / delay # Counter
        self.endVisibility = endtime/delay
    
    def move (self): 
        self.startVisibility -= 1
        self.endVisibility -= 1
        if (self.startVisibility < 0 and self.endVisibility > 0):
            super (ScheduledRectangle, self).move()
            self.setVisibility (True)

            print ("I am visible!")
        else:
            self.setVisibility (False)
        


################################################
# This code will play the music
def play_music(music_file, volume=0.8):
    '''
    stream music with mixer.music module in a blocking manner
    this will stream the sound from disk while playing
    '''
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
    '''
    pg.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag

    pg.init()

    pg.mixer.init()

    pg.mixer.music.load(music_file)

    pg.mixer.music.play(-1)
#play_music(filename)



#####################################


if __name__ == '__main__':
    
    filename = "test3.mp3"
        
    current_working_dir = os.getcwd()
    if not os.path.exists(current_working_dir + '/OnsetTimes/'):
        os.makedirs(current_working_dir + '/OnsetTimes/')

    if not os.path.exists(current_working_dir + '/OnsetTimes/' + filename + '.csv'):
        y, sr = librosa.load(filename)
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
        onset_times = librosa.frames_to_time(onset_frames, sr=sr) 
        librosa.output.times_csv(current_working_dir + '/OnsetTimes/' + filename +'.csv', onset_times)

    print('Starting to run the gui')
    SimpleLayoutApplication(filename).run()
