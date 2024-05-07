from utils import *

unapplied_formula = {}
formula = {}
clause_length = {}
assignment = []
assignment_lit = []
watch = {}
variable_count = 0
conflict_count = 0
original_formula_length = 0
conflict_activity = {}

seed = 314159

forget_interval = 61

def make_clause_length () :
    global clause_length

    for i, c in formula.items():
        clause_length[i] = len(c)

def make_2wl (): 
    global watch

    for i, c in formula.items(): 
        watch[i] = select2(c)

def make_variable_count ():
    global variable_count

    variable_count = 0
    for clause in formula.values(): 
        for elem in clause:
            variable_count = max(variable_count, abs(elem))

def regularize (): 
    make_clause_length()
    make_2wl()

def init (f): 
    global unapplied_formula, formula, clause_length, assignment, assignment_lit 
    global watch, variable_count, conflict_count, original_formula_length
    unapplied_formula = f
    formula = copy_formula(f)
    assignment = []
    assignment_lit = []
    conflict_count = 0 
    original_formula_length = max(formula.keys()) + 1
    make_variable_count()
    regularize()

def add_assignment (lit, message=-1): 
    global assignment, assignment_lit
    assignment.append((lit, message))
    assignment_lit.append(lit)

def rollback_assignment (index):
    global assignment, assignment_lit
    assignment = assignment[:index]
    assignment_lit = assignment_lit[:index]

def next_formula_index (): 
    return original_formula_length + conflict_count

def count_var_occurrence ():
    count = {}
    for clause in formula.values() : 
        for lit in clause :
            var = abs(lit)
            if var not in count: count[var] = 0
            count[var] += 1
    return count

def count_lit_occurrence ():
    count = {}
    for clause in formula.values() : 
        for lit in clause :
            if lit not in count: count[lit] = 0
            count[lit] += 1
    return count

def on_learn_path (ind) :
    global conflict_activity
    if ind < original_formula_length: return 
    if ind not in conflict_activity.keys() :
        conflict_activity[ind] = 0
    conflict_activity[ind] += 1
    if conflict_count % forget_interval == 0: 
        for ind in conflict_activity.keys(): 
            conflict_activity[ind] /= 2
