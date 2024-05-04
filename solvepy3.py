import os
import parser 
import dpll
import dpll2
import dpll3
import sys
import random
from utils import *

if __name__ == "__main__" :

    random.seed(42)
    os.environ["ENV"] = "RUN" 
    # os.environ["ENV"] = "DEBUG" 

    if len(sys.argv) != 2: 
        print("expected ONE argument")
        exit(0)

    filename = sys.argv[1]
    formula = parser.parse(filename)

    result = dpll3.solve(formula)


    print("FOUND")
    print(result)
    
    # if result :
    #     formula = dpll.assign_formula(result, formula)
    #     assert formula == {}
    #     print("solution checked")

