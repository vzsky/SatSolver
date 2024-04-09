import os
import parser 
import dpll 
import sys
from utils import *

if __name__ == "__main__" :

    os.environ["ENV"] = "TIME" # "DEBUG"

    if len(sys.argv) != 2: 
        print("expected ONE argument")
        exit(0)

    filename = sys.argv[1]
    formula = parser.parse(filename)

    result = dpll.solve(formula)

    print(result)
