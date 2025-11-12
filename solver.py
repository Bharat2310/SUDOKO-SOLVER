def is_valid(board, row, col, num):
    """
    Check if placing num at board[row][col] is valid.
    
    Args:
        board: 9x9 2D list representing the Sudoku grid
        row: row index (0-8)
        col: column index (0-8)
        num: number to check (1-9)
    
    Returns:
        bool: True if placement is valid, False otherwise
    """
    # Check row
    for x in range(9):
        if board[row][x] == num:
            return False
    
    # Check column
    for x in range(9):
        if board[x][col] == num:
            return False
    
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[i + start_row][j + start_col] == num:
                return False
    
    return True


def find_empty_location(board):
    """
    Find an empty cell in the board (represented by 0).
    
    Args:
        board: 9x9 2D list representing the Sudoku grid
    
    Returns:
        tuple: (row, col) of empty cell, or None if no empty cell exists
    """
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return (i, j)
    return None


def solve_sudoku(board):
    """
    Solve Sudoku puzzle using backtracking algorithm.
    
    Args:
        board: 9x9 2D list representing the Sudoku grid (0 represents empty cells)
    
    Returns:
        bool: True if puzzle is solved, False if no solution exists
    """
    # Find empty location
    empty = find_empty_location(board)
    
    # If no empty location, puzzle is solved
    if not empty:
        return True
    
    row, col = empty
    
    # Try digits 1-9
    for num in range(1, 10):
        if is_valid(board, row, col, num):
            # Place the number
            board[row][col] = num
            
            # Recursively attempt to solve
            if solve_sudoku(board):
                return True
            
            # Backtrack if solution not found
            board[row][col] = 0
    
    # Trigger backtracking
    return False


def validate_board(board):
    """
    Validate that the input board is properly formatted.
    
    Args:
        board: Input to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not isinstance(board, list):
        return False, "Board must be a list"
    
    if len(board) != 9:
        return False, "Board must have 9 rows"
    
    for i, row in enumerate(board):
        if not isinstance(row, list):
            return False, f"Row {i} must be a list"
        
        if len(row) != 9:
            return False, f"Row {i} must have 9 columns"
        
        for j, cell in enumerate(row):
            if not isinstance(cell, int):
                return False, f"Cell [{i}][{j}] must be an integer"
            
            if cell < 0 or cell > 9:
                return False, f"Cell [{i}][{j}] must be between 0 and 9"
    
    return True, None