import keyboard
import time
import pygame



def morse_code_translator(code):
    morse_code_dict = {
        '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
        '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
        '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
        '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
        '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
        '--..': 'Z', '.----': '1', '..---': '2', '...--': '3',
        '....-': '4', '.....': '5', '-....': '6', '--...': '7',
        '---..': '8', '----.': '9', '-----': '0', '': ' '
    }

    words = code.split(' / ')
    translated = []

    for word in words:
        letters = word.split(' ')
        translated_word = []

        for letter in letters:
            if letter in morse_code_dict:
                translated_word.append(morse_code_dict[letter])

        translated.append(''.join(translated_word))

    return ' '.join(translated)


def get_morse_code():
    space_duration = 0
    morse_code = ''
    
    while True:
        if keyboard.is_pressed('space'):
            break
        if keyboard.is_pressed('enter'):
            return ''
        space_duration += 1
        time.sleep(0.01)  # Adjust sleep time as needed

        if space_duration > 50:
            return ' ' 
    #keyboard.wait('space')  # Wait for initial space key press
    
    morseSound.play()    

    space_duration=0
    while keyboard.is_pressed('space'):
        space_duration += 1
        time.sleep(0.01)  # Adjust sleep time as needed
    
    morseSound.stop()
    if space_duration >= 20:  # Long press indicates dash
        morse_code += '-'
    else:  # Short press indicates dot
        morse_code += '.'

    return morse_code


# User input loop
morse_text = ''
pygame.mixer.init()
morseSound = pygame.mixer.Sound("../sounds/morse.wav")


while True:
    morse_symbol = get_morse_code()
    
    if morse_symbol == '':
        break
    
    if morse_symbol == ' ':  # Separator between words
        #morse_code += ' / '
        translated_text = morse_code_translator(morse_text)
        print(f"  {translated_text}")
        morse_text = ''
        
    else:
        morse_text += morse_symbol
    print (morse_symbol, end="", flush=True)

