import pytesseract
import re
import pyautogui
import pydirectinput
import time
from PIL import ImageGrab, Image, ImageDraw
import keyboard
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math

#load tesseract
with open("assets/tess_path.txt") as my_file:
    tess_path = my_file.read()
pytesseract.pytesseract.tesseract_cmd = tess_path


#extract text from image
def img_to_num(img):
    imgstr = pytesseract.image_to_string(img,config='--psm 6').replace(',', '')
    imgstr = imgstr.replace(';', '')
    return([int(s) for s in re.findall(r'\d+', imgstr)])


#self explanitory
def screen_cap():
    pyautogui.hotkey('alt', 'prtscr')
    img = ImageGrab.grabclipboard()
    img.save('temp.png')
    return(cv2.imread('temp.png'))


#get hp, money, round
def get_game_info():
    screen_cap()
    im = Image.open('temp.png')
    width, height = im.size

    ##### HP + Money #####
    left = .07 * width
    right = .30 * width
    top = .048 * height
    bottom = .1 * height
    im1 = im.crop((left, top, right, bottom))
    im1.save('temp1.png')

    #obscure image
    image = Image.open("temp1.png").convert("L")
    draw = ImageDraw.Draw(image)
    box_coordinates = (90, 0, 231, 70)
    draw.rectangle(box_coordinates, fill="black")
    image = image.point(lambda p: 255 if p > 250 else 0)
    image.save("temp1.png")

    hp, money = img_to_num('temp1.png')

    #### Round #####
    left = .745 * width
    right = .7728 * width
    top = .048 * height
    bottom = .1 * height
    im2 = im.crop((left, top, right, bottom))
    im2.save('temp2.png')

    #obscure image
    image = Image.open("temp2.png").convert("L")
    image = image.point(lambda p: 255 if p > 250 else 0)
    image.save("temp2.png")

    round = img_to_num('temp2.png')[0] + 1 #tells what next round is

    return(hp,money,round)


#recognize round end
def round_state():
    screen = screen_cap()

    #new round
    play_button = cv2.imread('assets/play_button.png')
    result = cv2.matchTemplate(screen, play_button, cv2.TM_CCOEFF_NORMED)
    location = np.where(result == 1)
    newround = len(location[0]) > 0

    #game over
    restart_button = cv2.imread('assets/restart_button.png')
    result = cv2.matchTemplate(screen, restart_button, cv2.TM_CCOEFF_NORMED)
    location = np.where(result == 1)
    gameover = len(location[0]) > 0
    

    if gameover:
        #click restart
        pyautogui.moveTo(location[0][0], location[1][0])
        pydirectinput.click()

        time.sleep(.25)
        restart_text = cv2.imread('assets/restart_text.png')
        result = cv2.matchTemplate(screen_cap(), restart_text, cv2.TM_CCOEFF_NORMED)
        location = np.where(result >= .8)

        #confirm restart
        pyautogui.moveTo(location[1][0], location[0][0])
        pydirectinput.click()        
        return(2)
            
    if newround:
        return(1)
    else:
        return(0)
    

#create map grid for placement reference
def define_grid(precision = 100, save = False):
    #get/crop image
    pyautogui.hotkey('alt', 'prtscr')
    img = ImageGrab.grabclipboard()
    img.save('temp.png')
    im = Image.open('temp.png')
    width, height = im.size

    left = 0 * width
    right = .85 * width
    top = .11 * height
    bottom = height

    image = im.crop((left, top, right, bottom))
    image_arr = np.array(image)

    #add grid
    fig, ax = plt.subplots()
    ax.imshow(image)
    ax.grid(True, color='white', linestyle='-')
    ax.set_xticks(np.arange(0, image_arr.shape[1], precision))
    ax.set_yticks(np.arange(0, image_arr.shape[0], precision))

    #get coordinates map
    x_centers = np.arange(precision / 2, image_arr.shape[1], precision)
    y_centers = np.arange(precision / 2, image_arr.shape[0], precision)
    X, Y = np.meshgrid(x_centers, y_centers)
    coordinates = np.column_stack((X.ravel(), Y.ravel()))

    if save:
        plt.savefig('map_grid.png')

    plt.close(fig)
    return(coordinates)


#get money values as df
def get_costs(difficulty):
    base_costs = pd.read_csv('assets/base_costs.csv')
    upgrade_costs = pd.read_csv('assets/upgrade_costs.csv')

    if difficulty == 'easy':
        base_costs['cost'] * 0.85
        upgrade_costs['cost'] = upgrade_costs['cost'] * 0.85
        return(base_costs,upgrade_costs)
    
    if difficulty == 'hard':
        base_costs['cost'] = base_costs['cost'] * 1.08
        upgrade_costs['cost'] = upgrade_costs['cost'] * 1.08
        return(base_costs,upgrade_costs)
    
    if difficulty == 'impoppable':
        base_costs['cost'] = base_costs['cost'] * 1.2
        upgrade_costs['cost'] = upgrade_costs['cost'] * 1.2
        return(base_costs,upgrade_costs)
    
    else:
        return(base_costs,upgrade_costs)