import bloon_functions

round = int(input("Enter starting round: "))
pyautogui.hotkey('alt', 'tab')

def main():
    while True:
        if keyboard.is_pressed('q'):
            print('Ending...')
            break
        else:

            time.sleep(2) #time between checks
            if is_new_round():
                print('Round ',round)
                round = round+1
                print(get_game_info())
                pydirectinput.press('space')
            else:
                print('Ongoing round')  



if __name__ == '__main__':
    main()