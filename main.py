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
import matplotlib.pyplot as plt


def main():
    pyautogui.hotkey('alt', 'tab')
    placement_coords = bfn.define_grid()

    while True:
        if keyboard.is_pressed('q'):
            print('Ending...')
            break
        else:

            time.sleep(2) #time between checks
            if bfn.round_state() == 1:
                hp, money, round = bfn.get_game_info()
                print(hp, money, round)
                pydirectinput.press('space')

            if bfn.round_state() == 2:
                print("Game over")

            else:
                print('Ongoing round...')  



if __name__ == '__main__':
    main()