import os 

Literal = int
Clause = set[Literal]
Assignment = list[tuple[Literal, int]]
Formula = dict[int, Clause]
var = abs
sgn = lambda x:  int(x/abs(x))

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
