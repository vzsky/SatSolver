from utils import *
from copy import deepcopy

def ensure_pure (ind) :
    def dec (f) : 
        def func (*args) : 
            new_args = deepcopy(args)
            result = f(*new_args)
            for i in ind :
                assert new_args[i] == args[i]
            return result
        return func
    return dec

def assign_clause (assignment: Assignment, clause: Clause) -> Clause | None : 
    for (asm, _) in assignment : 
        if asm in clause: return None
        if -asm in clause: clause = clause.difference([-asm])
    return clause

def assign_formula (assignment: Assignment, formula: Formula) -> Formula :
    new_formula = {}
    for index, clause in formula.items():
        new_clause = assign_clause(assignment, clause)
        if new_clause is not None:
            new_formula[index] = new_clause
    return new_formula

def get_contradicts (formula) -> list[int] :
    return [i for i, c in formula.items() if c == set()]

def get_units (formula) -> list[int] :
    return [i for i, c in formula.items() if len(c) == 1]

def pure_propagate (assignment: Assignment, formula: Formula) :
    counter = count_occurrence(formula)

    stable = False
    while stable == False: 
        stable = True
        for lit in counter.keys(): 
            if -lit not in counter.keys(): 
                assignment.append((lit, -2))
                formula = assign_formula([(lit, -2)], formula)
                counter = count_occurrence(formula)
                stable = False

    return assignment, formula

def unit_propagate (assignment: Assignment, formula: Formula) :
    ensure (formula == assign_formula(assignment, formula), "unit propagation only receive applied formula")

    stack = get_units(formula)
    while len(stack) : 
        ind = stack.pop()
        if ind in formula:
            if len(formula[ind]) == 0: continue
            lit = list(formula[ind])[0]
            assignment.append((lit, ind))
            formula = assign_formula([(lit, ind)], formula)
            # RETURNING ON CONTRACICT HERE NAKES LEARNING WORSE
            stack = get_units(formula)

    return assignment, formula

def backtrack (assignment: Assignment, clause: Clause) -> Assignment : 
    # TODO: a constant backtrack can be done. 
    l = 0 
    r = len(assignment)-1
    while (l < r) : 
        mid = (l+r+1)//2
        if assign_clause(assignment[:mid], clause) == set() :
            r = mid-1
        else : 
            l = mid
    return assignment[:l]

# CAN WE RETURN NONE HERE?
def resolution (c1: Clause, c2: Clause, lit: Literal) -> Clause : 
    ensure (c1 != None and c2 != None, "resolution cannot take on empty clause")
    ensure ((lit in c1 and -lit in c2) or (-lit in c1 and lit in c2),                   # type: ignore 
            "given literal is not a resoluble literal")

    return c1.union(c2) - set([lit, -lit])                                              # type: ignore

def learn (assignment: Assignment, conflictid: int, unapplied_formula: Formula) -> Clause : 
    conflict = unapplied_formula[conflictid]
    ensure (conflict != None, "learning a formula without conflict") 
    for (asm, ind) in reversed(assignment) :
        if ind == -1 : continue
        if ind == -2 : continue
        if asm not in conflict and -asm not in conflict : continue           # type: ignore
        conflict = resolution (conflict, unapplied_formula[ind], asm)
    return conflict

def count_occurrence (formula) : 
    count = {}
    for clause in formula.values() : 
        for lit in clause : 
            if lit not in count: 
                count[lit] = 0
            count[lit] += 1
    return count

def decision (formula) -> Literal : 
    for clause in formula.values() : 
        if clause != None : 
            return list(clause)[0]
    raise Exception("formula is satisfied but reach decision")
    # RANDOM IS DEFINITELY NOT A GOOD HEURISTIC

def solve (formula: Formula) -> Assignment | None :
    unapplied_formula = formula

    assignment = []

    while True:
        # if len(assignment) != 0: DEBUG("top assign: ", assignment[-1])
        DEBUG("current asm: ", len(assignment), "formula remain: ", len(formula), "total: ", len(unapplied_formula))
        # DEBUG(assignment)
        
        assignment, formula = unit_propagate(assignment, formula)
        assignment, formula = pure_propagate(assignment, formula)

        if formula == {} : 
            DEBUG("found assignment", assignment)
            DEBUG("result formula length: ", len(unapplied_formula))
            return assignment 

        has_learned = False
        contradicts = get_contradicts(formula)
        while len(contradicts) != 0 and contradicts[0] != None: 
            # DEBUG("assignment: ", assignment)
            learned_clause = learn(assignment, contradicts[0], unapplied_formula)
            if learned_clause == set() : 
                DEBUG("unsat")
                DEBUG("result formula length: ", len(unapplied_formula))
                return None
            length = len(unapplied_formula) 
            unapplied_formula[length] = learned_clause
            assignment = backtrack(assignment, learned_clause)
            formula = assign_formula(assignment, unapplied_formula)
            contradicts = get_contradicts(formula)
            has_learned = True
            # DEBUG("LEARN", learned_clause)
            
        if not has_learned: 
            lit = decision(formula)
            ensure (lit not in map_first(assignment), "decision cannot be assigned variable")
            assignment.append((lit, -1))
            # DEBUG("guessing", lit)
            formula = assign_formula([(lit, -1)], formula)

