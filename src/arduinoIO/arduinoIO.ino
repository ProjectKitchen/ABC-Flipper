

#define FIRST_BUTTON 2
#define NUM_BUTTONS 6

#define FIRST_LIGHT 10
#define NUM_LIGHTS 3

#define DEBOUNCE_TIME 100

void setup() {

  Serial.begin(115200);
  for (int i=FIRST_BUTTON;i<FIRST_BUTTON+NUM_BUTTONS; i++) {
    pinMode(i,INPUT_PULLUP);
  }
  
  for (int i=FIRST_LIGHT;i<FIRST_LIGHT+NUM_LIGHTS; i++) {
    pinMode(i,OUTPUT);
  }

}

int buttonState[6]={HIGH};
uint32_t buttonDebounce[6]={0};

void loop() {
  static int blinkCount=0;
  static int blinkPos=0;
  static int delayTime=1;
  int tmp;
  
  if (++blinkCount>200) {
    blinkCount=0;
    digitalWrite(FIRST_LIGHT+blinkPos,LOW);
    if (++blinkPos>NUM_LIGHTS) blinkPos=0;
    digitalWrite(FIRST_LIGHT+blinkPos,HIGH);
  }

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
    if ((c>='0') && (c<='9')) delayTime=c-'0';
    
  }
  
  delay(delayTime);

}
