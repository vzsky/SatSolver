import os
import parser 
import dpll 
import sys
import random
from utils import *

if __name__ == "__main__" :

    random.seed(42)
    os.environ["ENV"] = "DEBUG" # "DEBUG"

    if len(sys.argv) != 2: 
        print("expected ONE argument")
        exit(0)

    filename = sys.argv[1]
    formula = parser.parse(filename)

    assignment, _, units = dpll.assign_formula([], formula)
    assignment, contradicts, formula = dpll.unit_propagate([], formula, units)

    result = dpll.solve(formula)

    print("FOUND")
    print(result)
    
    if result :
        formula = dpll.assign_formula(result, formula)[0]
        assert formula == {}
        print("solution checked")

