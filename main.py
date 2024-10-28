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
import warnings
import json


def main():

    #setup
    pyautogui.hotkey('alt', 'tab')
    placement_coords = bfn.define_grid()
    base_costs, upgrade_costs = bfn.get_costs('easy') #Change difficulty if needed
    towers_list = [] #used by place_tower
    round = bfn.get_round() #only needs to run once
    round = round - 1
    starting_round = round
    first_run = True #Used to set fast forward
    spend_round = True
    last_money = 0
    last_hp = 0



    while True:
        state = bfn.round_state()

        if state == 1:
            #check round stats
            round = round + 1
            try:
                hp, money = bfn.get_game_info()
                print(f"-------Round {round}-------")
                print(f"Money: {money} Lives: {hp}")
            except:
                print('tesseract error: starting round')
                pydirectinput.press('space')
                continue



            #place towers
            if not first_run:
                spend_round = bfn.spend(money,hp,last_money,last_hp)

            if spend_round:
                bfn.place_tower(base_costs,placement_coords,towers_list,money,round)

            #export placement as json
            with open('data.json', 'w') as f:
                json.dump(towers_list, f)



            #start round
            if first_run:
                pydirectinput.press('space') #enable ff
                first_run = False

            last_hp = hp
            last_money = money
            pydirectinput.press('space')



        if state == 2:
            print("Game over")
            round = starting_round
            first_run = True




if __name__ == '__main__':
    main()