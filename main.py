#Imports
import pyautogui
import pydirectinput
import time
import keyboard
import matplotlib.pyplot as plt
import pandas as pd
import random
import bloon_bot as bb
import placement_selection as ps


def main(read_data = False):

    #----------- initial setup -----------#
    pyautogui.hotkey('alt', 'tab')
    placement_coords = bb.initialize_placements()
    base_costs, upgrade_costs = bb.get_costs('easy') #Change difficulty as needed
    bloon_data = pd.read_csv('assets/bloon_rounds.csv')
    attempt_towers = pd.read_csv('data/tower_data.csv')
    attempt_data = pd.read_csv('data/attempt_data.csv')
    attempt_rounds = pd.read_csv('data/rounds_data.csv')
    starting_round = bb.get_round() #only needs to run once
    starting_round = starting_round - 1
    attempt = list(attempt_data['attempt'])[-1] #gets most recent attempt
    first_attempt = True
    run = True

    while run:


        #----------- per-attempt setup -----------#
        attempt = attempt + 1
        print(f"\n--------------- Attempt {attempt} ---------------")

        round = starting_round
        first_round = True 
        spend_round = True
        
        if not first_attempt:
            #save data
            print('Saving data to csv')
            attempt_towers = pd.concat([attempt_towers, towers_df], ignore_index=True)
            attempt_towers.to_csv("data/tower_data.csv", index=False)
            attempt_data = pd.concat([attempt_data, attempt_df], ignore_index=True)
            attempt_data.to_csv("data/attempt_data.csv", index=False)
            attempt_rounds.to_csv("data/rounds_data.csv", index=False)

            #load most recent data
            attempt_towers = pd.read_csv('data/tower_data.csv')
            attempt_data = pd.read_csv('data/attempt_data.csv')
            attempt_rounds = pd.read_csv('data/rounds_data.csv')

        first_attempt = False
        
        if read_data:
            placement_pool = ps.get_placement_pool() #updates top runs after each attempt
            print(f"Top Attempts: {set(placement_pool['attempt'])}")

        towers_df = pd.DataFrame()
        attempt_df = pd.DataFrame()
        last_money = 0
        last_hp = 200 #adjust for dif
        spend_action = 'place'
        num_actions = 1
        in_game = True

        while in_game:


            #----------- error handling -----------#
            state_error = 0
            while True:

                if round > 40:
                    for i in range(1,6): #use up to 5 abilities to save time, starting at round 41
                        pydirectinput.press(str(i))

                if state_error == 5:
                    print('Could not solve error.')
                    break
                try:
                    state = bb.round_state()
                    break
                except AttributeError:
                    state_error = state_error+1
                    print("Failed to get state, trying again...")
                    continue
            


            #----------- check round state -----------#
            if state != 0:

                if state == 2:
                    print('Game Over')
                    print('Restarting...')
                    attempt_df = pd.DataFrame({'attempt':[attempt],
                                              'fin_round':round,
                                              'fin_lives':last_hp,
                                              'fin_cash':last_money})
                    break #exits loop

                if state == 3: #automatically navigates freeplay menu
                    print('Entering Freeplay')



                #----------- get round stats -----------#
                round = round + 1
                print(f"\n-------Round {round}-------")
                for tess_attempt in range(1,7):
                    if tess_attempt == 4:
                        print('Could not obtain hp/money: starting round.')
                        continue

                    try:
                        hp, money = bb.get_game_info()
                        print(f"Lives: {hp} Money: {money}")
                        break
                    except:
                        print("Tesseract error. Retrying...")
                        continue



                #---------- round action -----------#
                num_actions = 1+(money // 2500) #tweak this
                rounds_df = pd.DataFrame({'attempt':[attempt],
                                          'round':round,
                                          'action':0,
                                          'lives':hp,
                                          'lives_lost':last_hp - hp,
                                          'cash':money})

                for i in range(num_actions):

                    if not first_round:
                        spend_round = bb.spend(towers_df,attempt_rounds,bloon_data)
                        spend_action = bb.buy_action(towers_df)

                    if spend_round:
                        print('Spending')
                        if  spend_action == 'place':
                            #determine placement strategy
                            if read_data:
                                #10% mutation chance to possibly discover new techniques
                                mutation = random.random() < 0.1  
                                if mutation:
                                    print('Mutation!')
                                    tempdf = bb.place_tower(base_costs,placement_coords,towers_df,money,attempt,round)
                                else:
                                    tempdf = ps.pool_placement(placement_pool,towers_df,money,attempt,round)

                            if not read_data:
                                tempdf = bb.place_tower(base_costs,placement_coords,towers_df,money,attempt,round)

                            if tempdf is not None:
                                towers_df = tempdf

                        if  spend_action == 'upgrade':
                            tempdf = bb.upgrade_tower(towers_df,upgrade_costs,money)
                            if tempdf is not None:
                                towers_df = tempdf
                    
                        #save info
                        rounds_df = pd.DataFrame({'attempt':[attempt],
                                                  'round':round,
                                                  'action':spend_action,
                                                  'lives':hp,
                                                  'lives_lost':last_hp - hp,
                                                  'cash':money})
                        attempt_rounds = pd.concat([attempt_rounds,rounds_df], ignore_index=True)

                    else:
                        print('Saving')
                        rounds_df = pd.DataFrame({'attempt':[attempt],
                                                  'round':round,
                                                  'action':'none',
                                                  'lives':hp,
                                                  'lives_lost':last_hp - hp,
                                                  'cash':money})
                        attempt_rounds = pd.concat([attempt_rounds,rounds_df], ignore_index=True)



                #----------- start round -----------#
                if first_round:
                    pydirectinput.press('space') #enable ff
                    first_round = False

                last_hp = hp
                last_money = money
                pydirectinput.press('space')








if __name__ == '__main__':
    main(read_data=True)