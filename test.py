import dpll
from utils import *

def make_assignment (a: list[int]) :
    return [(x, int(-1)) for x in a]

def make_formula (a: list[list[int]|None]) -> Formula : 
    formula = dict(enumerate([None if x == None else set(x) for x in a]))
    return { i:c for i, c in formula.items() if c != None }

def test_assign_clause_1 () :
    A = make_assignment([1, 2, 3])
    C = set([1, 2, 3])
    result = dpll.assign_clause(A, C)
    assert result == None

def test_assign_clause_2 () :
    A = make_assignment([-3, 4, 5])
    C = set([1, 2, 3])
    result = dpll.assign_clause(A, C)
    assert result == set([1, 2])

def test_assign_clause_3 () :
    A = make_assignment([-3, -4, 5])
    C = set([1, 3, -4])
    result = dpll.assign_clause(A, C)
    assert result == None

def test_assign_formula_1 ():
    A = make_assignment([-3, -4, 5])
    F = make_formula([[1, 3, -4], [1, 2, 3], [3, 4, -5], [1, 3, -5]])
    result = dpll.assign_formula(A, F)
    assert result[0] == make_formula([None, [1, 2], [], [1]])

def test_assign_formula_2 ():
    A = make_assignment([1, 2, -3, -4])
    F = make_formula([[-1, 3, 4, 5], [5, 6], [3, 4, -5], [1, 3, -5]])
    result = dpll.assign_formula(A, F)
    assert result[0] == make_formula([[5], [5, 6], [-5], None])

def test_unit_prop_1 (): 
    A = make_assignment([])
    F = make_formula([[-1], [1, 2, 3], [1, -3]])
    result = dpll.unit_propagate(A, F, [0])
    rA = [(-1, 0), (-3, 2), (2, 1)]
    rF = dpll.assign_formula(rA, F)[0]
    assert (result[0], result[2]) == (rA, rF)

def test_unit_prop_2 (): 
    A = make_assignment([])
    F = make_formula([[-1], [1, 2, 3, 4], [1, -3], [-1, -3]])
    result = dpll.unit_propagate(A, F, [0])
    rA = [(-1, 0), (-3, 2)]
    rF = dpll.assign_formula(rA, F)[0]
    assert (result[0], result[2]) == (rA, rF)

def test_backtrack_1 ():
    A = make_assignment([1, 2, 3, 4, 5, 6])
    C = set([-1, -2, -3])
    assert dpll.assign_clause(A, C) == set()
    result = dpll.backtrack(A, C)
    assert result == make_assignment([1, 2])

def test_backtrack_2 ():
    A = make_assignment([1, -2, -3, 4, 5, 6])
    C = set([-1, 2, -5])
    assert dpll.assign_clause(A, C) == set()
    result = dpll.backtrack(A, C)
    assert result == A[:4]

def test_assign_formula_3 (): 
    """in class example`"""
    A = make_assignment([1, -2, -3, 4])
    F = make_formula([[-1, -4, 5], [-1, 6, -5], [-1, -6, 7], [-1, -7, -5], [1, 4, 6]])
    result = dpll.assign_formula(A, F)
    assert result == make_formula([[5], [6, -5], [-6, 7], [-7, -5], None])
    
def test_solve_1 ():
    F = make_formula([[-1, -4, 5], [-1, 6, -5], [-1, -6, 7], [-1, -7, -5], [1, 4, 6]])
    result = dpll.solve(F)
    assert result
    assert dpll.assign_formula(result, F)[0] == {}

if __name__ == "__main__" :
    os.environ["ENV"] = "DEBUG"

    test_assign_clause_1()
    test_assign_clause_2()
    test_assign_clause_3()
    test_assign_formula_1()
    test_assign_formula_2()
    test_unit_prop_1()
    test_unit_prop_2()
    test_backtrack_1()
    test_backtrack_2()

    DEBUG("solving 1: ")
    test_solve_1()
    DEBUG()

    print("all tests passed")
