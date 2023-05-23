

//  arduinoIO.ino
//  interface to flipper.py
//  hardware: Teensy2.0++
//  
//  buttons/sensors connected to in4-in17
//  relais connected to out18-out25 (lights) and out38-out45(magnets)

#define NUM_BUTTONS 14
#define FIRST_BUTTON 4

#define NUM_RELAIS   8
#define FIRST_RELAIS 38

#define BALL_RELAIS 38
#define THROWER2_RELAIS 39
#define THROWER1_RELAIS 40
#define BELL_RELAIS 41

#define NUM_LIGHTS 8
#define FIRST_LIGHT 18

#define NUM_TOPLIGHTS 4
#define FIRST_TOPLIGHT 18

#define NUM_RANDOMLIGHTS 4
#define FIRST_RANDOMLIGHT 22

#define BUMPERLIGHT_RELAIS 21

#define THROWER1_BUTTON 6
#define THROWER2_BUTTON 8
#define JOKER_BUTTON  14
#define BUMPER_BUTTON 13


#define BELL_DURATION 100
#define BALL_DURATION 100
#define BUMPERLIGHT_DURATION 200
#define BUTTON_DEBOUNCE_CYCLES  4
#define BUTTON_BYPASS_TIME 100

int blinkIdleTime = 2000;
int blinkActiveTime = 500;
int blinkWinTime = 200;
int bellOnTime = 0, ballOnTime = 0, bumperLightOnTime=0;

uint8_t buttonState[NUM_BUTTONS] = {0};
uint8_t buttonDebounce[NUM_BUTTONS] = {0};
uint32_t buttonTimestamp[NUM_BUTTONS] = {0};

#define GAMESTATE_IDLE    'a'
#define GAMESTATE_FLIPPER 'b'
#define GAMESTATE_ANAGRAM 'c'
#define GAMESTATE_WON     'd'
#define GAMESTATE_LOST    'e'

#define CMD_TRIGGER_BALL  'f'
#define CMD_TRIGGER_BELL  'g'
#define CMD_BUMPER_LIGHT  'i'
#define CMD_RANDOM_LIGHT  'h'


int gameState = GAMESTATE_IDLE;
int blinkCount = 0;
int blinkPos = 0;


void setup() {

  Serial.begin(115200);
  Serial1.begin (9600);

  for (int i = FIRST_BUTTON; i < FIRST_BUTTON + NUM_BUTTONS; i++) {
    pinMode(i, INPUT_PULLUP);
  }

  for (int i = FIRST_RELAIS; i < FIRST_RELAIS + NUM_RELAIS; i++) {
    pinMode(i, OUTPUT); digitalWrite(i, HIGH);
  }

  for (int i = FIRST_LIGHT; i < FIRST_LIGHT + NUM_LIGHTS; i++) {
    pinMode(i, OUTPUT); digitalWrite(i, HIGH);
  }

  Serial.print('s');
}


void setRandomLights(uint8_t mode) {
  uint8_t pattern=random(1<<NUM_RANDOMLIGHTS);
  if (!mode) pattern=0;   // clear all lights
  
  for (uint8_t i =0;i<NUM_RANDOMLIGHTS;i++)
    if (pattern&(1<<i)) digitalWrite(FIRST_RANDOMLIGHT+i,LOW); 
    else digitalWrite(FIRST_RANDOMLIGHT+i,HIGH);
}

void setTopLights(uint8_t mode) {
  
  for (uint8_t i =0;i<NUM_TOPLIGHTS;i++)
    if (mode) digitalWrite(FIRST_TOPLIGHT+i,LOW); 
    else digitalWrite(FIRST_TOPLIGHT+i,HIGH);

}

void processBlinks() {
  switch (gameState) {

    case GAMESTATE_IDLE:
      if (++blinkCount > blinkIdleTime) {
        blinkCount = 0;
        digitalWrite(FIRST_TOPLIGHT + blinkPos, HIGH);
        if (++blinkPos >= NUM_TOPLIGHTS) blinkPos = 0;
        digitalWrite(FIRST_TOPLIGHT + blinkPos, LOW);
        if (random(20)>15) setRandomLights(1);
      }
      break;
    case GAMESTATE_FLIPPER:
      // currently no periodic light effects during gameplay
      break;

    case GAMESTATE_ANAGRAM:
      if (++blinkCount > blinkActiveTime) {
        blinkCount = 0;
        digitalWrite(FIRST_TOPLIGHT + blinkPos, HIGH);
        if (++blinkPos >= NUM_TOPLIGHTS) blinkPos = 0;
        digitalWrite(FIRST_TOPLIGHT + blinkPos, LOW);
      }
      break;

    case GAMESTATE_WON:
      if (++blinkCount > blinkWinTime) {
        blinkCount = 0;
        for (int i = 0; i < NUM_TOPLIGHTS; i++)
          digitalWrite(FIRST_TOPLIGHT + i, HIGH);
        if (++blinkPos >= 5) {
          blinkPos = 0;
          blinkCount = 0;
          gameState = 'a';
        }

      }
      if (blinkCount == blinkWinTime / 2) {
        for (int i = 0; i < NUM_TOPLIGHTS; i++)
          digitalWrite(FIRST_TOPLIGHT + i, LOW);
      }
      break;
    case GAMESTATE_LOST:
      break;
  }
}


void loop() {

  int tmp;
  for (int i = 0; i < NUM_BUTTONS; i++) {

    tmp = digitalRead(FIRST_BUTTON + i);
    if ((tmp == LOW) && (buttonDebounce[i] < BUTTON_DEBOUNCE_CYCLES)) {
      buttonDebounce[i]++;
      if ((buttonDebounce[i] == BUTTON_DEBOUNCE_CYCLES) && !buttonState[i])  {
        buttonState[i] = 1;
        // handle button press
        if ((millis() - buttonTimestamp[i]) > BUTTON_BYPASS_TIME) {
          buttonTimestamp[i] = millis();
          Serial.print((char) ('0' + i)); 
          if (FIRST_BUTTON+i == BUMPER_BUTTON) {
            bumperLightOnTime=BUMPERLIGHT_DURATION;
            digitalWrite(BUMPERLIGHT_RELAIS, LOW);
          }
        }
      }
    }
    
    if ((tmp == HIGH) && (buttonDebounce[i] > 0)) {
      buttonDebounce[i]--;
      if ((buttonDebounce[i] == 0) && buttonState[i])  {
        buttonState[i] = 0;
        // if desired, handle button release
      }
    }
  }


  if (Serial.available()) {
    int c = Serial.read();
    if ((c >= 'a') && (c <= 'e')) {
      gameState = c;
      blinkPos = 0; blinkCount = 0;
      setRandomLights(0);
      setTopLights(0);
    }
    else if (c == CMD_TRIGGER_BELL) {
      digitalWrite(BELL_RELAIS, LOW);
      bellOnTime = BELL_DURATION;
    }
    else if (c == CMD_TRIGGER_BALL) {
      digitalWrite(BALL_RELAIS, LOW);
      ballOnTime = BALL_DURATION;
    }
    else if (c == CMD_BUMPER_LIGHT) {
      bumperLightOnTime = BUMPERLIGHT_DURATION;      
      digitalWrite(BUMPERLIGHT_RELAIS, LOW);
    }
    else if (c == CMD_RANDOM_LIGHT) {
      setRandomLights(1);      
    }
    else Serial1.write((byte)c);
  }

  if (bellOnTime) {
    bellOnTime--;
    if (!bellOnTime) digitalWrite(BELL_RELAIS, HIGH);
  }

  if (ballOnTime) {
    ballOnTime--;
    if (!ballOnTime) digitalWrite(BALL_RELAIS, HIGH);
  }

  if (bumperLightOnTime) {
    bumperLightOnTime--;
    if (!bumperLightOnTime) digitalWrite(BUMPERLIGHT_RELAIS, HIGH);
  }

  if (gameState == GAMESTATE_FLIPPER) {
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
