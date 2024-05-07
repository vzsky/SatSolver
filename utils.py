import os 

Literal = int
Clause = set[Literal]
Assignment = list[tuple[Literal, int]]
Formula = dict[int, Clause]

def copy_formula (formula: Formula) -> Formula :
    return { i: set(c) for i, c in formula.items() }

def select2 (s: Clause) -> Clause:
    if len(s) >= 2: 
        a, b, *_ = s
        return set([a, b])
    if len(s) == 1: 
        a, *_ = s
        return set([a])
    return set()

#######################################################################
###                             DEBUG                               ###
#######################################################################

def ensure (cond, msg) :
    if os.environ["ENV"] != "DEBUG" : return
    if not cond : 
        raise Exception(msg)

def ensureF (cond, msg) :
    ensure (not cond, msg)

def map_first (ls) : 
    return [x[0] for x in ls]

def DEBUG (*args): 
    if os.environ["ENV"] == "DEBUG" : 
        print(*args)
