import os
import parser 
import dpll
import dpll2
import dpll3
import sys
import random
from utils import *
import state
from copy import deepcopy

def assign_clause (assignment: list[Literal], clause: Clause) -> Clause | None : 
    for asm in assignment : 
        if asm in clause: return None
        if -asm in clause: clause = clause.difference([-asm])
    return clause

def assign_formula (assignment: list[Literal], formula: Formula) :
    new_formula = {}

    for index, clause in formula.items():
        new_formula[index] = assign_clause(assignment, clause)

    formula = {index:clause for index, clause in new_formula.items() if clause is not None }
    return formula

def unit_propagate (formula) :
    preassign = []
    units = (list(c)[0] for c in formula.values() if len(c) == 1)
    for lit in units:
        preassign.append(lit)
        formula = {i:assign_clause([lit], c) for i, c in formula.items()}
        formula = {i:c for i, c in formula.items() if c is not None}
    return formula, preassign 

def count_occurrence (formula) : 
    count = {}
    for clause in formula.values() : 
        for lit in clause : 
            if lit not in count: 
                count[lit] = 0
            count[lit] += 1
    return count

def pure_propagate (formula) :
    preassign = []
    count = count_occurrence(formula)
    stable = True
    while not stable:
        for lit in count.keys() : 
            if -lit in count.keys(): continue
            preassign.append(lit)
            formula = assign_formula([lit], formula)
            count = count_occurrence(formula)
            stable = False
    return formula, preassign

if __name__ == "__main__" :

    random.seed(state.seed)

    os.environ["ENV"] = "RUN" 
    os.environ["ENV"] = "DEBUG" 

    if len(sys.argv) != 2: 
        print("expected ONE argument")
        exit(0)

    filename = sys.argv[1]
    formula = parser.parse(filename)
    original_formula = deepcopy(formula)

    formula, preassign_unit = unit_propagate(formula)
    DEBUG("number of clause: ", len(formula))
    formula, preassign_pure = pure_propagate(formula)
    DEBUG("number of clause: ", len(formula))

    result = dpll3.solve(formula)
    print("FOUND")
    # print(result)

    if result :
        result = map_first(result) + preassign_unit + preassign_pure
        formula = assign_formula(result, original_formula)
        print("HERE", formula)
        assert formula == {}
        print("solution checked")

