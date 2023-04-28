

#define FIRST_BUTTON 2
#define NUM_BUTTONS 9

#define FIRST_LIGHT 14
#define NUM_LIGHTS 4

#define DEBOUNCE_TIME 100

int blinkIdleTime=2000;
int blinkActiveTime=500;
int blinkWinTime=200;

const int latchPin = 12; //Pin connected to latch pin (ST_CP) of 74HC595
const int clockPin = 11; //Pin connected to clock pin (SH_CP) of 74HC595
const int dataPin = 13;  //Pin connected to Data in (DS) of 74HC595


byte Tab[]={0xc0,0xf9,0xa4,0xb0,0x99,0x92,0x82,0xf8,0x80,0x90,0xff};

int buttonState[NUM_BUTTONS]={HIGH};
uint32_t buttonDebounce[NUM_BUTTONS]={0};

int blinkState='a';
int blinkCount=0;
int blinkPos=0;


void setup() {

  Serial.begin(115200);
  for (int i=FIRST_BUTTON;i<FIRST_BUTTON+NUM_BUTTONS; i++) {
    pinMode(i,INPUT_PULLUP);
  }
  
  for (int i=FIRST_LIGHT;i<FIRST_LIGHT+NUM_LIGHTS; i++) {
    pinMode(i,OUTPUT); digitalWrite(i,HIGH);
  }


  pinMode(latchPin, OUTPUT);
  pinMode(dataPin, OUTPUT);
  pinMode(clockPin, OUTPUT);

  digitalWrite(latchPin, LOW);
  for (int i=0; i<8; i++) shiftOut(dataPin, clockPin, MSBFIRST, 0xff);
  digitalWrite(latchPin, HIGH);


}

void processBlinks() {
  switch (blinkState) {

    case 'a':
      break;
    case 'b':  
      if (++blinkCount>blinkIdleTime) {
        blinkCount=0;
        digitalWrite(FIRST_LIGHT+blinkPos,HIGH);
        if (++blinkPos>=NUM_LIGHTS) blinkPos=0;
        digitalWrite(FIRST_LIGHT+blinkPos,LOW);
      }
      break;

    case 'c':  
      if (++blinkCount>blinkActiveTime) {
        blinkCount=0;
        digitalWrite(FIRST_LIGHT+blinkPos,HIGH);
        if (++blinkPos>=NUM_LIGHTS) blinkPos=0;
        digitalWrite(FIRST_LIGHT+blinkPos,LOW);
      }
      break;

    case 'd':  
      if (++blinkCount>blinkWinTime) {
        blinkCount=0;
        for (int i=0; i<NUM_LIGHTS; i++) 
          digitalWrite(FIRST_LIGHT+i,HIGH);
        if (++blinkPos>=5) { blinkPos=0; blinkCount=0; blinkState='a'; }

      }
      if (blinkCount==blinkWinTime/2) {
        for (int i=0; i<NUM_LIGHTS; i++) 
          digitalWrite(FIRST_LIGHT+i,LOW);
      }

      break;
    
  }
}


void loop() {

  int tmp;
   for (int i=0;i<NUM_BUTTONS;i++) {

    if ((tmp=digitalRead(FIRST_BUTTON+i)) != buttonState[i]) {
      buttonState[i]=tmp;
      if (tmp==LOW) {
        if (millis()-buttonDebounce[i] > DEBOUNCE_TIME) {
          buttonDebounce[i]=millis();
          Serial.print((char) ('0'+i));
        }
      }
    }

  }

  if (Serial.available()) {
    int c=Serial.read();
    if ((c>='0') && (c<='9')) {
      int bitToSet = c - 48;
      // write to the shift register with the correct bit set high:
      digitalWrite(latchPin, LOW);
      // shift the bits out:
      shiftOut(dataPin, clockPin, MSBFIRST, Tab[bitToSet]);
        // turn on the output so the LEDs can light up:
      digitalWrite(latchPin, HIGH);
    }
    else if ((c>='a') && (c<='d')) {
      blinkState=c;
      blinkPos=0;blinkCount=0;
    }
    
  }

  processBlinks();
  
  delay(1);   //  1kHz main loop

}
