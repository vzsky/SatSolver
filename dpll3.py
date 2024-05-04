from utils import *

unapplied_formula = {}
formula = {}
clause_length = {}
assignment = []
watch = {}
variable_count = 0

def copy_clause (clause): 
    return set(clause)

def copy_formula (formula) :
    return { i: copy_clause(c) for i, c in formula.items() }

def make_clause_length () :
    global clause_length, formula

    for i, c in formula.items():
        clause_length[i] = len(c)

def get_variable_count (formula):
    m = 0
    for index, clause in formula.items(): 
        for elem in clause:
            m = max(m, abs(elem))
    return m

def select2 (s): 
    if len(s) >= 2: 
        a, b, *_ = s
        return set([a, b])
    if len(s) == 1: 
        a, *_ = s
        return set([a])
    return set()

def make_2wl (): 
    global formula, watch

    for i, c in formula.items(): 
        watch[i] = select2(c)

def assign_clause (assignment: Assignment, clause: Clause) -> Clause | None : 
    for (asm, _) in assignment : 
        # print("check ass cls: ", asm, clause)
        if asm in clause: return None
        if -asm in clause: clause = clause.difference([-asm])
    return clause

def get_2wl (index):
    # global assignment
    # new_clause = assign_clause(assignment, formula[index])
    # if new_clause is None: 
    #     del formula[index]
    #     return None
    # else: 
    #     formula[index] = new_clause
    #     return select2(new_clause)

    # BELOW IS LAZY
    global assignment
    ma = map_first(assignment)
    clause = formula[index] # Here, assume that formula[index] exists

    wl = []
    # for elem in clause:
    while clause_length[index] != 0:
        elem = clause.pop()
        clause_length[index] -= 1
        if elem in ma: 
            # print("del clause", index)
            del formula[index]
            del clause_length[index]

            return None
        if -elem in ma: continue
        wl.append(elem)
        if len(wl) == 2: 
            break

    for w in wl:
        clause.add(w)
        clause_length[index] += 1
    formula[index] = clause
    return set(wl)

def assign_formula (asm: Assignment) :
    global formula, watch, assignment

    ma = map_first(asm)

    for index, clause in watch.items():
        status = False
        # print("@", index, "is watching", clause)
        # print("current assigntment", assignment)
        # print("current clause", formula[index])
        # print("current raw", unapplied_formula[index])
        for lit in clause :
            if lit in ma: 
                # print(lit, "in ma")
                watch[index] = None
                # print("formula", formula[index])
                # print("clause", clause_length[index])
                # print("del c", index)
                del clause_length[index]
                del formula[index]
                status = False
                break
            if -lit in ma: 
                # print(lit, "(neg) in ma")
                status = True

        if status:
            watch[index] = get_2wl(index)

            # print(assignment)
            # new_clause = assign_clause(assignment, unapplied_formula[index])

    watch = {index:clause for index, clause in watch.items() if clause is not None}

def get_contradicts () -> list[int] :
    global formula
    return [i for i, c in watch.items() if clause_length[i] == 0]

def get_units () -> list[int] :
    global formula, watch
    return [i for i, c in watch.items() if clause_length[i] == 1]

def unit_propagate () :
    global formula, assignment
    # ensure (formula == assign_formula(assignment, formula), "unit propagation only receive applied formula")
    stack = get_units()
    while len(stack) : 
        ind = stack.pop()
        if ind in formula:
            if clause_length[ind] == 0: continue
            lit = list(formula[ind])[0]
            # DEBUG("unit propagation", lit)
            assignment.append((lit, ind))
            assign_formula([(lit, ind)])
            # DEBUG("formula", formula)
            # DEBUG("watch", watch)
            # RETURNING ON CONTRADICT HERE NAKES LEARNING WORSE
            stack = get_units()

def backtrack (clause: Clause) : 
    global assignment
    # TODO: a constant backtrack can be done. 
    l = 0 
    r = len(assignment)-1
    while (l < r) : 
        mid = (l+r+1)//2
        if assign_clause(assignment[:mid], clause) == set() :
            r = mid-1
        else : 
            l = mid
    assignment = assignment[:l]

# CAN WE RETURN NONE HERE?
def resolution (c1: Clause, c2: Clause, lit: Literal) -> Clause : 
    # ensure (c1 != None and c2 != None, "resolution cannot take on empty clause")
    # ensure ((lit in c1 and -lit in c2) or (-lit in c1 and lit in c2),                   # type: ignore 
            # "given literal is not a resoluble literal")

    return c1.union(c2) - set([lit, -lit])                                              # type: ignore

def learn (conflictid: int) -> Clause : 
    global unapplied_formula, assignment

    conflict = unapplied_formula[conflictid]
    ensure (conflict != None, "learning a formula without conflict") 
    for (asm, ind) in reversed(assignment) :
        if ind == -1 : continue
        if ind == -2 : continue
        if asm not in conflict and -asm not in conflict : continue           # type: ignore
        conflict = resolution (conflict, unapplied_formula[ind], asm)   
    # DEBUG("learn", conflict)
    return conflict

def decision () -> Literal : 
    global formula, assignment

    chosen = map_first(assignment)

    for index, clause in formula.items() : 
        e = clause.pop()
        if e in chosen: 
            del formula[index]
            # print("del c", index)
            del clause_length[index]
            del watch[index]
        while -e in chosen: 
            e = clause.pop()
        clause.add(e)
        formula[index] = clause
        clause_length[index] = len(clause)
        return e

    raise Exception("cannot make decision")

def solve (f: Formula) -> Assignment | None :
    global unapplied_formula, formula, assignment, variable_count

    variable_count = get_variable_count(f)
    
    unapplied_formula = f 
    formula = copy_formula(f)
    make_2wl()
    make_clause_length()

    assignment = []

    while True:
        # if len(assignment) != 0: DEBUG("top assign: ", assignment[-1])
        # DEBUG("current asm: ", len(assignment), "formula remain: ", len(formula), "total: ", len(unapplied_formula))
        # DEBUG(assignment)
        # DEBUG(formula)
        
        unit_propagate()
        # pure_propagate()

        if formula == {} : 
            # DEBUG("found assignment", assignment)
            # DEBUG("result formula length: ", len(unapplied_formula))
            return assignment 

        has_learned = False
        contradicts = get_contradicts()
        while len(contradicts) != 0 and contradicts[0] != None: 
            # DEBUG("assignment: ", assignment)
            learned_clause = learn(contradicts[0])
            if learned_clause == set() : 
                # DEBUG("unsat")
                # DEBUG("result formula length: ", len(unapplied_formula))
                return None
            length = len(unapplied_formula) 
            unapplied_formula[length] = learned_clause
            backtrack(learned_clause)
            formula = copy_formula(unapplied_formula)
            make_2wl()
            make_clause_length()
            assign_formula(assignment)
            contradicts = get_contradicts()
            has_learned = True
            # DEBUG("LEARN", learned_clause)
            
        if not has_learned: 
            lit = decision()
            # ensure (lit not in map_first(assignment), "decision cannot be assigned variable")
            # ensure (-lit not in map_first(assignment), "decision cannot be assigned variable")
            assignment.append((lit, -1))
            assign_formula([(lit, -1)])
            # DEBUG("guessing", lit)
            # DEBUG("watch", watch)
