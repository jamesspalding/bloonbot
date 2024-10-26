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
import pandas as pd


def main():
    #setup
    pyautogui.hotkey('alt', 'tab')
    placement_coords = bfn.define_grid()
    base_costs, upgrade_costs = bfn.get_costs('easy') #Change difficulty if needed
    towers = pd.DataFrame({'x','y','tower','cost','hotkey'})

    while True:
        time.sleep(2) #time between checks
        if bfn.round_state() == 1:
            #check round stats
            hp, money, round = bfn.get_game_info()
            print(hp, money, round)

            #place towers
            tower = bfn.place_tower(money, base_costs, placement_coords)
            towers = towers._append(tower, ignore_index = True)
            
            #start round
            pydirectinput.press('space')

        if bfn.round_state() == 2:
            print("Game over")

        else:
            print('Ongoing round...')  



if __name__ == '__main__':
    main()