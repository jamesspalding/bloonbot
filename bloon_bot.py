import pytesseract
import re
import pyautogui
import pydirectinput
import time
from PIL import ImageGrab, Image, ImageDraw
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import random
import pickle as pkl


#load tesseract
with open("assets/tess_path.txt") as my_file:
    tess_path = my_file.read()
pytesseract.pytesseract.tesseract_cmd = tess_path


#load data obtained from c#
def get_round_info():
    with open('game_data.txt', 'r') as file:
        content = file.read()

    round_dat = content.split('\n')
    round_dat = [int(x) for x in round_dat[:-1]]

    round = round_dat[0]
    cash = round_dat[1]
    hp = round_dat[2]

    return round, cash, hp


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
    # screen_cap()
    # im = Image.open('temp.png')
    # width, height = im.size

    # left = .745 * width
    # right = .814 * width
    # top = .055 * height
    # bottom = .1 * height
    # im2 = im.crop((left, top, right, bottom))
    # im2.save('temp2.png')

    # #obscure image
    # image = Image.open("temp2.png").convert("L")
    # image = image.point(lambda p: 255 if p > 250 else 0) #extract ONLY numbers
    # image.save("temp2.png")
    # round = img_to_num('temp2.png')
    # round = round[0]

    round,_,_ = get_round_info()

    return round


#get hp, money
def get_game_info():
    # screen_cap()
    # im = Image.open('temp.png')
    # width, height = im.size

    # ##### HP + Money #####
    # left = .07 * width
    # right = .30 * width
    # top = .048 * height
    # bottom = .1 * height
    # im1 = im.crop((left, top, right, bottom))
    # im1.save('temp1.png')

    # #obscure image
    # image = Image.open("temp1.png").convert("L")
    # draw = ImageDraw.Draw(image)
    # box_coordinates = (90, 0, 231, 70)
    # draw.rectangle(box_coordinates, fill="black")
    # image = image.point(lambda p: 255 if p > 200 else 0)
    # image.save("temp1.png")

    # return(img_to_num('temp1.png'))
    _,money,hp = get_round_info()
    
    return hp, money


#given button reference, return presence and location
def find_button(screen, button_path):
    button = cv2.imread(button_path)
    result = cv2.matchTemplate(screen, button, cv2.TM_CCOEFF_NORMED)
    location = np.where(result >= .8)
    is_present = len(location[0]) > 0
    return is_present, location


#recognize round end
def round_state():
    ###paused
    while True:
        screen = screen_cap()
        paused,_ = find_button(screen, 'assets/paused_button.png')
        shop,_ = find_button(screen,'assets/shop_button.png')

        if paused:
            print('Game paused. Unpausing...')
            pydirectinput.press('esc')
            time.sleep(.5)

        if shop:
            print('Shop opened. Closing...')
            pydirectinput.press('esc')
            time.sleep(.5)
            pydirectinput.press('esc')
            time.sleep(.5)

        else:
            break


    ###game over
    gameover,location = find_button(screen, 'assets/restart_button.png')
    
    if gameover:
        #click restart
        pyautogui.moveTo(location[0][0], location[1][0])
        pydirectinput.click()
        time.sleep(.5)

        #confirm restart
        pyautogui.moveTo(1130,750) #for 1080p
        pydirectinput.click()     
        time.sleep(.5)
        return(2)

    ###freeplay
    freeplay,location = find_button(screen,'assets/win_button.png')

    if freeplay:
        pyautogui.moveTo(location[1][0], location[0][0])
        pydirectinput.click()        
        time.sleep(.25)

        #manually click to avoid tesseract use
        im = Image.open('temp.png')
        width, height = im.size
        pyautogui.moveTo(.62*width, .8*height)
        pydirectinput.click()
        time.sleep(.25)

        pyautogui.moveTo(.5*width, .7*height)
        pydirectinput.click()
        time.sleep(.25)
        return(3)

    ###new round
    newround,_ = find_button(screen,'assets/play_button.png')

    if newround:
        return(1)

    else:
        return(0)



#gets all coords and valid placements
def initialize_placements(first = False):
    if first:
        print('Generating placement map')
        screen_cap()
        image = cv2.imread("temp.png")
        height,width,_ = image.shape

        colors = {
            'short': ([35, 190, 145], [55, 210, 165]),  # Green
            'track': ([70, 80, 95], [80, 100, 115]),  # Grey
            'medium': ([80, 135, 200], [100, 180, 245]),  # Tan
            'long': ([20, 20, 40], [40, 40, 80]),  # Maroon
            'inaccessible': ([70, 70, 0], [90, 90, 20])  # Blue
        }

        # convert to array
        colors = {label: (np.array(lower, dtype=np.uint8), np.array(upper, dtype=np.uint8)) for label, (lower, upper) in colors.items()}

        data = {
            "x": [],
            "y": [],
            "r": [],
            "g": [],
            "b": [],
            "label": []
        }

        for y in range(height):
            for x in range(width):
                b, g, r = image[y, x]
                data["x"].append(x)
                data["y"].append(y)
                data["r"].append(r)
                data["g"].append(g)
                data["b"].append(b)
                
                label = "unknown"
                for color_label, (lower, upper) in colors.items():
                    if cv2.inRange(image[y, x].reshape(1, 1, 3), lower, upper)[0][0] == 255:
                        label = color_label
                        break
                data["label"].append(label)

        df = pd.DataFrame(data)
        df.to_csv('assets/placements.csv',index=False)

    else:
        df = pd.read_csv('assets/placements.csv')

    return(df)



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



def place_tower(base_costs,placements,towers_df,money,attempt,round):

    #select tower
    towers_afforded = base_costs[base_costs['cost'] <= money]
    if(len(towers_afforded) == 0):
        print('No money available.')
        return

    tower = towers_afforded.sample(n=1)
    tower = tower.reset_index(drop=True)
    name = tower['tower'].iloc[0]
    hotkey = tower['hotkey'].iloc[0]

    if tower['range'].iloc[0] == 'short':
        coords = placements[placements['label'] == 'short']

    if tower['range'].iloc[0] == 'medium':
        coords = placements[(placements['label'] == 'short')|
                            (placements['label'] == 'medium')]
        
    if tower['range'].iloc[0] == 'long':
        coords = placements[(placements['label'] == 'short')|
                            (placements['label'] == 'medium')|
                            (placements['label'] == 'long')]

    # select space and drop from coords
    space = coords.sample(n=1)
    placements = placements.drop(space.index).reset_index(drop=True) #drop space from pool after selected
    space = space.reset_index(drop=True)
    x=int(space['x'][0])
    y=int(space['y'][0])

    #try to place tower
    pyautogui.moveTo(x, y)
    pydirectinput.press(hotkey)
    pydirectinput.press('tab') #autonudge
    x,y = pyautogui.position() #get new position
    pydirectinput.click()
    print(f"{name} placed at ({x},{y})")

    placement_list = [attempt, round, x, y, name, 0, 0, 0] #coords, type, upgrades
    df = pd.DataFrame([placement_list], columns=["attempt", "round_placed", "x", "y", "type", "top_path", "middle_path", "bottom_path"])
    try:
        towers_df = pd.concat([towers_df,df], ignore_index=True)
    except:
        print("Error appending. Continuing...")
    return(towers_df)




#determine to save or spend for round
# def spend(money,lives,last_money,last_lives): #manually tweak these values to find best performance
#     result = False
#     lives_probs = 0
#     money_probs = 0
#     random_chance = 20

#     if lives != last_lives:
#         lives_lost = last_lives - lives
#         lives_probs = 15 * lives_lost
    
#     if money > last_money:
#         round_money = last_money - money
#         money_probs = round_money/10

#     totprobs = lives_probs + money_probs + random_chance
#     selection = random.randint(1, 100)

#     if selection <= totprobs:
#         result = True

#     if result:
#         print("Spending")
#     else:
#         print("Saving")

#     return(result)


#upgrades tower and updates df
def upgrade_tower(towers_df, upgrade_costs, money):
    i = 0
    locked_path = 'none'
    
    while True:
        selected_tower = towers_df.sample(1)
        original_index = selected_tower.index[0]

        # Check for crosspath
        upgraded_paths = int(sum([(selected_tower['top_path'].iloc[0] != 0),
                                   (selected_tower['middle_path'].iloc[0] != 0),
                                   (selected_tower['bottom_path'].iloc[0] != 0)]))
        
        if upgraded_paths == 2:
            locked_path = selected_tower.columns[selected_tower.eq(0).any()][0]
            print(f"{locked_path} is locked")

            #check for tier 3
            locked_path2 = 999
            if (selected_tower['top_path'].iloc[0] > 2) | (selected_tower['middle_path'].iloc[0] > 2) | (selected_tower['bottom_path'].iloc[0] > 2):
                locked_path2 = selected_tower.columns[selected_tower[['top_path','middle_path','bottom_path']].max(axis=1)][0]

            available_upgrades = upgrade_costs[(upgrade_costs['tower'].isin(selected_tower['type'])) &
                                               (upgrade_costs['cost'] < money) &
                                               (upgrade_costs['path'] != locked_path) &
                                               (upgrade_costs['path'] != locked_path2)]
        else:
            available_upgrades = upgrade_costs[(upgrade_costs['tower'].isin(selected_tower['type'])) &
                                               (upgrade_costs['cost'] < money)]

        available_upgrades = available_upgrades[
            ((available_upgrades['path'] == 'top_path') & 
             (available_upgrades['tier'] == selected_tower['top_path'].iloc[0] + 1)) |
            ((available_upgrades['path'] == 'middle_path') & 
             (available_upgrades['tier'] == selected_tower['middle_path'].iloc[0] + 1)) |
            ((available_upgrades['path'] == 'bottom_path') & 
             (available_upgrades['tier'] == selected_tower['bottom_path'].iloc[0] + 1))]

        if len(available_upgrades) != 0:
            selected_upgrade = available_upgrades.sample(1)
            break

        i += 1
        if i == 5:
            print('No upgrades available.')
            return towers_df

    # Select tower
    x = float(selected_tower['x'].iloc[0])
    y = float(selected_tower['y'].iloc[0])
    pyautogui.moveTo(x, y)
    pydirectinput.click()

    selected_upgrade_path = selected_upgrade['path'].iloc[0]

    # Upgrade the selected tower's path
    if selected_upgrade_path == 'top_path':
        pydirectinput.press(',')
        towers_df.at[original_index, 'top_path'] += 1
    elif selected_upgrade_path == 'middle_path':
        pydirectinput.press('.')
        towers_df.at[original_index, 'middle_path'] += 1 
    elif selected_upgrade_path == 'bottom_path':
        pydirectinput.press('/')
        towers_df.at[original_index, 'bottom_path'] += 1 

    pydirectinput.press('esc')

    print(f"{selected_tower['type'].iloc[0]} upgraded to "
          f"({towers_df.at[original_index, 'top_path']}, "
          f"{towers_df.at[original_index, 'middle_path']}, "
          f"{towers_df.at[original_index, 'bottom_path']})")
    
    return towers_df



#starts at 80% chance to place, goes down 5% per tower placed, capping at 20%
def buy_action(data): 
    n_towers = len(data)
    if n_towers <= 7:
        base_place = 80

        tower_factor = n_towers * 10
        new_buy = base_place - tower_factor
    
    else:
        new_buy = 10

    if random.randint(0,100) <= new_buy:
        return 'place'
    else:
        return 'upgrade'
