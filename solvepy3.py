import os
import parser 
import dpll
import sys
import random
from utils import *

if __name__ == "__main__" :

    random.seed(42)
    os.environ["ENV"] = "DEBU" # "DEBUG"

    if len(sys.argv) != 2: 
        print("expected ONE argument")
        exit(0)

    filename = sys.argv[1]
    formula = parser.parse(filename)

    result = dpll.solve(formula)


    print("FOUND")
    print(result)
    
    # if result :
    #     formula = dpll.assign_formula(result, formula)
    #     assert formula == {}
    #     print("solution checked")

