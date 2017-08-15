import tkinter
import sched, time

class SimpleLayoutApplication:
    def beat_time(self, param="default parameter"):
        print("From beat_time", time.time(), param)

    def __init__(self):
        self._root_window = tkinter.Tk()

        self._canvas = tkinter.Canvas(
            master = self._root_window, background = '#600000')
        
        self._times = []
        f = open('beat_times.csv', 'r')
        for line in f:
            self._times.append(int(float(line.strip())*1000))
        
        self._current_time = self._times.pop(0)	

    def run(self):
        self._root_window.after(self._current_time, self.test)
        self._root_window.mainloop()
    
    def test(self):
        print("Beat")
        old_time = self._current_time
        
        if len(self._times) != 0:
            self._current_time = self._times.pop(0)
            self._root_window.after(self._current_time - old_time, self.test)
if __name__ == '__main__':
    SimpleLayoutApplication().run()
