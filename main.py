#Imports
import pyautogui
import pydirectinput
import time
import keyboard
import matplotlib.pyplot as plt
import pandas as pd
import random
import bloon_bot as bb
import bloon_algorithm as ba


def main():

    #----------- initial setup -----------#
    pyautogui.hotkey('alt', 'tab')
    placement_coords = bb.define_grid()
    base_costs, upgrade_costs = bb.get_costs('easy') #Change difficulty as needed
    attempt_towers = pd.DataFrame()
    attempt_rounds = pd.DataFrame()
    starting_round = bb.get_round() #only needs to run once
    starting_round = starting_round - 1
    attempt = 0
    first_attempt = True
    run = True

    while run:


        #----------- per-attempt setup -----------#
        attempt = attempt + 1
        print(f"\n--------------- Attempt {attempt} ---------------")
        round = starting_round
        first_run = True 
        spend_round = True
        
        if not first_attempt:
            print('Saving data to csv')
            attempt_towers = pd.concat([attempt_towers, towers_df], ignore_index=True)
            attempt_towers.to_csv("data/tower_data.csv", index=False)

            attempt_rounds = pd.concat([attempt_rounds, rounds_df], ignore_index=True)
            attempt_rounds.to_csv("data/attempt_data.csv", index=False)
        first_attempt = False

        towers_df = pd.DataFrame()
        rounds_df = pd.DataFrame()
        last_money = 0
        last_hp = 0
        spend_action = 'place'

        in_game = True

        while in_game:


            #----------- error handling -----------#
            state_error = 0 #temporary fix until solution found
            while True:
                if state_error == 5:
                    print('Could not solve error.')
                    break
                try:
                    state = bb.round_state()
                    break
                except AttributeError:
                    state_error = state_error+1
                    print(f"Failed to get state, trying again... ({state_error}/5)")
                    continue
            


            #----------- check round state -----------#
            if state != 0:

                if state == 2:
                    print('Game Over')
                    print('Restarting...')
                    rounds_df = pd.DataFrame({'attempt':[attempt],
                                              'fin_round':round,
                                              'fin_lives':last_hp,
                                              'fin_cash':last_money})
                    break #exits loop

                if state == 3: #automatically navigates freeplay menu
                    print('Entering Freeplay')



                #----------- get round stats -----------#
                round = round + 1
                print(f"\n-------Round {round}-------")
                for tess_attempt in range(1,6):
                    if tess_attempt == 5:
                        print('Could not obtain hp/money: starting round')
                        pydirectinput.press('space')
                        continue

                    try:
                        hp, money = bb.get_game_info()
                        print(f"Lives: {hp} Money: {money}")
                        break
                    except:
                        print(f"Tesseract error. Retrying ({tess_attempt}/5)")
                        continue



                #---------- round action -----------#
                if not first_run:
                    spend_round = bb.spend(money,hp,last_money,last_hp)
                    spend_action = bb.buy_action(towers_df)


                if spend_round:
                    if  spend_action == 'place':
                        tempdf = bb.place_tower(base_costs,placement_coords,towers_df,money,attempt,round)
                        if tempdf is not None:
                            towers_df = tempdf

                    if  spend_action == 'upgrade':
                        tempdf = bb.upgrade_tower(towers_df,upgrade_costs,money)
                        if tempdf is not None:
                            towers_df = tempdf



                #----------- start round -----------#
                if first_run:
                    pydirectinput.press('space') #enable ff
                    first_run = False

                last_hp = hp
                last_money = money
                pydirectinput.press('space')








if __name__ == '__main__':
    main()