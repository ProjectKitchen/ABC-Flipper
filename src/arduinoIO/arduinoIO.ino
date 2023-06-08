

//  arduinoIO.ino
//  interface to flipper.py
//  hardware: Teensy2.0++
//
//  buttons/sensors connected to in4-in17
//  relais connected to out18-out25 (lights) and out38-out45(magnets)

#define NUM_BUTTONS 13
#define FIRST_BUTTON 4

#define NUM_RELAIS   8
#define FIRST_RELAIS 38

#define BALL_RELAIS 38
#define THROWER2_RELAIS 39
#define THROWER1_RELAIS 40
#define BELL_RELAIS 41

#define NUM_LIGHTS 8
#define FIRST_LIGHT 18

#define NUM_TOPLIGHTS 3
#define FIRST_TOPLIGHT 18

#define NUM_RANDOMLIGHTS 4
#define FIRST_RANDOMLIGHT 22

#define BUMPERLIGHT_RELAIS 21

#define THROWER1_BUTTON 6
#define THROWER2_BUTTON 8
#define JOKER_BUTTON   14
#define BUMPER_BUTTON  13
#define MODE_SWITCH    17


#define BELL_DURATION 100
#define BALL_DURATION 100
#define BUMPERLIGHT_DURATION 200
#define BUTTON_DEBOUNCE_CYCLES  4
#define BUTTON_BYPASS_TIME 100
#define FLIPPERCOIL_MAXTIME 15000
#define FLIPPER_BYPASS_TIME 5000

int blinkIdleTime = 2000;
int blinkGameTime = 750;
int blinkActiveTime = 500;
int blinkWinTime = 200;
int bellOnTime = 0, ballOnTime = 0, bumperLightOnTime = 0, topLightBlink = 0;
int thr1Count = 0, thr2Count = 0, flipper1Bypass = 0, flipper2Bypass = 0;
int autoSolve=-1;

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
#define CMD_TOP_LIGHT     'j'


int gameState = GAMESTATE_IDLE;
int blinkCount = 0;
int blinkPos = 0;


void setup() {

  Serial.begin(115200);
  Serial1.begin (9600);

  pinMode(MODE_SWITCH,INPUT_PULLUP);
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
  //uint8_t pattern=random(1<<NUM_RANDOMLIGHTS);
  static uint8_t pattern = 4;
  if (mode == 1) {
    if (pattern == 4) pattern = 8; else pattern = 4;
  }
  else if (mode == 2) {
    if (pattern == 12) pattern = 0; else pattern = 12;
  }
  if (!mode) pattern = 0; // clear all lights

  for (uint8_t i = 0; i < NUM_RANDOMLIGHTS; i++)
    if (pattern & (1 << i)) digitalWrite(FIRST_RANDOMLIGHT + i, LOW);
    else digitalWrite(FIRST_RANDOMLIGHT + i, HIGH);
}

void setTopLights(uint8_t mode) {

  for (uint8_t i = 0; i < NUM_TOPLIGHTS; i++)
    if (mode) digitalWrite(FIRST_TOPLIGHT + i, LOW);
    else digitalWrite(FIRST_TOPLIGHT + i, HIGH);

}

void processBlinks() {
  switch (gameState) {

    case GAMESTATE_IDLE:
      if (++blinkCount > blinkIdleTime) {
        blinkCount = 0;
        digitalWrite(FIRST_TOPLIGHT + blinkPos, HIGH);
        if (++blinkPos >= NUM_TOPLIGHTS) blinkPos = 0;
        digitalWrite(FIRST_TOPLIGHT + blinkPos, LOW);
        if (random(20) > 5) setRandomLights(1);

        if (digitalRead(MODE_SWITCH) != autoSolve) {
          autoSolve=digitalRead(MODE_SWITCH);
          if (autoSolve == LOW) Serial.print ('='); else  Serial.print ('>');          
        }

      }
      break;
    case GAMESTATE_FLIPPER:
      if (++blinkCount > blinkGameTime) {
        blinkCount = 0;
        switch (random(3)) {
          case 0:
            digitalWrite(FIRST_TOPLIGHT, HIGH);
            digitalWrite(FIRST_TOPLIGHT + 1, LOW);
            digitalWrite(FIRST_TOPLIGHT + 2, LOW);
            break;
          case 1:
            digitalWrite(FIRST_TOPLIGHT, LOW);
            digitalWrite(FIRST_TOPLIGHT + 1, HIGH);
            digitalWrite(FIRST_TOPLIGHT + 2, LOW);
            break;
          case 2:
            digitalWrite(FIRST_TOPLIGHT, LOW);
            digitalWrite(FIRST_TOPLIGHT + 1, LOW);
            digitalWrite(FIRST_TOPLIGHT + 2, HIGH);
            break;

        }
      }
      break;

    case GAMESTATE_ANAGRAM:
      if (++blinkCount > blinkActiveTime) {
        setRandomLights(2);
        blinkCount = 0;
        digitalWrite(FIRST_TOPLIGHT + blinkPos, HIGH);
        if (++blinkPos >= NUM_TOPLIGHTS) blinkPos = 0;
        digitalWrite(FIRST_TOPLIGHT + blinkPos, LOW);
      }
      break;

    case GAMESTATE_WON:
      if (++blinkCount > blinkWinTime) {
        blinkCount = 0;
        setRandomLights(2);
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
          if (FIRST_BUTTON + i == BUMPER_BUTTON) {
            bumperLightOnTime = BUMPERLIGHT_DURATION;
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
    if ((c >= GAMESTATE_IDLE) && (c <= GAMESTATE_LOST)) {
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
    else if (c == CMD_TOP_LIGHT) {
      topLightBlink = 800;
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

  if (topLightBlink) {
    topLightBlink--;
    if ((topLightBlink % 300) < 200) setTopLights(1);
    else setTopLights(0);
    if (!topLightBlink) setTopLights(0);
  }


  // control flipper coils via buttons
  if (gameState == GAMESTATE_FLIPPER) {

    if (!digitalRead(THROWER1_BUTTON)) {
      if ((thr1Count < FLIPPERCOIL_MAXTIME) && (!flipper1Bypass)) {
        thr1Count++;
        if (thr1Count == FLIPPERCOIL_MAXTIME) flipper1Bypass = FLIPPER_BYPASS_TIME;
        else digitalWrite(THROWER1_RELAIS, LOW);
      }

    }
    else {
      thr1Count = 0;
      digitalWrite(THROWER1_RELAIS, HIGH);
    }
    if (flipper1Bypass) {
      flipper1Bypass--;
      digitalWrite(THROWER1_RELAIS, HIGH);
    }

    if (!digitalRead(THROWER2_BUTTON)) {
      if ((thr2Count < FLIPPERCOIL_MAXTIME) && (!flipper2Bypass)) {
        thr2Count++;
        if (thr2Count == FLIPPERCOIL_MAXTIME) flipper2Bypass = FLIPPER_BYPASS_TIME;
        else digitalWrite(THROWER2_RELAIS, LOW);
      }

    }
    else {
      thr2Count = 0;
      digitalWrite(THROWER2_RELAIS, HIGH);
    }
    if (flipper2Bypass) {
      flipper2Bypass--;
      digitalWrite(THROWER2_RELAIS, HIGH);
    }

  } else {
    // deactivate throwers!
    digitalWrite (THROWER1_RELAIS, HIGH);
    digitalWrite (THROWER2_RELAIS, HIGH);
  }

  processBlinks();
  delay(1);   //  1kHz main loop
}
