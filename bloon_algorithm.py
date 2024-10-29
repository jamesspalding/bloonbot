import pandas as pd
import random

# tower_data = pd.read_csv('data/tower_data.csv')
# attempt_data = pd.read_csv('data/attempt_data.csv') # Must be divisible by 2. remove random obs if not.



# given attempt data, return top percentage of population in pairs
def get_top_attempts(attempt_data,percentage=.5,show_table=False):
    top_length = int(len(attempt_data)/2)
    mid_rounds = attempt_data['fin_round'].quantile(percentage)

    top_attempts = attempt_data[attempt_data['fin_round'] >= mid_rounds]
    top_attempts = top_attempts.sort_values(by=['fin_round','fin_lives', 'fin_cash'], ascending=[False,False,False]).reset_index(drop=True)
    top_attempts = top_attempts.iloc[0:top_length]

    if show_table:
        print(top_attempts)

    #create pairs
    top_attempts = list(top_attempts['attempt'])
    random.shuffle(top_attempts)
    parents = [top_attempts[i:i+2] for i in range(0, len(top_attempts), 2)]
    
    return parents



# Create child attempt from 2 parent attempts either colwise (inheritance) or rowwise (crossover)
def create_child(parents, tower_data, method):
    top_attempt_towers = tower_data[tower_data['attempt'].isin(parents)]
    parent1 = top_attempt_towers[top_attempt_towers['attempt']==parents[0]].drop('attempt', axis=1).reset_index(drop=True)
    parent2 = top_attempt_towers[top_attempt_towers['attempt']==parents[1]].drop('attempt', axis=1).reset_index(drop=True)

    ### Inherit columns (round_placed, location, tower, upgrades) from parent 2, rest from parent 1
    inherit_cols = random.sample([0,1,3,4],2) 
    if 1 in inherit_cols: #if x selected, include y
        inherit_cols.append(2)

    if 4 in inherit_cols: #if top path selected, inclue other paths
        inherit_cols.extend([5,6])

    #replace selected cols from parent2
    child_inheritance = parent1.copy()
    child_len = min(len(parent1), len(parent2))
    for col_index in inherit_cols:
        if col_index < child_len:
            child_inheritance.iloc[:child_len, col_index] = parent2.iloc[:child_len, col_index]
    
    if method == 'inheritance':
        return child_inheritance

    ### Crossover rows from random threshold
    round_cutoff = parent1['round_placed'].sample(1).iloc[0]
    p1_split = parent1[parent1['round_placed'] <= round_cutoff]
    p2_split = parent2[parent2['round_placed'] > round_cutoff]

    child_crossover = pd.concat([p1_split, p2_split], axis=0, ignore_index=True)

    if method == 'crossover':
        return child_crossover
    
    return child_inheritance, child_crossover



# Randomly mutate a specic value within a child attempt
def create_mutation(mutate_child, base_costs):
    #select row/cols to mutate
    mutate_row = random.sample(range(0,len(mutate_child)),1)
    mutate_col = random.sample([0,1,3,4],1)
    if 1 in mutate_col: mutate_col.append(2)
    if 4 in mutate_col: mutate_col.extend([5,6])

    # Create mutation
    if 0 in mutate_col: #get valid round placed rounds by checking above and below
        lower = mutate_child['round_placed'][mutate_row[0]-1]
        upper = mutate_child['round_placed'][mutate_row[0]+1]
        mutate_val = random.randint(lower+1,upper-1)
        
    if 1 in mutate_col: #get valid xy coords
        #select random attempt from top attempts and use a random xy coord to ensure validity NEEDS WORK
        mutate_x = 0
        mutate_y = 0
        mutate_val = [mutate_x,mutate_y]

    if 3 in mutate_col: #select tower, check if afforded later
        mutate_val = base_costs['tower'].sample(1).iloc[0]
        

    if 4 in mutate_col: #create random upgrade path
        upgrade_levels = random.sample(range(1,5),3)
        upgrade_levels[random.sample(range(0,3),1)[0]] = 0
        max_value = max(upgrade_levels)
        if max_value > 2:
            upgrade_levels = [value if value == max_value else min(value, 2) if value > 1 else value for value in upgrade_levels] #leave max values alone, set any other upgrades past 2 to 2
        mutate_val = upgrade_levels

    mutate_child.iloc[mutate_row, mutate_col] = mutate_val
    return mutate_child