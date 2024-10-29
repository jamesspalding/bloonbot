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
import random

#load tesseract
with open("assets/tess_path.txt") as my_file:
    tess_path = my_file.read()
pytesseract.pytesseract.tesseract_cmd = tess_path


#extract text from image
def img_to_num(img):   
    imgstr = pytesseract.image_to_string(img, lang='bloons')
    imgstr = imgstr.replace(',', '')
    num_list = [int(s) for s in re.findall(r'\d+', imgstr)]
    return(num_list)


#self explanitory
def screen_cap():
    pyautogui.hotkey('alt', 'prtscr')
    img = ImageGrab.grabclipboard()
    img.save('temp.png')
    return(cv2.imread('temp.png'))


#get round
def get_round():
    screen_cap()
    im = Image.open('temp.png')
    width, height = im.size

    left = .745 * width
    right = .814 * width
    top = .055 * height
    bottom = .1 * height
    im2 = im.crop((left, top, right, bottom))
    im2.save('temp2.png')

    #obscure image
    image = Image.open("temp2.png").convert("L")
    image = image.point(lambda p: 255 if p > 250 else 0) #extract ONLY numbers
    image.save("temp2.png")
    round = img_to_num('temp2.png')
    round = round[0]

    return(round)


#get hp, money
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
    image = image.point(lambda p: 255 if p > 200 else 0)
    image.save("temp1.png")

    return(img_to_num('temp1.png'))


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
    return(pd.DataFrame(coordinates))


#get money values as df
def get_costs(difficulty):
    base_costs = pd.read_csv('assets/base_costs2.csv')
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


#place tower
def place_tower(base_costs,coords,towers_df,money):

    #select tower
    towers_afforded = base_costs[base_costs['cost'] <= money]
    if(len(towers_afforded) == 0):
        print('No money available.')
        return

    tower = towers_afforded.sample(n=1)
    tower = tower.reset_index(drop=True)
    name = tower['tower'].iloc[0]
    hotkey = tower['hotkey'].iloc[0]
    cost = float(tower['cost'].iloc[0])

    iteration = 0
    while True: #loops until valid placement found
        iteration = iteration + 1

        # select space and drop from coords
        space = coords.sample(n=1)
        coords = coords.drop(space.index).reset_index(drop=True) #drop space from pool after selected
        space = space.reset_index(drop=True)
        x=float(space[0].iloc[0])
        y=float(space[1].iloc[0])

        #try to place tower
        pyautogui.moveTo(x, y)
        pydirectinput.press(hotkey)
        pydirectinput.click()
    
        #check if money went down, skip if tesseract can't read money
        try:
            _, new_money = get_game_info()

            if(new_money != money):
                print(f"{name} placed at ({x},{y})")
                break

            if(iteration > 9): #10 tries to find valid placement
                print('No location found.')
                pydirectinput.press('esc') #deselects tower
                return

        except ValueError:
            print('Tesseract error, skipping...')
            return


    placement_list = [x, y, name, 0, 0, 0] #coords, type, upgrades
    df = pd.DataFrame([placement_list], columns=["x", "y", "type", "top_path", "middle_path", "bottom_path"])
    towers_df = towers_df._append(df)
    return(towers_df)




#determine to save or spend for round
def spend(money,lives,last_money,last_lives): #manually tweak these values to find best performance
    result = False
    lives_probs = 0
    money_probs = 0
    random_chance = 20

    if lives != last_lives:
        lives_lost = last_lives - lives
        lives_probs = 15 * lives_lost
    
    if money > last_money:
        round_money = last_money - money
        money_probs = round_money/30

    totprobs = lives_probs + money_probs + random_chance
    selection = random.randint(1, 100)

    if selection <= totprobs:
        result = True

    if result:
        print("Spending")
    else:
        print("Saving")

    return(result)



def stop_program(towers_df):
    towers_df.to_csv('data.csv', index=False)
    return(False)



# def upgrade_tower(towers_df, upgrade_costs, money):
#     i=0
#     locked_path = 'none'
#     while True:
#         selected_tower = towers_df.sample(1)
#         original_index = selected_tower.index[0]

#         #check for crosspath
#         upgraded_paths = int(sum([(selected_tower['top_path'].iloc[0] != 0),(selected_tower['middle_path'].iloc[0] != 0),(selected_tower['bottom_path'].iloc[0] != 0)]))
#         if upgraded_paths == 2:
#             locked_path = selected_tower.columns[selected_tower.eq(0).any()][0]

#             print(f"{locked_path} is locked")

#             available_upgrades = upgrade_costs[(upgrade_costs['tower'].isin(selected_tower['type']))&
#                                                (upgrade_costs['cost']<money)&
#                                                (upgrade_costs['path'] != locked_path)]
            
#         else:
#             available_upgrades = upgrade_costs[(upgrade_costs['tower'].isin(selected_tower['type']))&
#                                                (upgrade_costs['cost']<money)]

#         available_upgrades = available_upgrades[((available_upgrades['path']==('top_path'))&
#                                                 (available_upgrades['tier']==selected_tower['top_path'].iloc[0]+1))|
#                                                 ((available_upgrades['path']==('middle_path'))&
#                                                 (available_upgrades['tier']==selected_tower['middle_path'].iloc[0]+1))|
#                                                 ((available_upgrades['path']==('bottom_path'))&
#                                                 (available_upgrades['tier']==selected_tower['bottom_path'].iloc[0]+1))]


#         if len(available_upgrades) != 0:
#             selected_upgrade = available_upgrades.sample(1)
#             break

#         i=i+1
#         if i == 5:
#             print('No upgrades found.')
#             break


#     x=float(selected_tower['x'].iloc[0])
#     y=float(selected_tower['y'].iloc[0])
#     pyautogui.moveTo(x, y)
#     pydirectinput.click()

#     selected_upgrade_path = selected_upgrade['path'].iloc[0]

#     if selected_upgrade_path == 'top_path':
#         pydirectinput.press(',')
#         selected_tower['top_path'] = selected_tower['top_path'] + 1
#         pydirectinput.press('esc')

#     if selected_upgrade_path == 'middle_path':
#         pydirectinput.press('.')
#         selected_tower['middle_path'] = selected_tower['middle_path'] + 1
#         pydirectinput.press('esc')

#     if selected_upgrade_path == 'bottom_path':
#         pydirectinput.press('/')
#         selected_tower['bottom_path'] = selected_tower['bottom_path'] + 1
#         pydirectinput.press('esc')

#     towers_df.loc[original_index] = selected_tower.iloc[0].values
#     print(f"{selected_tower['type'].iloc[0]} upgraded to ({selected_tower['top_path'].iloc[0]},{selected_tower['middle_path'].iloc[0]},{selected_tower['bottom_path'].iloc[0]})")
#     return(towers_df)
    





def upgrade_tower(towers_df, upgrade_costs, money):
    i = 0
    locked_path = 'none'
    
    while True:
        # Sample one tower from towers_df
        selected_tower = towers_df.sample(1)
        original_index = selected_tower.index[0]  # Capture the original index

        # Check for crosspath
        upgraded_paths = int(sum([(selected_tower['top_path'].iloc[0] != 0),
                                   (selected_tower['middle_path'].iloc[0] != 0),
                                   (selected_tower['bottom_path'].iloc[0] != 0)]))
        if upgraded_paths == 2:
            locked_path = selected_tower.columns[selected_tower.eq(0).any()][0]
            print(f"{locked_path} is locked")

            available_upgrades = upgrade_costs[(upgrade_costs['tower'].isin(selected_tower['type'])) &
                                               (upgrade_costs['cost'] < money) &
                                               (upgrade_costs['path'] != locked_path)]
        else:
            available_upgrades = upgrade_costs[(upgrade_costs['tower'].isin(selected_tower['type'])) &
                                               (upgrade_costs['cost'] < money)]

        available_upgrades = available_upgrades[
            ((available_upgrades['path'] == 'top_path') & 
             (available_upgrades['tier'] == selected_tower['top_path'].iloc[0] + 1)) |
            ((available_upgrades['path'] == 'middle_path') & 
             (available_upgrades['tier'] == selected_tower['middle_path'].iloc[0] + 1)) |
            ((available_upgrades['path'] == 'bottom_path') & 
             (available_upgrades['tier'] == selected_tower['bottom_path'].iloc[0] + 1))
        ]

        if len(available_upgrades) != 0:
            selected_upgrade = available_upgrades.sample(1)
            break

        i += 1
        if i == 5:
            print('No upgrades found.')
            return towers_df

    # Place the tower
    x = float(selected_tower['x'].iloc[0])
    y = float(selected_tower['y'].iloc[0])
    pyautogui.moveTo(x, y)
    pydirectinput.click()

    selected_upgrade_path = selected_upgrade['path'].iloc[0]

    # Upgrade the selected tower's path
    if selected_upgrade_path == 'top_path':
        pydirectinput.press(',')
        towers_df.at[original_index, 'top_path'] += 1  # Update using .at for single scalar
    elif selected_upgrade_path == 'middle_path':
        pydirectinput.press('.')
        towers_df.at[original_index, 'middle_path'] += 1  # Update using .at for single scalar
    elif selected_upgrade_path == 'bottom_path':
        pydirectinput.press('/')
        towers_df.at[original_index, 'bottom_path'] += 1  # Update using .at for single scalar

    pydirectinput.press('esc')

    # No need to reassign the entire selected_tower; just update the specific paths
    print(f"{selected_tower['type'].iloc[0]} upgraded to "
          f"({towers_df.at[original_index, 'top_path']}, "
          f"{towers_df.at[original_index, 'middle_path']}, "
          f"{towers_df.at[original_index, 'bottom_path']})")
    
    return towers_df