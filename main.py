import pytesseract
import re
import pyautogui
import pydirectinput
import time
from PIL import ImageGrab, Image

#load tesseract
tess_path = 'C:/Users/james/AppData/Local/Programs/Tesseract-OCR/tesseract.exe'
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

# get_game_info()








import cv2
import numpy as np

#recognize round end
def is_new_round():
    
    pyautogui.hotkey('alt', 'prtscr')
    img = ImageGrab.grabclipboard()
    img.save('temp.png')

    play_button = cv2.imread('play_button.png')
    screen = cv2.imread('temp.png')

    result = cv2.matchTemplate(screen, play_button, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= .8)

    if len(locations[0]) > 0:
        return(True)
    else:
        return(False)










import keyboard


#main func
round = int(input("Enter starting round: "))
pyautogui.hotkey('alt', 'tab')


while True:
    if keyboard.is_pressed('q'):
        print('Ending...')
        break
    else:

        time.sleep(2)
        if is_new_round():
            print('Round ',round)
            round = round+1
            print(get_game_info())
            pydirectinput.press('space')
        else:
            print('Ongoing round')
            