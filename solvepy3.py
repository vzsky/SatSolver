import parser 
import dpll
import sys
import random
from utils import *
import state

def serious_assign_formula (assignment, formula: Formula) :
    new_formula = {}

    for index, clause in formula.items():
        new_formula[index] = dpll.assign_clause(assignment, clause)

    formula = {index:clause for index, clause in new_formula.items() if clause is not None }
    return formula

def unit_propagate (formula) :
    preassign = []
    units = (list(c)[0] for c in formula.values() if len(c) == 1)
    for lit in units:
        preassign.append(lit)
        formula = {i:dpll.assign_clause([lit], c) for i, c in formula.items()}
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
            formula = serious_assign_formula([lit], formula)
            count = count_occurrence(formula)
            stable = False
    return formula, preassign

if __name__ == "__main__" :

    random.seed(state.seed)

    if len(sys.argv) != 2: 
        print("expected ONE argument")
        exit(0)

    filename = sys.argv[1]
    formula = parser.parse(filename)
    original_formula = copy_formula(formula)

    formula, preassign_unit = unit_propagate(formula)
    formula, preassign_pure = pure_propagate(formula)

    result = dpll.solve(formula)

    if result :
        result = result + preassign_unit + preassign_pure
        # assert serious_assign_formula(result, original_formula) == {}
        # print("solution checked")
        print ("s SATISFIABLE")
        answer = " ".join([str(lit) for lit in result])
        print("v " + answer + " 0")
    else :
        print("s UNSATISFIABLE")

