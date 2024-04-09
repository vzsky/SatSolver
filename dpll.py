from abc import update_abstractmethods
from copy import deepcopy

# Typing and Aliasing
Literal = int
Clause = set[Literal] | None
Assignment = list[tuple[Literal, int]]
Formula = list[Clause]
var = abs
sgn = lambda x:  int(x/abs(x))


def assign_clause (assignment: Assignment, clause: Clause) -> Clause : 
    if clause == None: return None
    result = deepcopy(clause)
    for lit in clause: 
        for (asm, _) in assignment : 
            if asm == lit: return None
            if var(asm) == var(lit): 
                result.remove(lit) 
                break
    return result

def assign_formula (assignment: Assignment, formula: Formula) -> Formula :
    return [ assign_clause(assignment, clause) for clause in formula ]

def unit_propagate (assignment: Assignment, formula: Formula) -> tuple[Assignment, Formula] :
    for ind, clause in enumerate(formula): 
        if clause != None and len(clause) == 1:
            lit = list(clause)[0]
            assignment.append((lit, ind))
            assigned_formula = assign_formula(assignment, formula)
            return unit_propagate (assignment, assigned_formula)
    return assignment, formula

def backtrack (assignment: Assignment, clause: Clause) -> Assignment : 
    while (assign_clause(assignment, clause) == set()) : 
        assignment.pop()
    return assignment

def resolution (c1: Clause, c2: Clause, lit: Literal) -> Clause : 
    if c1 == None or c2 == None : 
        raise Exception ("resolution cannot take on empty clause")
    if (lit not in c1 or -lit not in c2) and (-lit not in c1 or lit not in c2): 
        raise Exception ("given literal is not a resoluble literal")

    return c1.union(c2) - set([lit, -lit])

def learn (assignment: Assignment, conflictid: int, unapplied_formula: Formula) -> Clause : 
    conflict = unapplied_formula[conflictid]
    if conflict == None: 
        raise Exception("learning a formula without conflict")
    for (asm, ind) in reversed(assignment) :
        if ind == -1 : continue
        if asm not in conflict and -asm not in conflict : continue           # type: ignore
        conflict = resolution (conflict, unapplied_formula[ind], asm)
    return conflict

def decision (formula) -> Literal : 
    # for now, any will do 
    for clause in formula : 
        if clause != None : 
            return list(clause)[0]
    raise Exception("formula is satisfied but reach decision")

def dpll (formula: Formula) -> Assignment | None :
    unapplied_formula = formula

    assignment = []
    while True: 
        assignment, formula = unit_propagate(assignment, formula)
        if all(c == None for c in formula) : 
            return assignment 

        if any(c == set() for c in formula) :
            conflictid = None 
            for ind, c in enumerate(formula) : 
                if c == set(): 
                    conflictid = ind
                    break 
            assert conflictid != None

            learned_clause = learn(assignment, conflictid, unapplied_formula)
            if learned_clause == set() : return None
            formula = unapplied_formula + [learned_clause]
            assignment = backtrack(assignment, learned_clause)
            continue
        lit = decision(formula)
        assignment.append((lit, -1))


