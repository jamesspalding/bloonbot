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

#load tesseract
with open("assets/tess_path.txt") as my_file:
    tess_path = my_file.read()
pytesseract.pytesseract.tesseract_cmd = tess_path


#extract text from image
def img_to_num(img):
    imgstr = pytesseract.image_to_string(img,config='--psm 6').replace(',', '')
    imgstr = imgstr.replace(';', '')
    return([int(s) for s in re.findall(r'\d+', imgstr)])


#returns health, money, and round
def get_game_info():

    pyautogui.hotkey('alt', 'prtscr')
    img = ImageGrab.grabclipboard()
    img.save('temp.png')
    im = Image.open('temp.png')
    width, height = im.size
    varlist = []
    
    while True:
        left = .07 * width
        right = .27 * width
        top = .048 * height
        bottom = .1 * height
        
        im1 = im.crop((left, top, right, bottom))
        im1.save('temp1.png')
        hpmoney = img_to_num('temp1.png')

        if len(hpmoney) !=2:
            print(len(hpmoney), ' value found, retrying...')
        else:
            varlist = hpmoney
            break

    if len(str(varlist[0])) > 3:
       varlist[0] = varlist[0] // 10

    return(varlist)


#self explanitory
def screen_cap():
    pyautogui.hotkey('alt', 'prtscr')
    img = ImageGrab.grabclipboard()
    img.save('temp.png')
    return(cv2.imread('temp.png'))


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