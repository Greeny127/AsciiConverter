import cv2 as cv #video reading
import imutils #resizing
import time #framerate limiter
from tqdm import tqdm #progress bar
import sys #command line args
from win32com.propsys import propsys #getting source fps

'''
args[0] main.py (ie the file name of the program)
args[1] source vide path (video.mp4)
args[2] grayscale (True False)
args[3] detail (maximum is 68)
args[4] width of video (essentially controls resolution)

-------------------------------------------------------

RECCOMENDED DETAIL LEVELS
For width 50 and below - 5
for width 100 and above - 68

-------------------------------------------------------

FULL PATH IS NEEDED FOR SOURCE VIDEO
win32com gives out an error of "file not found" if you don't give full path

-------------------------------------------------------

IN CASE FPS IS NOT FOUND IN SOURCE VIDEO
a try/except is set up to set fps by default
'''

class Ascii:
    def __init__(self, videopath, grayscale="True", detail=5, width=50, fps="60.00"):
        self.chars = ".'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
        self.path = videopath
        self.video = cv.VideoCapture(self.path)
        self.height = self.video.get(cv.CAP_PROP_FRAME_HEIGHT)
        self.width = width
        self.grayscale = grayscale
        self.detail = detail

        try:    
            self.properties = propsys.SHGetPropertyStoreFromParsingName(self.path)
            tfps = str(self.properties.GetValue(propsys.PSGetPropertyKeyFromName("System.Video.FrameRate")).GetValue()) #Had to scour through docs from the 90's for this ;-;
            tfps = tfps[:2] + "." + tfps[:2]
            self.fps = float(tfps)

        except Exception as e:
            self.fps = int(fps)
            print("An error occured so setting fps to {}".format(str(fps)))
            print("error - ", e)

    def getFrames(self):
        '''
        gets each frame and resizes
        '''
        frames = []
        success, image = self.video.read()
        count = 0
        while success:
            if self.grayscale == "True":    
                image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

            image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
            image = imutils.resize(image, width=self.width)
            self.height, self.width, _ = image.shape
            frames.append(image)
            success,image = self.video.read()
            count += 1

        return frames

    def __normalize(self, values, actual_bounds, desired_bounds):
        #MAGIC VOODO STUFF DO NOT TOUCH
        return [desired_bounds[0] + (x - actual_bounds[0]) * (desired_bounds[1] - desired_bounds[0]) / (actual_bounds[1] - actual_bounds[0]) for x in values]

    def convertAscii(self, frames):
        '''
        converts images to ascii through brightness and normalising
        '''
        newFrames = []
        for frame in tqdm(frames):
            newFrame = ""
            
            for x in range(int(self.height)):
                for y in range(int(self.width)):
                    b, g, r = frame[x, y]
                    brightness = sum([b, g, r])/3
                    char = self.chars[round(self.__normalize([brightness], (0, 255), (0, self.detail))[0])] * 2
                    newFrame += char 
                    
                newFrame += "\n"

            newFrames.append(newFrame)

        return newFrames

    def displayFrames(self, frames):
        '''
        displays frames with frame limiting
        '''
        duration = 1 / self.fps
        cursor_up = lambda lines: '\x1b[{0}A'.format(lines)
        
        for frame in frames:
            print(frame)
            time.sleep(duration)
            print(cursor_up(int(self.height) + 2)) #To overwrite the last printed frame (moves carriage to the top)

        return True

args = sys.argv

bot = Ascii(args[1], args[2], int(args[3]), int(args[4]))

print("Starting video reading")
frames = bot.getFrames()
print("Video reading done")

print("\nStarting ascii conversion")
frames = bot.convertAscii(frames)
print("Ascii conversion done")

print("\nStarting video in 2 seconds")
time.sleep(2)

video = bot.displayFrames(frames)