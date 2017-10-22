import pygame as pg

class AudioPlayer:
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