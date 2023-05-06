
// for font customisation use:
//  https://tchapi.github.io/Adafruit-GFX-Font-Customiser/
//  https://github.com/adafruit/Adafruit-GFX-Library/tree/master/Fonts


#include <Adafruit_GFX.h>     // Core graphics library
#include <Adafruit_ST7735.h>  // Hardware-specific library for ST7735
#include <SPI.h>
//#include <Fonts/FreeSansBold24pt7b.h>
#include "FreeSansBold24pt7b.h"

// These pins will also work for the 1.8" TFT shield.
#define TFT_CS 10
#define TFT_RST -1  // Or set to -1 and connect to Arduino RESET pin
#define TFT_DC 8

// For 1.44" and 1.8" TFT with ST7735 use:
Adafruit_ST7735 tft = Adafruit_ST7735(TFT_CS, TFT_DC, TFT_RST);

char text[] = "A";
uint8_t displayNum = 0;

void setup(void) {

  Serial.begin(9600);
  Serial1.begin(9600);

  pinMode(LED_BUILTIN_TX,INPUT);
  pinMode(LED_BUILTIN_RX,INPUT);


  // Use this initializer if using a 1.8" TFT screen:
  tft.initR(INITR_BLACKTAB);  // Init ST7735S chip, black tab
  // tft.initR(INITR_GREENTAB);      // Init ST7735S chip, green tab
  // tft.setSPISpeed(40000000);

  uint16_t time = millis();
  tft.fillScreen(ST77XX_BLACK);

  delay(500);
  tft.setRotation(1);  // rotate 90 degrees
  tft.setFont(&FreeSansBold24pt7b);

  tft.setTextSize(2);
  //tft.setTextSize(13);
  tft.fillScreen(ST77XX_BLACK);
/*
  for (int i=65;i<255;i++) {
    text[0]=i;
    tft.fillScreen(ST77XX_BLACK);
    tft.setCursor(60, 100);  // 63, 100
    tft.setTextColor(ST77XX_YELLOW);
    tft.println(text);
    delay(300);
  }
  */
}


void loop() {
  int input = 0;
  if (Serial.available()) input = Serial.read(); 
  else if (Serial1.available()) input = Serial1.read();
  else {   pinMode(LED_BUILTIN_TX,INPUT);
          pinMode(LED_BUILTIN_RX,INPUT);
          return;
  }

  if ((input>'0') && (input < '6')) {
    displayNum = input;
  } else {
    if (displayNum == '1') {
      text[0] = input;
      tft.fillScreen(ST77XX_BLACK);
      tft.setCursor(60, 100);  // 63, 20
      tft.setTextColor(ST77XX_YELLOW);
      tft.println(text);
      displayNum=0;
    } else {
      Serial1.write(displayNum-1);
      Serial1.write((uint8_t)input);
      displayNum=0;
    }
  }
}


// tft.invertDisplay(true);
// delay(500);
// tft.invertDisplay(false);
//  tft.setCursor(0, 20);    // 63, 20
//  tft.setTextColor(ST77XX_BLACK);
//  tft.println(text);