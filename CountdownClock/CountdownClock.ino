#include <RGBmatrixPanel.h>
#include <Keypad.h>
#include <SPI.h>

//Pins for the LED panel
#define CLK 11 
#define OE   9
#define LAT 10
#define A   A0
#define B   A1
#define C   A2
#define D   A3

//Initialize matrix setup. "true" enables double-buffering, which keeps the animation from flickering
//The "64" is there because this is a 32x64 matrix
RGBmatrixPanel matrix(A,B,C,D,CLK,LAT,OE,true,64);

//Setting up text
const char str[] PROGMEM="BLASTOFF"; //Scrolling text string
int16_t    textX        =matrix.width(), //Width of the matrix for text string
           textMin      =sizeof(str) * -12, //Setting number of columns at right side after last letter before we reset the scrolling pattern
           hue          =0; //Hue to start at zero

//Allows for string pointers
#define F2(progmem_ptr) (const __FlashStringHelper *)progmem_ptr

//Defining our pins for the keypad
const byte numROWS=4;
const byte numCOLS=4;
char keys[numROWS][numCOLS]=
{
  {'1','2','3','A'},
  {'4','5','6','B'},
  {'7','8','9','C'},
  {'*','0','#','D'}
};
byte rowPins[numROWS]={40,41,42,43};
byte colPins[numCOLS]={44,45,46,47};

//Initialize keypad
Keypad keypad=Keypad(makeKeymap(keys),rowPins,colPins,numROWS,numCOLS);

//States for timer
enum TimerState
{
  SETTING,
  RUNNING,
  PAUSED
};

unsigned long startTime=0; //Start time when the timer begins
int countDownTime=0; //Countdown time in MM:SS

TimerState timerState=SETTING; //Initialize the timer state to SETTING

void settingTimer()
{
  int minutes,seconds;
  char timeStr[6],key;

  while(true)
  {
    minutes=countDownTime/100;
    seconds=countDownTime%100;
    snprintf(timeStr,sizeof(timeStr),"%02d:%02d",minutes,seconds);

    // Prints the desired time
    matrix.fillScreen(0);
    matrix.setTextColor(matrix.ColorHSV(0,255,255,true)); 
    matrix.setCursor(3,9); 
    matrix.print(timeStr);
    matrix.swapBuffers(false);

    key=keypad.getKey();
    if(key!=NO_KEY)
    {
      // Checks if 'A' is pressed to start the timer
      if(key=='A' && countDownTime>0)
      {
        timerState=RUNNING;
        startTime=millis();
        break;
      }
      // Checks if 'C' is pressed to reset the timer
      else if(key=='C')
      {
        countDownTime=0;
      }
      // Checks if 'D' is pressed to backspace
      else if(key=='D' && countDownTime>0)
      {
        countDownTime/=10;
      }
      // Checks if a number is pressed
      else if(key>='0' && key<='9' && countDownTime<=999)
      {
        countDownTime=countDownTime*10+(key-'0');
      }
    }
  }
}

void runningTimer()
{
  char timeStr[6],key;
  unsigned long currentTime,timeRemaining;

  int minutes=countDownTime/100;
  int seconds=countDownTime%100;
  unsigned long countDownTimeS=(minutes*60)+seconds; //Count down time in seconds

  while(true)
  {
    // Calculates the remaining time on timer
    currentTime=millis();
    timeRemaining=countDownTimeS*1000-(currentTime-startTime);

    // Checks if timeRemaining is 0
    if(timeRemaining>6039000)
    {
      displayBlastoffText();
      break;
    }

    minutes=timeRemaining/60000;
    seconds=(timeRemaining/1000)%60;
    snprintf(timeStr,sizeof(timeStr),"%02d:%02d",minutes,seconds);
    
    // Prints remaining time
    matrix.fillScreen(0);
    matrix.setTextColor(matrix.ColorHSV(0,255,255,true)); 
    matrix.setCursor(3,9); 
    matrix.print(timeStr);
    matrix.swapBuffers(false);

    key=keypad.getKey();
    if(key!=NO_KEY)
    {
      // Checks if 'B' is pressed to pause the timer
      if(key=='B')
      {
        timerState=PAUSED;
        countDownTime=minutes*100+seconds;
        break;
      }
      // Checks if 'C' is pressed to reset the timer
      else if(key=='C')
      {
        timerState=SETTING;
        startTime=0;
        countDownTime=0;
        break;
      }
    }
  }
}

void pausedTimer()
{
  char timeStr[6];

  int minutes=countDownTime/100;
  int seconds=countDownTime%100;
  snprintf(timeStr,sizeof(timeStr),"%02d:%02d",minutes,seconds);

  // Prints the paused time
  matrix.fillScreen(0);
  matrix.setTextColor(matrix.ColorHSV(0,255,255,true)); 
  matrix.setCursor(3,9); 
  matrix.print(timeStr);
  matrix.swapBuffers(false);

  while(true)
  {
    char key=keypad.getKey();
    if(key!=NO_KEY)
    {
      // Checks if 'A' is pressed to resume the timer
      if(key=='A')
      {
        timerState=RUNNING;
        startTime=millis();
        break;
      }
      // Checks if 'C' is pressed to reset the timer
      else if(key=='C')
      {
        timerState=SETTING;
        startTime=0;
        countDownTime=0;
        break;
      }
    }
  }
}

void displayBlastoffText()
{
  while(true)
  {
    // Prints "BLASTOFF"
    matrix.fillScreen(0);
    matrix.setTextColor(matrix.ColorHSV(hue,255,255,true));
    matrix.setCursor(textX,9);
    matrix.print(F2(str));
    matrix.swapBuffers(false);

    // Moves text left with text wrapping
    if((--textX)<textMin)
    {
      textX=matrix.width();
    }

    // Increase hue
    hue+=7;
    if(hue>=1536)
    {
      hue=0;
    }

    // Checks if 'C' is pressed to reset the timer
    char key=keypad.getKey();
    if (key=='C')
    {
      timerState=SETTING;
      startTime=0;
      countDownTime=0;
      hue=0;
      break;
    }
  }
}

void setup()
{
  Serial.begin(9600);

  matrix.begin();
  matrix.setTextWrap(false); //Allows text to run off right edge
  matrix.setTextSize(2); //Sets text size
}

void loop()
{
  //Handles setting the timer
  if (timerState==SETTING)
  {
    settingTimer();
  }
  //Handles running the timer
  else if(timerState==RUNNING)
  {
    runningTimer();
  }
  //Handles paused state
  else if(timerState==PAUSED)
  {
    pausedTimer();
  }
}