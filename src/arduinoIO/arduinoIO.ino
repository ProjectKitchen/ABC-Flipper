

#define FIRST_BUTTON 14
#define NUM_BUTTONS 10

#define FIRST_RELAIS 2
#define NUM_RELAIS   6

#define FIRST_LIGHT 2
#define NUM_LIGHTS 4

#define THROWER1_BUTTON 16 
#define THROWER2_BUTTON 18 

#define THROWER1_RELAIS 6 
#define THROWER2_RELAIS 7 


#define DEBOUNCE_TIME 100

int blinkIdleTime=2000;
int blinkActiveTime=500;
int blinkWinTime=200;

int buttonState[NUM_BUTTONS]={HIGH};
uint32_t buttonDebounce[NUM_BUTTONS]={0};

#define GAMESTATE_IDLE    'a'
#define GAMESTATE_FLIPPER 'b'
#define GAMESTATE_ANAGRAM 'c'
#define GAMESTATE_GAMEWON 'd'

int gameState=GAMESTATE_IDLE;
int blinkCount=0;
int blinkPos=0;


void setup() {

  Serial.begin(115200);
  Serial1.begin (9600);
  
  for (int i=FIRST_BUTTON;i<FIRST_BUTTON+NUM_BUTTONS; i++) {
    pinMode(i,INPUT_PULLUP);
  }
  
  for (int i=FIRST_RELAIS;i<FIRST_RELAIS+NUM_RELAIS; i++) {
    pinMode(i,OUTPUT); digitalWrite(i,HIGH);
  }

 Serial.print('s');
}

void processBlinks() {
  switch (gameState) {

    case GAMESTATE_IDLE:
      if (++blinkCount>blinkIdleTime) {
        blinkCount=0;
        digitalWrite(FIRST_LIGHT+blinkPos,HIGH);
        if (++blinkPos>=NUM_LIGHTS) blinkPos=0;
        digitalWrite(FIRST_LIGHT+blinkPos,LOW);
      }
      break;
    case GAMESTATE_FLIPPER:  
      // TBD: light effects during game?
      break;

    case GAMESTATE_ANAGRAM:  
      if (++blinkCount>blinkActiveTime) {
        blinkCount=0;
        digitalWrite(FIRST_LIGHT+blinkPos,HIGH);
        if (++blinkPos>=NUM_LIGHTS) blinkPos=0;
        digitalWrite(FIRST_LIGHT+blinkPos,LOW);
      }
      break;

    case GAMESTATE_GAMEWON:  
      if (++blinkCount>blinkWinTime) {
        blinkCount=0;
        for (int i=0; i<NUM_LIGHTS; i++) 
          digitalWrite(FIRST_LIGHT+i,HIGH);
        if (++blinkPos>=5) { blinkPos=0; blinkCount=0; gameState='a'; }

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
    if ((c>='a') && (c<='d')) {
      gameState=c;
      blinkPos=0;blinkCount=0;
    } else Serial1.write((byte)c);    
  }

  if (gameState==GAMESTATE_FLIPPER) {
     // control throwers via flipper buttons!
     digitalWrite (THROWER1_RELAIS, digitalRead(THROWER1_BUTTON));
     digitalWrite (THROWER2_RELAIS, digitalRead(THROWER2_BUTTON));
  } else {
     // deactivate throwers!
     digitalWrite (THROWER1_RELAIS, HIGH);   
     digitalWrite (THROWER2_RELAIS, HIGH); 
  }
  
  processBlinks();
  delay(1);   //  1kHz main loop
}
