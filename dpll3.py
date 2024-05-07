from utils import *
import decision
import state
import random

def assign_clause (assignment_lit, clause: Clause) -> Clause | None : 
    for asm in assignment_lit : 
        if asm in clause: return None
        if -asm in clause: clause = clause.difference([-asm])
    return clause

def get_2wl (index):
    global state
    clause = state.formula[index] 

    wl = []
    while state.clause_length[index] != 0:
        elem = clause.pop()
        state.clause_length[index] -= 1
        if elem in state.assignment_lit: return None
        if -elem in state.assignment_lit: continue

        wl.append(elem)
        if len(wl) == 2: break

    for w in wl:
        clause.add(w)
        state.clause_length[index] += 1

    state.formula[index] = clause
    return set(wl)

def assign_formula (asm):
    global state

    for index, clause in state.watch.items():
        for lit in clause :
            if -lit in asm: 
                state.watch[index] = get_2wl(index)
                break
            if lit in asm: 
                state.watch[index] = None
                break
        if state.watch[index] == None:
            del state.clause_length[index]
            del state.formula[index]

    state.watch = {i:c for i, c in state.watch.items() if c is not None}

def get_clauses_with_length (n) :
    return (i for i in state.watch.keys() if state.clause_length[i] == n)

def unit_propagate () :
    stack = get_clauses_with_length(1)
    try: 
        while True:
            ind = next(stack)
            if ind not in state.formula: continue
            if state.clause_length[ind] == 0: continue

            lit = list(state.formula[ind])[0]
            state.add_assignment(lit, ind)
            assign_formula([lit])
            stack = get_clauses_with_length(1)
    except StopIteration:
        return

def backtrack (clause: Clause) : 
    # IDEA: a constant backtrack can be done. 
    l, r = 0, len(state.assignment_lit)-1
    while l < r: 
        mid = (l+r+1)//2
        if assign_clause(state.assignment_lit[:mid], clause) == set() :
            r = mid-1
        else : 
            l = mid

    state.rollback_assignment(l)

def resolution (c1: Clause, c2: Clause, lit: Literal) -> Clause : 
    return c1.union(c2) - set([lit, -lit])                                             

def learn (conflictid: int) -> Clause : 

    conflict = state.unapplied_formula[conflictid]
    for (asm, ind) in reversed(state.assignment) :
        if ind <= 0 : continue
        if asm not in conflict and -asm not in conflict : continue          
        decision.on_learn_path(state.unapplied_formula[ind])
        state.on_learn_path(ind)
        conflict = resolution (conflict, state.unapplied_formula[ind], asm)   
    return conflict

restart_interval = 36
restart_treshold = 36
restart_growth = 1.1
def should_restart () -> bool :
    global restart_treshold, restart_interval, restart_growth
    if state.conflict_count >= restart_treshold: 
        restart_interval *= restart_growth
        restart_treshold += restart_interval
        return True
    return False

total_forgot = 0
def forget () :
    global state, total_forgot
    forget = 0
    num_forget = restart_interval * 0.15

    while forget < num_forget:
        if state.conflict_activity == {}: return 
        m = min(state.conflict_activity.values())
        for key, val in state.conflict_activity.items(): 
            if val == m: 
                try: 
                    del state.formula[key]
                    del state.unapplied_formula[key]
                    del state.watch[key]
                except: 
                    pass
                state.conflict_activity[key] = None
                forget += 1
        state.conflict_activity = {i:c for i, c in state.conflict_activity.items() if c is not None}
    total_forgot += forget

def solve (f: Formula) -> Assignment | None :
    
    state.init(f)
    random.seed(state.seed)
    decision.init()

    while True:

        unit_propagate()

        if state.watch == {} : 
            DEBUG("result formula length: ", len(state.unapplied_formula))
            return state.assignment 

        has_learned = False
        contradicts = get_clauses_with_length(0)
        try: 
            while True: 
                contradict = next(contradicts)
                if contradict == None: continue
                learned_clause = learn(contradict)
                state.conflict_count += 1

                if learned_clause == set() : 
                    DEBUG("unsat")
                    DEBUG("result formula length: ", len(state.unapplied_formula))
                    DEBUG("total forget", total_forgot)
                    return None

                nxt = state.next_formula_index()
                state.unapplied_formula[nxt] = learned_clause
                state.formula = copy_formula(state.unapplied_formula)

                decision.on_learn(learned_clause)

                if should_restart() : 
                    # print("restart")
                    forget()
                    decision.on_restart()
                    state.rollback_assignment(1)
                    state.formula = copy_formula(state.unapplied_formula)
                else: 
                    backtrack(learned_clause)


                state.regularize()
                assign_formula(state.assignment_lit)
                contradicts = get_clauses_with_length(0)
                has_learned = True
        except StopIteration:
            pass
            
        if not has_learned: 
            lit = decision.get()
            state.add_assignment(lit)
            assign_formula([lit])
