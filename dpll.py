from utils import *
from copy import deepcopy

unapplied_formula = {}
formula = {}
assignment = []

# def ensure_pure (ind) :
#     def dec (f) : 
#         def func (*args) : 
#             new_args = deepcopy(args)
#             result = f(*new_args)
#             for i in ind :
#                 assert new_args[i] == args[i]
#             return result
#         return func
#     return dec

def assign_clause (assignment: Assignment, clause: Clause) -> Clause | None : 
    for (asm, _) in assignment : 
        if asm in clause: return None
        if -asm in clause: clause = clause.difference([-asm])
    return clause

def assign_formula (assignment: Assignment) :
    global formula

    new_formula = {}

    for index, clause in formula.items():
        new_formula[index] = assign_clause(assignment, clause)

    formula = {index:clause for index, clause in new_formula.items() if clause is not None }

def get_contradicts () -> list[int] :
    global formula
    return [i for i, c in formula.items() if c == set()]

def get_units () -> list[int] :
    global formula
    return [i for i, c in formula.items() if len(c) == 1]

def pure_propagate () :
    global formula, assignment
    counter = count_occurrence()

    stable = False
    while stable == False: 
        stable = True
        for lit in counter.keys(): 
            if -lit not in counter.keys(): 
                assignment.append((lit, -2))
                assign_formula([(lit, -2)])
                counter = count_occurrence()
                stable = False

def unit_propagate () :
    global formula, assignment
    # ensure (formula == assign_formula(assignment, formula), "unit propagation only receive applied formula")
    stack = get_units()
    while len(stack) : 
        ind = stack.pop()
        if ind in formula:
            if len(formula[ind]) == 0: continue
            lit = list(formula[ind])[0]
            assignment.append((lit, ind))
            assign_formula([(lit, ind)])
            # RETURNING ON CONTRADICT HERE NAKES LEARNING WORSE
            stack = get_units()

def backtrack (clause: Clause) : 
    global assignment
    # TODO: a constant backtrack can be done. 
    l = 0 
    r = len(assignment)-1
    while (l < r) : 
        mid = (l+r+1)//2
        if assign_clause(assignment[:mid], clause) == set() :
            r = mid-1
        else : 
            l = mid
    assignment = assignment[:l]

# CAN WE RETURN NONE HERE?
def resolution (c1: Clause, c2: Clause, lit: Literal) -> Clause : 
    ensure (c1 != None and c2 != None, "resolution cannot take on empty clause")
    ensure ((lit in c1 and -lit in c2) or (-lit in c1 and lit in c2),                   # type: ignore 
            "given literal is not a resoluble literal")

    return c1.union(c2) - set([lit, -lit])                                              # type: ignore

def learn (conflictid: int) -> Clause : 
    global unapplied_formula, assignment

    conflict = unapplied_formula[conflictid]
    ensure (conflict != None, "learning a formula without conflict") 
    for (asm, ind) in reversed(assignment) :
        if ind == -1 : continue
        if ind == -2 : continue
        if asm not in conflict and -asm not in conflict : continue           # type: ignore
        conflict = resolution (conflict, unapplied_formula[ind], asm)
    return conflict

def count_occurrence () : 
    global formula

    count = {}
    for clause in formula.values() : 
        for lit in clause : 
            if lit not in count: 
                count[lit] = 0
            count[lit] += 1
    return count

def decision () -> Literal : 
    global formula

    for clause in formula.values() : 
        if clause != None : 
            return list(clause)[0]
    raise Exception("formula is satisfied but reach decision")
    # RANDOM IS DEFINITELY NOT A GOOD HEURISTIC

def solve (f: Formula) -> Assignment | None :
    global unapplied_formula, formula, assignment 

    unapplied_formula = f 
    formula = f

    assignment = []

    while True:
        # if len(assignment) != 0: DEBUG("top assign: ", assignment[-1])
        DEBUG("current asm: ", len(assignment), "formula remain: ", len(formula), "total: ", len(unapplied_formula))
        # DEBUG(assignment)
        
        unit_propagate()
        # pure_propagate()

        if formula == {} : 
            DEBUG("found assignment", assignment)
            DEBUG("result formula length: ", len(unapplied_formula))
            return assignment 

        has_learned = False
        contradicts = get_contradicts()
        while len(contradicts) != 0 and contradicts[0] != None: 
            # DEBUG("assignment: ", assignment)
            learned_clause = learn(contradicts[0])
            if learned_clause == set() : 
                DEBUG("unsat")
                DEBUG("result formula length: ", len(unapplied_formula))
                return None
            length = len(unapplied_formula) 
            unapplied_formula[length] = learned_clause
            backtrack(learned_clause)
            # formula = deepcopy(unapplied_formula)
            formula = unapplied_formula
            assign_formula(assignment)
            contradicts = get_contradicts()
            has_learned = True
            # DEBUG("LEARN", learned_clause)
            
        if not has_learned: 
            lit = decision()
            ensure (lit not in map_first(assignment), "decision cannot be assigned variable")
            assignment.append((lit, -1))
            # DEBUG("guessing", lit)
            assign_formula([(lit, -1)])

