import bloon_functions as bfn
import pytesseract
import re
import pyautogui
import pydirectinput
import time
from PIL import ImageGrab, Image
import keyboard
import cv2
import numpy as np



def main():
    round = int(input("Enter starting round: "))
    pyautogui.hotkey('alt', 'tab')
    while True:
        if keyboard.is_pressed('q'):
            print('Ending...')
            break
        else:

            time.sleep(2) #time between checks
            if bfn.round_state() == 1:
                print('Round ',round)
                round = round+1
                print(bfn.get_game_info())
                pydirectinput.press('space')

            if bfn.round_state() == 2:
                print("Game over")

            else:
                print('Ongoing round...')  



if __name__ == '__main__':
    main()