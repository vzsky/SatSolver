from utils import *

def parse (filename) : 

    def parse_clause (string: str) -> Clause:
        return set(int(x) for x in string.strip().split()[:-1])

    with open(filename) as f: 

        try : 
            line = f.readline()
            while line.strip().split()[0] == 'c':
                line = f.readline()


            [_, nclause] = [int(x) for x in line.strip().split()[2:]]

        except : 
            raise Exception("cannot parse ill-syntax file")


        formula = []

        lines = f.readlines()
        for line in lines : 
            formula.append(parse_clause(line))

        if len(formula) != nclause : 
            raise Exception ("number of clause doesn't match")
        
        return dict(enumerate(formula))
