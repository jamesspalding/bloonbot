import pandas as pd
import pyautogui
import pydirectinput
import random
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, cohen_kappa_score, make_scorer
import pickle as pkl

##### generate parents for attempt #####
def get_placement_pool():
    tower_costs = pd.read_csv('assets/base_costs2.csv')
    towers = pd.read_csv('data/tower_data.csv')
    attempts = pd.read_csv('data/attempt_data.csv')

    #get top placements via tournament selection
    top_attempts = pd.DataFrame()
    for i in range(1,21):
        tournament = attempts.sample(5)
        attempts = attempts.drop(tournament.index)
        winner = tournament[tournament['fin_round']==int(tournament['fin_round'].max())].sample(1)
        top_attempts = pd.concat([top_attempts,winner], ignore_index=True)

    top_attempts = top_attempts.reset_index(drop=True)

    #add to pool
    top_towers = towers[towers['attempt'].isin(top_attempts['attempt'])]
    placement_pool = top_towers[['x','y','type','attempt']]
    placement_pool = pd.merge(placement_pool, tower_costs, left_on='type', right_on='tower')
    placement_pool = placement_pool.drop(['tower','range'],axis=1)

    return placement_pool


##### place towers based off parents #####
def pool_placement(placement_pool,towers_df,money,attempt,round):
    #instead of drawing from all towers and placing randomly, take from top towers and place accordingly
    afforded_towers = placement_pool[placement_pool['cost'] <= money]

    if afforded_towers.empty:
        print("Can't afford any towers. Skipping...")
        return None

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


#random forest for predicting lives lost
def spend(towers_df,attempt_rounds,bloon_data):
    with open('assets/round_pred_scale.pkl', 'rb') as f:
        scaler = pkl.load(f)

    with open('assets/round_predictions.pkl', 'rb') as f:
        model = pkl.load(f)

    #state lives lost in previous round, not current
    attempt_rounds['lives_lost'] = attempt_rounds['lives_lost'].shift(-1)
    attempt_rounds['lives_lost'] = attempt_rounds['lives_lost'].fillna(0)
    attempt_rounds['previous_action'] = attempt_rounds['action'].shift(1)
    attempt_rounds['previous_action'] = attempt_rounds['previous_action'].fillna('none')

    #add tower cols
    all_towers = ['super_monkey','ice_monkey','ninja_monkey','mortar_monkey',
                  'alchemist','glue_gunner','boomerang_monkey','dart_monkey',
                  'spike_factory','monkey_ace','sniper_monkey','wizard_monkey',
                  'monkey_village','druid_monkey','engineer','tack_shooter','bomb_shooter']

    for col in all_towers:
        attempt_rounds[col] = 0

    #current monkey placements
    for _, row in towers_df.iterrows():
        attempt = row['attempt']
        round_placed = row['round_placed']
        tower_type = row['type']
        
        mask = (attempt_rounds['attempt'] == attempt) & (attempt_rounds['round'] >= round_placed)
        attempt_rounds.loc[mask, tower_type] += 1

    #merge bloon data
    round_pred = pd.merge(attempt_rounds,bloon_data, left_on='round', right_on='Round')

    #prepare data
    round_pred = round_pred.drop(['attempt','action','Round','round','lives','lives_lost'],axis=1)
    round_pred = pd.get_dummies(round_pred)
    round_pred = round_pred.astype(int)

    #scale data
    scaled_data = scaler.fit_transform(round_pred)

    #predict if hp loss
    probabilities = model.predict_proba(scaled_data)[:, 1]
    prediction = (probabilities >= .35).astype(int) #tweak threshold here
    return prediction[-1]


##### Refit rf model #####
def refit_model():
    print('Fitting new model...')

    with open('assets/round_predictions.pkl', 'rb') as f:
        prior_model = pkl.load(f)

    towers = pd.read_csv('data/tower_data.csv')
    rounds = pd.read_csv('data/rounds_data.csv')
    bloon_data = pd.read_csv('assets/bloon_rounds.csv')

    #state lives lost in previous round, not current
    rounds['lives_lost'] = rounds['lives_lost'].shift(-1)
    rounds['lives_lost'] = rounds['lives_lost'].fillna(0)
    rounds['previous_action'] = rounds['action'].shift(1)
    rounds['previous_action'] = rounds['previous_action'].fillna('none')

    rounds['lost_hp'] = rounds['lives_lost'] != 0 #Response

    #add tower cols
    for col in list(set(towers['type'])):
        rounds[col] = 0

    #current monkey placements
    for _, row in towers.iterrows():
        attempt = row['attempt']
        round_placed = row['round_placed']
        tower_type = row['type']
        
        mask = (rounds['attempt'] == attempt) & (rounds['round'] >= round_placed)
        rounds.loc[mask, tower_type] += 1

    #merge bloon data
    round_pred = pd.merge(rounds,bloon_data, left_on='round', right_on='Round')

    #prepare data
    response = round_pred['lost_hp']
    round_pred = round_pred.drop(['attempt','action','Round','round','lives','lives_lost','lost_hp'],axis=1)
    round_pred = pd.get_dummies(round_pred)
    round_pred = round_pred.astype(int)

    #split
    X_train, X_test, y_train, y_test = train_test_split(round_pred, response, test_size=0.2)

    #scale
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    kappa_scorer = make_scorer(cohen_kappa_score)

    param_dist = {
        'n_estimators': [100, 200, 300, 400, 500],
        'max_depth': [None, 10, 20, 30, 40],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
        'max_features': ['sqrt', 'log2', None],
        'bootstrap': [True, False]
    }

    rf = RandomForestClassifier()

    #takes ~3 min
    best_model = RandomizedSearchCV(
        estimator=rf, 
        param_distributions=param_dist, 
        n_iter=50, 
        scoring=kappa_scorer, 
        cv=5, 
        n_jobs=-1,
        verbose=3
    )

    best_model.fit(X_train, y_train)
    prior_model.fit(X_train, y_train)

    new_pred = best_model.predict(X_test)
    prior_pred = prior_model.predict(X_test)

    new_kappa = cohen_kappa_score(y_train, new_pred)
    prior_kappa = cohen_kappa_score(y_train, prior_pred)

    if new_kappa > prior_kappa: #update model and scaler with new
        print("New model better. Updating...")

        with open('assets/round_predictions.pkl', 'wb') as f:
            pkl.dump(best_model, f)

        with open('assets/round_pred_scale.pkl', 'wb') as f:
            pkl.dump(scaler, f)

    else:
        print('Old classifier better.')

    return


