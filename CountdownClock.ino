#include <RGBmatrixPanel.h>
#include <Keypad.h>
#include <SPI.h>

// Defining our pins for the LED panel
#define CLK 11 
#define OE   9
#define LAT 10
#define A   A0
#define B   A1
#define C   A2
#define D   A3

// Setup for keypad variables
char currentTimeValue[4]; // 4 nums: MM:SS
int currentState = 1;
int timerSeconds = 0;
int loopCount = 0; 

// Defining our pins for the keypad
const byte numCOLS = 4; 
char keys[ROWS][numCOLS] = {
  {'1','2','3','A'},
  {'4','5','6','B'},
  {'7','8','9','C'},
  {'*','0','#','D'}
};
byte rowPins[ROWS] = {40,41,42,43}; 

byte colPins[numCOLS]= {44,45,46,47}; 

Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, numCOLS);

// Defining our matrix setup. "true" enables double-buffering, which keeps the animation from flickering
// the "64" is there because this is a 32x64 matrix and this library can also be used for other sizes
RGBmatrixPanel matrix(A, B, C, D, CLK, LAT, OE, true, 64);

#define F2(progmem_ptr) (const __FlashStringHelper *)progmem_ptr // Lets us use string pointers

// Setting up our text
const char str[] PROGMEM = "BLASTOFF"; // Insert scrolling text string here
int16_t    textX         = matrix.width(), // Defining the width of the matrix
           textMin       = sizeof(str) * -12, // Setting number of columns at right side after last letter before we reset the scrolling pattern
           hue           = 0; // Setting hue to zero to start


void setup() {
  Serial.begin(9600);
  matrix.begin();
  matrix.setTextWrap(false); // Allow text to run off right edge
  matrix.setTextSize(2); // Set text size

  // Initialize time values as zeros
  currentTimeValue[0]='0';
  currentTimeValue[1]='0';
  currentTimeValue[2]='0';
  currentTimeValue[3]='0';
}

void loop() {

  // Clear background
  matrix.fillScreen(0);


  // Draw big scrolly text
  matrix.setTextColor(matrix.ColorHSV(hue, 255, 255, true)); //color changes hue as it scrolls
  matrix.setCursor(textX, 9); //sets text 9 rows from the top 
  matrix.print(F2(str)); // prints the string we defined earlier


  char key = keypad.getKey();
  if (key != NO_KEY){
  Serial.println(key);
  }

  // Move text left with text wrapping, increase hue
  if((--textX) < textMin) textX = matrix.width();
  hue += 7;
  if(hue >= 1536) hue -= 1536;

  // Update display
  matrix.swapBuffers(false);
}