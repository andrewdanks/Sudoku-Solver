from cspbase import *
import itertools
import sys
from collections import deque

SQUARE_SIZE = 9

def permutations(L):
  '''Return a list of all permutations of list L.'''
  return list(itertools.permutations(L))

def intersection(L1, L2):
  '''Return the list representing the intersection of lists L1 and L2.'''
  ret = set(L1).intersection(set(L2))
  return list(ret)

def get_box_number(row, col):
  '''Return what box (row,col) is in. Boxes numbers 0 to 8 from left to right, top to bottom'''
  quadrants = {0:range(3),1:range(3,6),2:range(6,9)}
  for (i,q) in quadrants.items():
    if row in q: row_quadrant = i
  for (i,q) in quadrants.items():
    if col in q: col_quadrant = i
  return 3*row_quadrant + col_quadrant

def get_cell_values_for_box(box, board):
  '''Return a list of the cells that are in the given box (an int from 0-8). Each cell in the list
  is a dictionary of the form {'row':int, 'col':int}'''
  cells = []
  for row in range(9):
    for col in range(9):
      if get_box_number(row,col) == box:
        cells.append(board[row][col])
  return cells

def get_cells_for_box(box):
  '''Return a list of the cells that are in the given box (an int from 0-8). Each cell in the list
  is a dictionary of the form {'row':int, 'col':int}'''
  cells = []
  for row in range(9):
    for col in range(9):
      if get_box_number(row,col) == box:
        cells.append({'row':row,'col':col})
  return cells


def fill_list(L, fill_list):
  '''Given list L, fill each 0 in the list with the elements from fill_list.'''
  new_L = L[:]
  j = 0
  for i in range(len(L)):
    if L[i] == 0:
      new_L[i] = fill_list[j]
      j += 1
  return new_L

def cell_id(row,col):
  return str(row)+str(col)


def write_board_variables(variables):
  '''Put the variables of the board in a readable format.'''

  human_board = []
  for row in range(SQUARE_SIZE):
    human_board.append([])
    for col in range(SQUARE_SIZE):
      V = variables[row][col]
      domain = V.cur_domain()
      domain.sort()
      human_board[row].append(domain)
  return human_board


def enforce_gac(constraint_list):
  '''Input a list of constraint objects, each representing a constraint, then 
     enforce GAC on them pruning values from the variables in the scope of
     these constraints. Return False if a DWO is detectd. Otherwise, return True. 
     The pruned values will be reflected in the variable object cur_domain (i.e.,
     enforce_gac will modify the variable objects that are in the scope of
     the constraints passed to it.'''
  GACQueue = deque(constraint_list)
  while GACQueue:
    C = GACQueue.popleft()
    for V in C.scope:
      for d in V.cur_domain():
        if not C.has_support(V, d):
          #print 'pruned', d, 'from', V.name
          V.prune_value(d)
          if V.domain_size() < 1:
            return False
          else:
            # Push all constraints C' such that V is in scope of C' and C'
            # is not in GACQueue
            for C2 in constraint_list:
              if C2 not in GACQueue and V in C2.scope:
                GACQueue.append(C2)
  return True

def initialize_variables(board):

  # Create a variable for each cell of the board:
  variables = {}  #indexed by row then col
  variables_by_col = {} # indexed by col then row
  variables_by_box = {} # indexed by box
  for row in range(SQUARE_SIZE):
    variables[row] = {}
    for col in range(SQUARE_SIZE):
      d = board[row][col]
      domain = range(1,10) if d == 0 else [d]
      V = Variable('('+str(row)+','+str(col)+')', domain)
      variables[row][col] = V

      box = get_box_number(row, col)

      if box not in variables_by_box:
        variables_by_box[box] = []
      variables_by_box[box].append(V)

      if col not in variables_by_col:
        variables_by_col[col] = {}
      variables_by_col[col][row] = V

  return variables, variables_by_col, variables_by_box


def sudoku_enforce_gac_model_1(board):
  SQUARE_SIZE = len(board)

  variables, variables_by_col, variables_by_box = initialize_variables(board)
  constraint_list = []

  compared = {}

  # Create all binary not-equal constraints for values in the same row:
  for row in range(SQUARE_SIZE):
    for col1 in range(SQUARE_SIZE):
      CELL1_ID = cell_id(row,col1)
      if CELL1_ID not in compared: compared[CELL1_ID] = []

      for col2 in range(SQUARE_SIZE):

        CELL2_ID = cell_id(row,col2)
        if (CELL1_ID == CELL2_ID) or (CELL2_ID in compared and CELL1_ID in compared[CELL2_ID]) or CELL2_ID in compared[CELL1_ID]:
          continue
        compared[CELL1_ID].append(CELL2_ID)
        
        V1, V2 = variables[row][col1], variables[row][col2]
        scope = [V1, V2]
        C = Constraint('NOT-EQUAL-ROW:'+V1.name+';'+V2.name, scope)

        sat_tuples = []

        for d1 in V1.cur_domain():
          for d2 in V2.cur_domain():
            if d1 != d2:
              t1, t2 = [d1, d2], [d2, d1]
              if C.tuple_is_valid(t1):
                sat_tuples.append(t1)
              if C.tuple_is_valid(t2):
                sat_tuples.append(t2)

        C.add_satisfying_tuples(sat_tuples)
        constraint_list.append(C)


  # Create all binary not-equal constraints for values in the same col:
  for col in range(SQUARE_SIZE):
    for row1 in range(SQUARE_SIZE):
      CELL1_ID = cell_id(row1,col)
      if CELL1_ID not in compared: compared[CELL1_ID] = []

      for row2 in range(SQUARE_SIZE):

        CELL2_ID = cell_id(row2,col)
        if (CELL1_ID == CELL2_ID) or (CELL2_ID in compared and CELL1_ID in compared[CELL2_ID]) or CELL2_ID in compared[CELL1_ID]:
          continue
        compared[CELL1_ID].append(CELL2_ID)
        
        V1, V2 = variables_by_col[col][row1], variables_by_col[col][row2]
        scope = [V1, V2]
        C = Constraint('NOT-EQUAL-COL:'+V1.name+';'+V2.name, scope)

        sat_tuples = []

        for d1 in V1.cur_domain():
          for d2 in V2.cur_domain():
            if d1 != d2:
              t1, t2 = [d1, d2], [d2, d1]
              if C.tuple_is_valid(t1):
                sat_tuples.append(t1)
              if C.tuple_is_valid(t2):
                sat_tuples.append(t2)

        C.add_satisfying_tuples(sat_tuples)
        constraint_list.append(C)


  # Create all binary not-equal constraints for values in the same box:
  for box in range(SQUARE_SIZE):
    cells = get_cells_for_box(box)
    for cell1 in cells:
      row1, col1 = cell1['row'], cell1['col']
      CELL1_ID = cell_id(row1,col1)
      if CELL1_ID not in compared: compared[CELL1_ID] = []

      for cell2 in cells:
        row2, col2 = cell2['row'], cell2['col']
        CELL2_ID = cell_id(row2,col2)

        if (CELL1_ID == CELL2_ID) or (CELL2_ID in compared and CELL1_ID in compared[CELL2_ID]) or CELL2_ID in compared[CELL1_ID]:
          continue
        compared[CELL1_ID].append(CELL2_ID)

        
        V1, V2 = variables[row1][col1], variables[row2][col2]
        scope = [V1, V2]
        C = Constraint('NOT-EQUAL-BOX:'+V1.name+';'+V2.name, scope)

        sat_tuples = []

        for d1 in V1.cur_domain():
          for d2 in V2.cur_domain():
            if d1 != d2:
              t1, t2 = [d1, d2], [d2, d1]
              if C.tuple_is_valid(t1):
                sat_tuples.append(t1)
              if C.tuple_is_valid(t2):
                sat_tuples.append(t2)

        C.add_satisfying_tuples(sat_tuples)
        constraint_list.append(C)


  enforce_gac(constraint_list)

  new_board = write_board_variables(variables)
  for row in new_board:
    print row


def model1_create_constraint(name, variables, relevant_board, cells, compared):
  for cell1 in cells:

    row1, col1 = cell1['row'], cell1['col']
    CELL1_ID = cell_id(row1,col1)

    if CELL1_ID not in compared:
      compared[CELL1_ID] = []

    for cell2 in cells:

      row2, col2 = cell2['row'], cell2['col']
      CELL2_ID = cell_id(row2,col2)

      if (CELL1_ID == CELL2_ID) or (CELL2_ID in compared and CELL1_ID in compared[CELL2_ID]) or CELL2_ID in compared[CELL1_ID]:
          continue

      compared[CELL1_ID].append(CELL2_ID)

      V1, V2 = variables[row1][col1], variables[row2][col2]
      scope = [V1, V2]

      C = Constraint(name, scope)

      sat_tuples = []

      for d1 in V1.cur_domain():
        for d2 in V2.cur_domain():
          if d1 != d2:
            t1, t2 = [d1, d2], [d2, d1]
            if C.tuple_is_valid(t1):
              sat_tuples.append(t1)
            if C.tuple_is_valid(t2):
              sat_tuples.append(t2)

      C.add_satisfying_tuples(sat_tuples)
      constraint_list.append(C)

      return C

def sudoku_enforce_gac_model_2(board):
  SQUARE_SIZE = len(board)

  board_by_col = []
  for col in range(SQUARE_SIZE):
    board_by_col.append([])
    for row in range (SQUARE_SIZE):
      board_by_col[col].append([])
    for row in range(SQUARE_SIZE):
      board_by_col[col][row] = board[row][col]


  variables, variables_by_col, variables_by_box = initialize_variables(board)
  constraint_list = []

  # Create ALL-DIFF constraints for each row:
  for row in range(SQUARE_SIZE):
    C = model2_create_constrant('ALL-DIFF-ROW-'+str(row), variables, board[row], row)
    constraint_list.append(C)

  # Create ALL-DIFF constraints for each col:
  for col in range(SQUARE_SIZE):
    C = model2_create_constrant('ALL-DIFF-COL-'+str(col), variables_by_col, board_by_col[col], col)
    constraint_list.append(C)


  # Create ALL-DIFF constraints for each col:
  for box in range(SQUARE_SIZE):
    relevant_board = get_cell_values_for_box(box, board)
    C = model2_create_constrant('ALL-DIFF-BOX-'+str(box), variables_by_box, relevant_board, box)
    constraint_list.append(C)


  enforce_gac(constraint_list)


  new_board = write_board_variables(variables)
  for row in new_board:
    print row


def model2_create_constrant(name, variables, relevant_board, i):
  scope = []
  for j in range(SQUARE_SIZE):
    scope.append(variables[i][j])
  C = Constraint(name, scope)
  sat_tuples = []
  free_values = []
  for d in range(1,10):
    if d not in relevant_board:
      free_values.append(d)
  free_values_comb = permutations(free_values)
  for f in free_values_comb:
    t = fill_list(relevant_board, f)
    if C.tuple_is_valid(t):
      sat_tuples.append(t)
  C.add_satisfying_tuples(sat_tuples)
  
  return C


