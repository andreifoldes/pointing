
const byte buttonPin = 2;      // the number of the pushbutton pin
const byte numLEDs = 6;
const byte ledPin[numLEDs] = {3,4,5,6,7,8};

int incomingNum;          // for incoming serial data
int incoming;
int buttonState;             // the current reading from the input pin
int lastButtonState = LOW;   // the previous reading from the input pin

unsigned long lastDebounceTime = 0;  // the last time the output pin was toggled
unsigned long debounceDelay = 50;    // the debounce time; increase if the output flickers

boolean sendPressPermission = false;
boolean sendReleasePermission = false;


void setup()
{
  Serial.begin(9600);

  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  
    // flash LEDs so we know we they are alive
  for (byte n = 0; n < numLEDs; n++) {
     pinMode(ledPin[n], OUTPUT);
     delay(100);
     digitalWrite(ledPin[n], HIGH);
     delay(200);
     digitalWrite(ledPin[n], LOW);

  }
  
  delay(500); // delay() is OK in setup as it only happens once
  
  pinMode(buttonPin, INPUT);
  digitalWrite(buttonPin, HIGH);

}

void loop(){
  
  // read the state of the switch into a local variable:
  int reading = digitalRead(buttonPin);

  // check to see if you just pressed the button
  // (i.e. the input went from LOW to HIGH), and you've waited long enough
  // since the last press to ignore any noise:

  // If the switch changed, due to noise or pressing:
  if (reading != lastButtonState) {
    // reset the debouncing timer
    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > debounceDelay) {
    // whatever the reading is at, it's been there for longer than the debounce
    // delay, so take it as the actual current state:

    // if the button state has changed:
    if (reading != buttonState) {
      buttonState = reading;

      // only toggle the LED if the new button state is HIGH
      if (buttonState == LOW and sendPressPermission) {
        Serial.print(2);
        sendPressPermission = false;
      }

      if (buttonState == HIGH and sendReleasePermission) {
        Serial.print(1);
        sendReleasePermission = false;
      }
    }
  }
  // save the reading. Next time through the loop, it'll be the lastButtonState:
  lastButtonState = reading;

  }
  
void serialEvent() {
     while(Serial.available()) {


            incoming = (int)Serial.read();
            
            if(incoming >= 3 && incoming <= 9)
            {
              incomingNum = incoming;
              digitalWrite(incomingNum, HIGH);    // sets the LED on
            }
            else if(incoming == 0)
            {
              digitalWrite(incomingNum, LOW);
            }
            else if(incoming == 2)
            {
              sendPressPermission=true;
            }
            else if(incoming == 1)
            {
              sendReleasePermission=true;
            }
    }
  }


 //feedback light turn on and turn off when clicking
 //nofeedback light disappers as soon as p. starts movement





