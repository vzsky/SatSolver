from copy import deepcopy
from utils import *

def assign_clause (assignment: Assignment, clause: Clause) -> Clause : 
    if clause == None: return None
    rem = set()
    for (asm, _) in assignment : 
        for lit in clause: 
            if asm == lit: return None
            if var(asm) == var(lit): 
                rem.add(lit)
                break
    return clause - rem

def assign_formula (assignment: Assignment, formula: Formula) -> Formula :
    formula = { ind : assign_clause(assignment, clause) for ind, clause in formula.items() }
    formula = { i:c for i, c in formula.items() if c != None }
    return formula

def unit_propagate (assignment: Assignment, formula: Formula) -> tuple[Assignment, Formula] :
    ensure (formula == assign_formula(assignment, formula), "unit propagation only receive applied formula")
    status = True
    while status: 
        status = False
        for ind, clause in formula.items(): 
            if clause == None or len(clause) != 1: continue
            status = True
            lit = list(clause)[0]
            assignment.append((lit, ind))
            formula = assign_formula([(lit, ind)], formula)
            break 
    return assignment, formula

def backtrack (assignment: Assignment, clause: Clause) -> Assignment : 
    while (assign_clause(assignment, clause) == set()) : 
        assignment.pop()
    return assignment

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
        if asm not in conflict and -asm not in conflict : continue           # type: ignore
        conflict = resolution (conflict, unapplied_formula[ind], asm)
    return conflict

def decision (formula) -> Literal : 
    # for now, any will do 
    for clause in formula.values() : 
        if clause != None : 
            return list(clause)[0]
    raise Exception("formula is satisfied but reach decision")

def solve (formula: Formula) -> Assignment | None :
    unapplied_formula = formula

    assignment = []
    while True:

        if os.environ["ENV"] == "DEBUG" : 
            print("current: ", len(assignment), "formula remain: ", len(formula))

        assignment, formula = unit_propagate(assignment, formula)

        if formula == {} : 
            return assignment 

        conflictid = None 
        for ind, c in formula.items() : 
            if c == set(): 
                conflictid = ind
                break 

        if conflictid != None: 
            learned_clause = learn(assignment, conflictid, unapplied_formula)
            if learned_clause == set() : return None
            length = len(unapplied_formula) 
            unapplied_formula[length] = learned_clause
            formula = deepcopy(unapplied_formula)
            assignment = backtrack(assignment, learned_clause)
            formula = assign_formula(assignment, formula)
            continue

        lit = decision(formula)
        ensure (lit not in map_first(assignment), "decision cannot be assigned variable")
        assignment.append((lit, -1))
        formula = assign_formula([(lit, -1)], formula)

