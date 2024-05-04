from utils import *
# from copy import deepcopy

unapplied_formula = {}
formula = {}
assignment = []

watch = {}
contradiction = []
unit_stack = []

def deepcopy_formula(formula) :
    return { i: c for i, c in formula.items() }

def make_2wl () :
    global formula, watch

    for i, c in formula.items() : 
        l = len(c) 
        # ensure(l > 0, "making 2wl for a contradictory formula")
        if l == 1 :
            e, *_ = c
            watch[i] = [e]
            unit_stack.append(i)
        else : 
            e, f, *_ = c
            watch[i] = [e, f]

def serious_assign_clause (assignment, clause) : 
    for (asm, _) in assignment : 
        if asm in clause: return None
        if -asm in clause: clause = clause.difference([-asm])
    return clause

def get_new_watch (ind) : 
    global assignment
    clause = serious_assign_clause (assignment, formula[ind])
    # DEBUG("assigning clause", formula[ind], clause)
    if clause is None: 
        del formula[ind]
        return None
    formula[ind] = clause

    if len(clause) == 0: 
        contradiction.append(ind) 
        return []

    if len(clause) == 1: 
        unit_stack.append(ind)
        e, *_ = clause
        return [e]

    e, f, *_ = clause
    return [e, f]

def assign_formula (lit): 
    global formula, watch, assignment 
    
    new_watch = {}
    for i, w in watch.items(): 
        if lit in w :           
            del formula[i]
        elif -lit in w :        
            new_w = get_new_watch(i)
            if new_w is not None :  new_watch[i] = new_w
        else:                   
            new_watch[i] = w

        if i in new_watch and new_watch[i] == []:  
            contradiction.append(i)
    watch = new_watch

def evaluate_assignment ():
    global assignment
    for (asm, _) in assignment :
        assign_formula (asm)

def unit_propagate (): 
    global unit_stack, formula, assignment

    while len(unit_stack) :
        # if len(contradiction) != 0: return 

        ind = unit_stack.pop()
        if ind not in formula : continue
        if len(formula[ind]) != 1 : continue

        lit = list(formula[ind])[0]
        # DEBUG("unit propagting", lit)
        assignment.append((lit, ind))
        assign_formula(lit)

        # DEBUG("solving", formula)
        # DEBUG("assigning", assignment)

def resolution (c1: Clause, c2: Clause, lit: Literal) -> Clause : 
    # ensure (c1 != None and c2 != None, "resolution cannot take on empty clause")
    # ensure ((lit in c1 and -lit in c2) or (-lit in c1 and lit in c2),                   # type: ignore 
    #         "given literal is not a resoluble literal")

    return c1.union(c2) - set([lit, -lit])                                              # type: ignore

def learn (conflictid) : 
    global unapplied_formula, assignment 

    # DEBUG("unapplied_formula", unapplied_formula)

    conflict = unapplied_formula[conflictid]
    # ensure (conflict != None, "learning a formula without conflict") 
    for (asm, ind) in reversed(assignment) :
        if ind < 0 : continue
        if asm not in conflict and -asm not in conflict : continue                      # type: ignore
        conflict = resolution (conflict, unapplied_formula[ind], asm)
    # DEBUG("learned", conflict)
    return conflict

def backtrack (clause) : 
    global assignment
    # IDEA: a constant backtrack can be done. 
    l = 0 
    r = len(assignment)-1
    while (l < r) : 
        mid = (l+r+1)//2
        if serious_assign_clause(assignment[:mid], clause) == set() :
            r = mid-1
        else : 
            l = mid
    assignment = assignment[:l]

def decision () -> Literal : 
    global formula

    for clause in formula.values() : 
        if clause != None : 
            e, *_ = clause
            return e
    raise Exception("formula is satisfied but reach decision")

def solve (f: Formula) -> Assignment | None :
    global unapplied_formula, formula, assignment, contradiction, unit_stack

    unapplied_formula = deepcopy_formula(f)
    formula = f
    assignment = []
    make_2wl () 

    while True:

        # DEBUG("solving", formula)
        # DEBUG("assigning", assignment)
        # DEBUG("watching", watch)
        
        unit_propagate()

        if formula == {} :
            # DEBUG("found")
            return assignment

        has_learned = False 
        while len(contradiction) != 0 : 
            ind = contradiction.pop() 
            if contradiction is None : continue 
            learned_clause = learn(ind)

            if learned_clause == set() : 
                # DEBUG("unsat")
                # DEBUG("result formula length: ", len(unapplied_formula))
                return None

            length = len(unapplied_formula) 
            unapplied_formula[length] = learned_clause

            # DEBUG("unapplied_formula turned into", unapplied_formula)
            backtrack(learned_clause)
            contradiction = []
            unit_stack = []

            formula = deepcopy_formula(unapplied_formula)
            make_2wl()
            evaluate_assignment()
            has_learned = True
            break

        if not has_learned :
            lit = decision()
            # ensure (lit not in map_first(assignment), "decision cannot be assigned variable")
            assignment.append((lit, -1))
            # DEBUG("guessing", lit)
            assign_formula(lit)

