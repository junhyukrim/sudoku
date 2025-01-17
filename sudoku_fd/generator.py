import random

def generate(num):
    def is_valid_partial(board, row, col, num):
        # Check row
        if num in board[row]:
            return False
        # Check column
        if num in [board[i][col] for i in range(9)]:
            return False
        # Check 3x3 box
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(start_row, start_row + 3):
            for j in range(start_col, start_col + 3):
                if board[i][j] == num:
                    return False
        return True

    # Initialize empty board and shuffled cells list
    board = [[0 for _ in range(9)] for _ in range(9)]
    cells = [(i, j) for i in range(9) for j in range(9)]
    random.shuffle(cells)

    count = 0
    max_attempts = 2000  # Limit the number of attempts to prevent infinite loops
    attempts = 0

    while count < num and attempts < max_attempts:
        if not cells:  # Check if cells list is empty
            print("Failed to generate a valid Sudoku puzzle. Retrying...")
            return generate(num)  # Retry generating a new puzzle

        row, col = cells.pop()  # Safely pop a cell from the list
        value = random.randint(1, 9)
        if is_valid_partial(board, row, col, value):  # Check validity before placing the number
            board[row][col] = value
            count += 1

        attempts += 1

    if attempts >= max_attempts:
        print("Maximum attempts reached. Unable to generate a valid puzzle.")
        return None

    return board
