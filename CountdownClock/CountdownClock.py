import time,board,displayio
from adafruit_matrixportal.keypad import Keypad
from adafruit_matrixportal.matrixportal import MatrixPortal

# Pins for the LED panel
CLK=board.D11
OE=board.D9
LAT=board.D10
A=board.A0
B=board.A1
C=board.A2
D=board.A3

# Initialize matrix setup. "double_buffer" enables double-buffering, which keeps the animation from flickering
# The "64" is there because this is a 32x64 matrix
matrix=MatrixPortal(
    width=64,
    height=32,
    gpio=displayio.FourWire(CLK,LAT,A,B,C,D),
)

# Setting up text
str="BLASTOFF"  # Scrolling text string
textX=matrix.display.width  # Width of the matrix for text string
textMin=len(str)*-12  # Setting number of columns at the right side after the last letter before we reset the scrolling pattern
hue=0   # Hue to start at zero

# Defining our pins for the keypad
numROWS=4
numCOLS=4
keys=[
    ['1','2','3','A'],
    ['4','5','6','B'],
    ['7','8','9','C'],
    ['*','0','#','D']
]
rowPins=[board.D40,board.D41,board.D42,board.D43]
colPins=[board.D44,board.D45,board.D46,board.D47]

# Initialize keypad
keypad=Keypad.make_keymap(keys,rowPins,colPins,numROWS,numCOLS)

# States for the timer
class TimerState:
    SETTING=0
    RUNNING=1
    PAUSED=2

startTime=0  # Start time when the timer begins
countDownTime=0  # Countdown time in MM:SS

timerState=TimerState.SETTING  # Initialize the timer state to SETTING

def settingTimer():
    global startTime,countDownTime,timerState

    while(True):
        minutes=countDownTime//100
        seconds=countDownTime%100
        timeStr="{:02d}:{:02d}".format(minutes,seconds)

        # Prints the desired time
        matrix.display.fill(0)
        matrix.display.text(timeStr,x=3,y=9,color=0xFFFFFF)
        matrix.display.show()

        key=keypad.read()
        if(key is not None):
            # Checks if 'A' is pressed to start the timer
            if(key=='A' and countDownTime>0):
                timerState=TimerState.RUNNING
                startTime=time.monotonic()
                break
            # Checks if 'C' is pressed to reset the timer
            elif(key=='C'):
                countDownTime=0
            # Checks if 'D' is pressed to backspace
            elif(key=='D' and countDownTime>0):
                countDownTime//=10
            # Checks if a number is pressed
            elif('0'<=key<='9' and countDownTime<=999):
                countDownTime=countDownTime*10+int(key)

def runningTimer():
    global countDownTime,timerState

    minutes=countDownTime//100
    seconds=countDownTime%100
    countDownTimeS=(minutes*60)+seconds

    while(True):
        # Calculates the remaining time on the timer
        currentTime=time.monotonic()
        timeRemaining=countDownTimeS-currentTime-startTime

        if(timeRemaining>6039000):
            displayBlastoffText()
            break

        minutes=timeRemaining//60
        seconds=timeRemaining%60
        timeStr="{:02d}:{:02d}".format(minutes,seconds)

        # Prints remaining time
        matrix.display.fill(0)
        matrix.display.text(timeStr,x=3,y=9,color=0xFFFFFF)
        matrix.display.show()

        key=keypad.read()
        if(key is not None):
            # Checks if 'B' is pressed to pause the timer
            if(key=='B'):
                timerState=TimerState.PAUSED
                countDownTime=minutes*100+seconds
                break
            # Checks if 'C' is pressed to reset the timer
            elif(key=='C'):
                timerState=TimerState.SETTING
                startTime=0
                countDownTime=0
                break

def pausedTimer():
    global startTime,timerState

    minutes=countDownTime//100
    seconds=countDownTime%100
    timeStr="{:02d}:{:02d}".format(minutes,seconds)

    # Prints the paused time
    matrix.display.fill(0)
    matrix.display.text(timeStr,x=3,y=9,color=0xFFFFFF)
    matrix.display.show()

    while(True):
        key=keypad.read()
        if(key is not None):
            # Checks if 'A' is pressed to resume the timer
            if(key=='A'):
                timerState=TimerState.RUNNING
                startTime=time.monotonic()
                break
            # Checks if 'C' is pressed to reset the timer
            elif(key=='C'):
                timerState=TimerState.SETTING
                startTime=0
                countDownTime=0
                break

def displayBlastoffText():
    global timerState,startTime,countDownTime,hue

    while(True):
        # Prints "BLASTOFF"
        matrix.display.fill(0)
        matrix.display.text(str,x=textX,y=9,color=matrix.display.color565(hue,255,255))
        matrix.display.show()

        # Moves text left with text wrapping
        textX-=1
        if textX<textMin:
            textX=matrix.display.width

        # Increase hue
        hue+=7
        if hue>=1536:
            hue=0

        key=keypad.read()
        if(key=='C'):
            timerState=TimerState.SETTING
            startTime=0
            countDownTime=0
            hue=0
            break

def setup():
    matrix.display.auto_refresh=False
    matrix.display.show()
    matrix.display.auto_refresh=True

def loop():
    global timerState

    # Handles setting the timer
    if(timerState==TimerState.SETTING):
        settingTimer()
    # Handles running the timer
    elif(timerState==TimerState.RUNNING):
        runningTimer()
    # Handles paused state
    elif(timerState==TimerState.PAUSED):
        pausedTimer()