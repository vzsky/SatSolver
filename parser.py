import os
from utils import *

def parse (filename) : 

    def parse_clause (string: str) -> Clause:
        return set(int(x) for x in string.strip().split()[:-1])

    with open(filename) as f: 

        try : 
            line = f.readline()
            while line.strip().split()[0] == 'c':
                line = f.readline()


            [nvar, nclause] = [int(x) for x in line.strip().split()[2:]]

            if os.environ["ENV"] == "DEBUG":
                print("formula length: ", nclause)
                print("variables count: ", nvar)

        except : 
            raise Exception("cannot parse ill-syntax file")


        formula = []

        lines = f.readlines()
        for line in lines : 
            formula.append(parse_clause(line))

        if len(formula) != nclause : 
            raise Exception ("number of clause doesn't match")
        
        return dict(enumerate(formula))
    
def resolution (c1: Clause, c2: Clause, lit: Literal) -> Clause : 
    ensure (c1 != None and c2 != None, "resolution cannot take on empty clause")
    ensure ((lit in c1 and -lit in c2) or (-lit in c1 and lit in c2),                   # type: ignore 
            "given literal is not a resoluble literal")

    return c1.union(c2) - set([lit, -lit])                                              # type: ignore


