import random
from utils import *

def assign_clause (assignment: Assignment, clause: Clause) -> Clause | None : 
    if clause == None: return None
    rem = set()
    for (asm, _) in assignment : 
        for lit in clause: 
            if asm == lit: return None
            if var(asm) == var(lit): 
                rem.add(lit)
                break
    return clause - rem

def assign_formula (assignment: Assignment, formula: Formula) -> tuple[Formula, list[int], list[int]] :
    f = { ind : assign_clause(assignment, clause) for ind, clause in formula.items() }
    formula = { i:c for i, c in f.items() if c != None }
    contradicts = [i for i, c in formula.items() if c == set()]
    units = [i for i, c in formula.items() if len(c) == 1]
    return formula, contradicts, units

def unit_propagate (assignment: Assignment, formula: Formula, units: list[int]) -> tuple[Assignment, list[int], Formula] :
    ensure (formula == assign_formula(assignment, formula)[0], "unit propagation only receive applied formula")

    contradicts = []
    stack = units
    while len(stack) : 
        ind = stack.pop()
        if ind in formula:
            lit = list(formula[ind])[0]
            assignment.append((lit, ind))
            formula, contradicts, units = assign_formula([(lit, ind)], formula)
            if len(contradicts) != 0: 
                return assignment, contradicts, formula
            stack += units

    return assignment, contradicts, formula

def backtrack (assignment: Assignment, clause: Clause) -> Assignment : 
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
    count = count_occurrence(formula)
    result = random.choices(list(count.keys()), list(count.values())) 
    return result[0]

def solve (formula: Formula) -> Assignment | None :
    unapplied_formula = formula

    assignment = []
    contradicts = []
    units = []

    while True:
        # if len(assignment) != 0: DEBUG("top assign: ", assignment[-1])
        # DEBUG("current: ", len(assignment), "formula remain: ", len(formula), "total: ", len(unapplied_formula))

        assignment, contradicts, formula = unit_propagate(assignment, formula, units)

        if formula == {} : 
            DEBUG("found assignment", assignment)
            DEBUG("result formula length: ", len(unapplied_formula))
            return assignment 

        has_learned = False
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
            formula, contradicts, units = assign_formula(assignment, unapplied_formula)
            has_learned = True
            # DEBUG("LEARN", learned_clause)
            
        if not has_learned: 
            lit = decision(formula)
            ensure (lit not in map_first(assignment), "decision cannot be assigned variable")
            assignment.append((lit, -1))
            # DEBUG("guessing", lit)
            formula, contradicts, units = assign_formula([(lit, -1)], formula)

