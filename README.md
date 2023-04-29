# ABC-Flipper

**A Pinball Machine for solving Anagram Puzzles! (In cooperation with David Moises)**



# Preparation

## Material

| Nr.  | Description                        | 
| ---- | ---------------------------------- | 
| 1    | 1 x RaspberryPi 4                  | 
| 2    | 1 x Arduino Nano                   | 
| 3    | 8 x 7-Segment SPI LED Display (DFrobot)  | 
| 4    | 1 x 8-Relay Module for Arduino     | 
| 5    | 5 x SPI LCD Display (ST7735, 160x128, SPI) | 
| 6    | Breadboard, jumper wires, buttons/reed switches | 


## Connect components as shown;

![flipperBreadboardFoto1](./img/flipper_breadboard1.jpg)
![flipperBreadboardFoto2](./img/flipper_breadboard2.jpg)
![flipperBreadboardFoto3](./img/flipper_breadboard3.jpg)


## Install SW-Requirements

| Nr.  | Description                       | Source                                                       |
| ---- | --------------------------------- | ------------------------------------------------------------ |
| 1    | Python3                           | Open an command shell window and check your python/python3 version: `python3 --version'. The recommended version is python3.8 or newer |
| 2    | pyserial library                  | Install via pip: `pip3 install pyserial` |
| 3    | numa.oled LCD/OLED library        | Install via pip: `pip3 install numa.oled`|
| 4    | pygame library                    | Install via pip: `pip3 install pygame`   |
| 5    | Arduino IDE                       | Download from Arduino website https://www.arduino.cc        |


## Deploy Software

* Build an flash the Arduino code (folder src/arduinoIO) 
* run python3 flipper.py
* install startup script and configure read-only filesystem for RP4


