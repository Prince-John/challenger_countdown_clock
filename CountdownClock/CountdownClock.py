import time
import board
import digitalio
import rainbowio
import terminalio
from adafruit_display_text import bitmap_label
from adafruit_matrixportal.matrixportal import MatrixPortal

# Handles setting the timer
def settingTimer(): 
    global minutes,seconds,timerState

    digits=[0,0,0,0] # Array to store the digits of the timer
    counterNum=0 # Counter to keep track of the number of times the up button is pressed
    downButtonHits=0 # Counter to keep track of the number of times the down button is pressed
    while(True):
        minutes=digits[3]*10+digits[2]
        seconds=digits[1]*10+digits[0]
        timeStr="{:02d}:{:02d}".format(minutes,seconds)

        showTime(timeStr,1)

        # If the up button is pressed, increment the counterNum by 1
        if(not upButton.value):
            time.sleep(0.3)

            counterNum=(counterNum+1)%10 # Increments the counterNum by 1 and wraps around to 0 if it reaches 10
            digits[downButtonHits]=counterNum # Sets the digit at the downButtonHits index to the counterNum

            minutes=digits[3]*10+digits[2]
            seconds=digits[1]*10+digits[0]
        # If the down button is pressed, move to the next digit
        elif(not downButton.value):
            time.sleep(0.3)

            counterNum=0
            downButtonHits+=1

            # If the downButtonHits counter is 4, all four digits are set and the timer is ready to run
            if(downButtonHits==4):
                # If time is greater than 99:60, set it to 99:60
                if(minutes==99 and seconds>=60):
                    seconds=59
                timerState=TimerState.RUNNING
                break

# Handles running the timer
def runningTimer():
    global startTime,minutes,seconds,timerState

    countDownTimeS=(minutes*60)+seconds

    minutes=int(countDownTimeS//60)
    seconds=int(countDownTimeS%60)
    timeStr="{:02d}:{:02d}".format(minutes,seconds)
    showTime(timeStr,0)
    time.sleep(1)
    startTime=time.monotonic()
    while(True):
        currentTime=time.monotonic()
        timeRemaining=countDownTimeS-(currentTime-startTime)

        # If time is up, display the blastoff text
        if(timeRemaining<=0):
            displayBlastoffText()
            break
        
        minutes=int(timeRemaining//60)
        seconds=int(timeRemaining%60)
        timeStr="{:02d}:{:02d}".format(minutes,seconds)

        # Prints remaining time
        showTime(timeStr,0)

        # If the up button is pressed, pause the timer
        if(not upButton.value):
            time.sleep(0.3)
            timerState=TimerState.PAUSED
            break
        # If the down button is pressed, reset the timer
        elif(not downButton.value):
            time.sleep(0.3)
            timerState=TimerState.SETTING
            minutes=0
            seconds=0
            break

# Handles paused state
def pausedTimer():
    global minutes,seconds,timerState

    timeStr="{:02d}:{:02d}".format(minutes,seconds)

    # Prints the paused time
    showTime(timeStr,2)

    while(True):
        # If the up button is pressed, resume the timer
        if(not upButton.value):
            time.sleep(0.3)
            timerState=TimerState.RUNNING
            break
        # If the down button is pressed, reset the timer
        elif(not downButton.value):
            time.sleep(0.3)
            timerState=TimerState.SETTING
            minutes=0
            seconds=0
            break

# Displays the blastoff text
def displayBlastoffText():
    global timerState,minutes,seconds

    matrixPortal.display.show(blastOffTextArea) # Displays the blastoff text
    hue=0
    while(True):
        # Adjust the x-coordinate for smooth scrolling
        blastOffTextArea.x-=1

        # Increment the hue value for the color of the text
        hue=(hue+1)%1536
        blastOffTextArea.color=rainbowio.colorwheel(hue)

        # If the right edge of the label is off the left side of the screen, move it back to the right
        if(blastOffTextArea.x+blastOffTextArea.width<-70):
            blastOffTextArea.x=matrixPortal.display.width

        # Update the display
        matrixPortal.display.refresh()

        # Add a small delay to control the scrolling speed
        time.sleep(0.02)

        # If the up button is pressed, reset the timer
        if(not downButton.value):
            time.sleep(0.3)
            timerState=TimerState.SETTING
            minutes=0
            seconds=0
            break

# Displays the time
def showTime(time,mode):
    if(mode==0):
        setColor=0xFF0000 # Red 
    elif(mode==1):
        setColor=0x00FF00 # Green
    elif(mode==2):
        setColor=0x0000FF # Blue

    textArea=bitmap_label.Label(terminalio.FONT,text=time,scale=2,x=3,y=16,color=setColor)
    matrixPortal.display.show(textArea)

# Initialize the matrix portal
matrixPortal=MatrixPortal(status_neopixel=board.NEOPIXEL)

# Initialize the blastoff text
blastOffTextArea=bitmap_label.Label(terminalio.FONT,text="BLASTOFF!!!",scale=2,x=matrixPortal.display.width,y=16,color=0xFF0000)

# Initialize the buttons
upButtonPin=board.BUTTON_UP
downButtonPin=board.BUTTON_DOWN

upButton=digitalio.DigitalInOut(upButtonPin)
upButton.switch_to_input(pull=digitalio.Pull.UP)

downButton=digitalio.DigitalInOut(downButtonPin)
downButton.switch_to_input(pull=digitalio.Pull.UP)

# States for the timer
class TimerState:
    SETTING=0
    RUNNING=1
    PAUSED=2

startTime=0  # Start time when the timer begins
minutes=0 # Minutes for the timer
seconds=0 # Seconds for the timer

timerState=TimerState.SETTING  # Initialize the timer state to SETTING
while(True):
    # Handles setting the timer
    if(timerState==TimerState.SETTING):
        settingTimer()
    # Handles running the timer
    elif(timerState==TimerState.RUNNING):
        runningTimer()
    # Handles paused state
    elif(timerState==TimerState.PAUSED):
        pausedTimer()