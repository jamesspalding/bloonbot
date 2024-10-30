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

    #setup
    pyautogui.hotkey('alt', 'tab')
    placement_coords = bb.define_grid()
    base_costs, upgrade_costs = bb.get_costs('easy') #Change difficulty if needed
    attempt_towers = pd.DataFrame()
    attempt_rounds = pd.DataFrame()
    starting_round = bb.get_round() #only needs to run once
    starting_round = starting_round - 1
    attempt = 0
    first_attempt = True
    run = True

    while run:

        if keyboard.is_pressed('p'): #quit program and export results to csv
            print('Quitting...')
            run = bb.stop_program(towers_df)

        #set initial values
        attempt = attempt + 1
        print(f"--------------- Attempt {attempt} ---------------")
        round = starting_round
        first_run = True 
        choice = 1
        spend_round = True

        
        if not first_attempt:
            attempt_towers = pd.concat([attempt_towers, towers_df], ignore_index=True)
            attempt_towers.to_csv("data/tower_data.csv", index=False)

            attempt_rounds = pd.concat([attempt_rounds, rounds_df], ignore_index=True)
            attempt_rounds.to_csv("data/attempt_data.csv", index=False)
        first_attempt = False
            

        towers_df = pd.DataFrame()
        rounds_df = pd.DataFrame()
        last_money = 0
        last_hp = 0

        in_game = True

        while in_game:


            state = bb.round_state()

            if state != 0:

                if state == 2:
                    print('Game Over')
                    print('Restarting...')
                    rounds_df = pd.DataFrame({'attempt':[attempt],
                                              'fin_round':round,
                                              'fin_lives':last_hp,
                                              'fin_cash':last_money})
                    break #exits loop


                if state == 3:
                    print('Entering Freeplay')

                #check round stats
                round = round + 1
                print(f"-------Round {round}-------")
                try:
                    hp, money = bb.get_game_info()
                    print(f"Lives: {hp} Money: {money}")
                except:
                    print('Tesseract error: starting round')
                    pydirectinput.press('space')
                    continue #if money/hp cannot be determined, round is not recorded


                #place towers
                if not first_run: 
                    spend_round = bb.spend(money,hp,last_money,last_hp)
                    ########## Make better way to determine if buy/upgrade ##########
                    choice = random.randint(1, 2) 


                if spend_round:
                    if  choice == 1: #make a better way later
                        tempdf = bb.place_tower(base_costs,placement_coords,towers_df,money,attempt,round)
                        if tempdf is not None:
                            towers_df = tempdf
                        print(towers_df)

                    else:
                        tempdf = bb.upgrade_tower(towers_df,upgrade_costs,money)
                        if tempdf is not None:
                            towers_df = tempdf
                        print(towers_df)



                #start round
                if first_run:
                    pydirectinput.press('space') #enable ff
                    first_run = False

                last_hp = hp
                last_money = money
                pydirectinput.press('space')








if __name__ == '__main__':
    main()