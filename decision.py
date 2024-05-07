from utils import *
import random
import state

vsids_score = {}
vsids_interval = 0
vsids_divisor = 2
 
berkmin_score = {}
berkmin_interval = 0
berkmin_divisor = 2

def init () : 
    global vsids_score, vsids_interval, vsids_divisor
    global berkmin_score, berkmin_interval, berkmin_divisor
    random.seed(state.seed)
    vsids_interval = 79
    vsids_score = state.count_var_occurrence()
    vsids_divisor = 1.8

    berkmin_interval = 57
    berkmin_score = state.count_var_occurrence()
    berkmin_divisor = 1.8

def on_restart (): 
    pass

def on_learn_path (conflict) :
    global berkmin_score
    for lit in conflict :
        berkmin_score[abs(lit)] += 1
    if state.conflict_count % berkmin_interval == 0:
        for i in berkmin_score.keys() : 
            berkmin_score[i] //= berkmin_divisor
    
def on_learn (conflict) : 
    global vsids_score
    on_learn_path(conflict)
    for lit in conflict :
        vsids_score[abs(lit)] += 1
    if state.conflict_count % vsids_interval == 0:
        for i in vsids_score.keys() : 
            vsids_score[i] //= vsids_divisor


def get () : 
    mom_chance = 0.95 ** state.conflict_count
    if random.random() < mom_chance : 
        return mom()
    return berkmin()

#######################################################################
###                         HEURISTICS                              ###
#######################################################################

def mom () -> Literal : 
    min_clause = min(state.clause_length.values())
    shortest_clauses = [state.formula[i] for i, c in state.clause_length.items() if c == min_clause] 

    count = {}
    for clause in shortest_clauses : 
        for lit in clause : 
            if lit in state.assignment_lit:  continue
            if -lit in state.assignment_lit: continue
            if lit not in count: 
                count[lit] = 0
            count[lit] += 1
    
    mx, mi = 0, []
    for i, c in count.items(): 
        if c > mx: 
            mx = c
            mi = []
        if c == mx: 
            mi.append(i)
    assert len(mi) != 0
    return random.choice(mi)

def vsids () -> Literal:
    global vsids_score
    mx, mi = -1, []
    for i in vsids_score.keys() : 
        if i in state.assignment_lit: continue
        if -i in state.assignment_lit: continue
        if vsids_score[i] > mx : 
            mx = vsids_score[i]
        if vsids_score[i] == mx:
            mi.append(i)
    return random.choice(mi) * (-1 if random.randint(0, 1) else 1)

def berkmin () -> Literal:
    global berkmin_score
    mx, mi = -1, []
    for i in berkmin_score.keys() : 
        if i in state.assignment_lit: continue
        if -i in state.assignment_lit: continue
        if berkmin_score[i] > mx : 
            mx = berkmin_score[i]
        if berkmin_score[i] == mx:
            mi.append(i)
    return random.choice(mi) * (-1 if random.randint(0, 1) else 1)

