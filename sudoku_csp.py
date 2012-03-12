from cspbase import *


def enforce_gac(constraint_list):
  '''Input a list of constraint objects, each representing a constraint, then 
     enforce GAC on them pruning values from the variables in the scope of
     these constraints. Return False if a DWO is detectd. Otherwise, return True. 
     The pruned values will be reflected in the variable object cur_domain (i.e.,
     enforce_gac will modify the variable objects that are in the scope of
     the constraints passed to it.'''

  GACQueue = constraint_list

  while not GACQueue.empty():

    C = GACQueue.pop(0)

    i = 0
    for V in C.scope:
      j = 0
      for d in V.cur_domain():

        # Find set of assignments A for all other variables in C.scope
        # such that C(A U V=d) is True
        #found_A = False

        #for V2 in C.scope:
        #  if V2 is V: continue

        #  t = []
        #  for x in V2:
        #    t.append(x)
        found_A = find_set_of_assignments(C, V, d, scope)

        variables = S.scope
        variables.remove(V)
        seen = [V]
        Q = [V]
        while not Q.empty():
          t = Q.pop(0)
          if 





        if not found_A:
          V.prune_value(d)
          if V.domain_size() < 1:
            return False
          else:
            # Push all constraints C' such that V is in scope of C' and C'
            # is not in GACQueue
            for C2 in constraint_list:
              if C2 not in GACQueue and V in C2.scope:
                GACQueue.append(C2)

        j += 1
      i += 1



  return True
                            
def sudoku_enforce_gac_model_1(initial_sudoku_board):
  '''The input board is specified as a list of 9 lists. Each of the
     9 lists represents a row of the board. If a 0 is in the list it
     represents an empty cell. Otherwise if a number between 1--9 is
     in the list then this represents a pre-set board position.

     In model_1 you should create a variable for each cell of the
     board, with domain equal to {1-9} if the board has a 0 at that
     position, and domain equal {i} if the board has a fixed number i
     at that cell. 
     
     Model_1 should create BINARY CONSTRAINTS OF NOT-EQUAL between all
     relevant variables (e.g., all pairs of variables in the same
     row), then invoke enforce_gac on those constraints. All of the
     constraints of Model_1 MUST BE binary constraints (i.e.,
     constraints whose scope includes two and only two variables).
     
     The ouput should have the same layout as the input: a list of
     nine lists each representing a row of the board. However, now the
     numbers in the positions of the input list are to be replaced by
     LISTS which are the corresponding cell's pruned domain (current
     domain) AFTER gac has been performed.
     
     For example, if GAC failed to prune any values the output from
     the above input would result in an output would be: NOTE I HAVE
     PADDED OUT ALL OF THE LISTS WITH BLANKS SO THAT THEY LINE UP IN
     TO COLUMNS. Python would not output this list of list in this
     format.
     
     [[[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[                2],[1,2,3,4,5,6,7,8,9],[                9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[                6],[1,2,3,4,5,6,7,8,9]],
     [[1,2,3,4,5,6,7,8,9],[                4],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[                1],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[                8]],
     [[1,2,3,4,5,6,7,8,9],[                7],[1,2,3,4,5,6,7,8,9],[                4],[                2],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[                3]],
     [[                5],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[                3],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9]],
     [[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[                1],[1,2,3,4,5,6,7,8,9],[                6],[1,2,3,4,5,6,7,8,9],[                5],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9]],
     [[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[                3],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[                6]],
     [[                1],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[                5],[                7],[1,2,3,4,5,6,7,8,9],[                4],[1,2,3,4,5,6,7,8,9]],
     [[                6],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[                9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[                2],[1,2,3,4,5,6,7,8,9]],
     [[1,2,3,4,5,6,7,8,9],[                2],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[                8],[1,2,3,4,5,6,7,8,9],[                1],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9]]]
     
     Of course, GAC would prune some variable domains so this would
     not be the outputted list.
     '''


'''
X Dom[X] = {1,2,3}
Y Dom[Y] = {3,4,5}
Z Dom[Z] = {4,6,8}
C(X,Y,Z) = True iff Z=X+Y
constraint: [ [1 3 4] [1 5 6] [2 4 6] [3 3 6] [3 5 8] ]
'''

    variables = {}
    for row in initial_sudoku_board:
      variables[row] = {}
      for col in row:
        val = initial_sudoku_board[row][col]
        domain = range(1,10) if val == 0 else [val]
        variables[row][col] = Variable(str(row)+','str(col), domain)

    sat_tuples = []
    constraints = []
    for row in variables:
      scope = []
      for col in row:

        V = variables[row][col]
        domain = V.domain()
        if len(domain) == 1:
          prune_val = domain[0]
          for r in variables:
            for c in r:
              if r == row and c == col: continue
              V2 = variables[r][c]
              V2.prune_value(prune_val)
        scope.append(V)
      C = Constraint('NOT-EQUAL-ROW-'+str(row), scope)
      constraints.append(c)

    # Generate satisfying tuples:


    for c in constraints: c.print_constraint()
    enforce_gac(constraints)
    for c in constraints: c.print_constraint()





##############################

def sudoku_enforce_gac_model_2(initial_sudoku_board):
  '''This function takes the same input format (a list of 9 lists
  specifying the board, and generates the same format output as
  sudoku_enforce_gac_model_1.
  
  The variables of model_2 are the same as for model_1: a variable
  for each cell of the board, with domain equal to {1-9} if the
  board has a 0 at that position, and domain equal {i} if the board
  has a fixed number i at that cell.

  However, model_2 has different constraints. In particular, instead
  of binary non-equals constaints model_2 has 27 all-different
  constraints: all-different constraints for the variables in each
  of the 9 rows, 9 columns, and 9 sub-squares. Each of these
  constraints is over 9-variables (some of these variables will have
  a single value in their domain). model_2 should create these
  all-different constraints between the relevant variables, then
  invoke enforce_gac on those constraints.
  '''

  variables = {}
  for row in initial_sudoku_board:
  variables[row] = {}
  for col in row:
    val = initial_sudoku_board[row][col]
    domain = [val] if val != 0 else range(1,10)
    v = Variable(str(row)+','str(col), domain)
    variables[row][col] = v
   
  C_BOX = Constraint('NOT-EQUAL-BOX')
  C_COL = Constraint('NOT-EQUAL-COL')
  C_ROW = Constraint('NOT-EQUAL-ROW')
    
