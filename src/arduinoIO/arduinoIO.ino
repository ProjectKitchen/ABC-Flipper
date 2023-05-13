

#define TEENSY2    // for Teensy2.0++ controller!  comment/remove for Teensy 3.2!


#ifdef TEENSY2
  #define FIRST_BUTTON 4
  #define NUM_BUTTONS 14
  
  #define FIRST_RELAIS 38
  #define NUM_RELAIS   8
  
  #define FIRST_LIGHT 18
  #define NUM_LIGHTS 4
  
  #define THROWER1_BUTTON 6 
  #define THROWER2_BUTTON 8 
  
  
  #define BELL_RELAIS 38 
  #define BALL_RELAIS 39 
  #define THROWER1_RELAIS 40
  #define THROWER2_RELAIS 41 
#else
  #define FIRST_BUTTON 14
  #define NUM_BUTTONS 10
  
  #define FIRST_RELAIS 2
  #define NUM_RELAIS   8
  
  #define FIRST_LIGHT 2
  #define NUM_LIGHTS 4
  
  #define THROWER1_BUTTON 16 
  #define THROWER2_BUTTON 18 
  
  
  #define BELL_RELAIS 8 
  #define BALL_RELAIS 9 
  #define THROWER1_RELAIS 7
  #define THROWER2_RELAIS 6 
#endif

#define BELL_ACTIVE_TIME 20 


#define DEBOUNCE_TIME 100

int blinkIdleTime=2000;
int blinkActiveTime=500;
int blinkWinTime=200;
int bellOnTime=0, ballOnTime=0;

int buttonState[NUM_BUTTONS]={HIGH};
uint32_t buttonDebounce[NUM_BUTTONS]={0};

#define GAMESTATE_IDLE    'a'
#define GAMESTATE_FLIPPER 'b'
#define GAMESTATE_ANAGRAM 'c'
#define GAMESTATE_WON     'd'
#define GAMESTATE_LOST    'e'

#define CMD_TRIGGER_BALL  'f'
#define CMD_TRIGGER_BELL  'g'

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

  for (int i=FIRST_LIGHT;i<FIRST_LIGHT+NUM_LIGHTS; i++) {
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

    case GAMESTATE_WON:  
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
    case GAMESTATE_LOST:
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
    if ((c>='a') && (c<='e')) {
      gameState=c;
      blinkPos=0;blinkCount=0;
    } 
    else if (c==CMD_TRIGGER_BELL) {
      digitalWrite(BELL_RELAIS, LOW);
      bellOnTime=100;      
    }
    else if (c==CMD_TRIGGER_BALL) {
      digitalWrite(BALL_RELAIS, LOW);
      ballOnTime=100;      
    }
    else Serial1.write((byte)c);    
  }

  if (bellOnTime) {
    bellOnTime--;
    if(!bellOnTime) digitalWrite(BELL_RELAIS,HIGH);
  }

  if (ballOnTime) {
    ballOnTime--;
    if(!ballOnTime) digitalWrite(BALL_RELAIS,HIGH);
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
