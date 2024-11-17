import pandas as pd
import pyautogui
import pydirectinput

def get_placement_pool():
    tower_costs = pd.read_csv('assets/base_costs2.csv')
    towers = pd.read_csv('data/tower_data.csv')
    attempts = pd.read_csv('data/attempt_data.csv')

    #get top 20 placements
    top_attempts = attempts.sort_values('fin_round',ascending=False).reset_index(drop=True)
    top_attempts = top_attempts.iloc[0:20] #select top 20 best attempts

    #add to pool
    top_towers = towers[towers['attempt'].isin(top_attempts['attempt'])]
    placement_pool = top_towers[['x','y','type','attempt']]
    placement_pool = pd.merge(placement_pool, tower_costs, left_on='type', right_on='tower')
    placement_pool = placement_pool.drop(['tower','range'],axis=1)

    return placement_pool

def pool_placement(placement_pool,towers_df,money,attempt,round):
    #instead of drawing from all towers and placing randomly, take from top towers and place accordingly
    afforded_towers = placement_pool[placement_pool['cost'] <= money]

    #select row, remove from index
    selected_tower = afforded_towers.sample(1)
    afforded_towers = afforded_towers.drop(selected_tower.index)

    name = selected_tower['type'].iloc[0]  
    hotkey = selected_tower['hotkey'].iloc[0]  
    x = int(selected_tower['x'].iloc[0])
    y = int(selected_tower['y'].iloc[0])

    #place tower
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