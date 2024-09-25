import numpy as np

#Import necessary functions from tetris (assuming you have them there)
from tetris import rotate, check_collision, lock_piece, clear_lines, GRID_WIDTH, GRID_HEIGHT

def get_best_move(grid, shape, piece_x, piece_y, parameters):
    #Find the best move for the Tetrimino based on score parameters
    best_score = -float('inf')
    best_move = None

    #Test all possible actions
    for rotation in range(4):
        rotated_shape = shape
        for _ in range(rotation):
            rotated_shape = rotate(rotated_shape)  #Rotate the piece 90 degrees

        for x in range(GRID_WIDTH):
            if not check_collision(grid, rotated_shape, x, piece_y):
                #Drop the piece to the lowest possible position
                test_y = piece_y
                while not check_collision(grid, rotated_shape, x, test_y + 1):
                    test_y += 1

                #Evaluate this position
                test_grid = [row[:] for row in grid]
                lock_piece(test_grid, rotated_shape, x, test_y)
                score = score_parameters(test_grid, parameters)

                if score > best_score:
                    best_score = score
                    best_move = (rotation, x, test_y)

    return best_move

def score_parameters(grid, parameters):
    #Calculate the score based on the grid and parameters
    aggregate_height = calculate_aggregate_height(grid)
    complete_lines = sum(row.count(1) == GRID_WIDTH for row in grid)
    holes = count_holes(grid)
    bumpiness = calculate_bumpiness(grid)
    
    x = np.array([aggregate_height, complete_lines, holes, bumpiness])
    return np.dot(parameters, x)

def calculate_aggregate_height(grid):
    #Calculate the sum of heights of all columns
    aggregate_height = 0
    for col_idx in range(GRID_WIDTH):
        col_height = sum(1 for row_idx in range(GRID_HEIGHT) if grid[row_idx][col_idx] == 1)
        aggregate_height += col_height
    return aggregate_height

def count_holes(grid):
    #Count the number of holes in the grid
    holes = 0
    for col_idx in range(GRID_WIDTH):
        column_has_tile = False
        for row_idx in range(GRID_HEIGHT):
            if grid[row_idx][col_idx] == 1:
                column_has_tile = True
            elif grid[row_idx][col_idx] == 0 and column_has_tile:
                holes += 1
    return holes

def calculate_bumpiness(grid):
    #Calculate the bumpiness of the grid
    column_heights = [0] * GRID_WIDTH
    for col_idx in range(GRID_WIDTH):
        for row_idx in range(GRID_HEIGHT):
            if grid[row_idx][col_idx] == 1:
                column_heights[col_idx] = GRID_HEIGHT - row_idx
                break
    bumpiness = 0
    for i in range(GRID_WIDTH - 1):
        bumpiness += abs(column_heights[i] - column_heights[i + 1])
    return bumpiness

def save_parameters(parameters, filename="best_parameters.npy"):
    try:
        np.save(filename, parameters)
        print(f"Parameters saved successfully: {parameters}")
    except Exception as e:
        print(f"Error saving parameters: {e}")

def load_parameters(filename="best_parameters.npy"):
    try:
        parameters = np.load(filename)
        if parameters.shape != (4,):
            raise ValueError("Parameters must be a 1D array of shape (4,)")
        return parameters
    except FileNotFoundError:
        print("Parameter file not found. Using default parameters.")
        return np.array([-0.5, 0.6, 1.0, -0.2])  # Default parameters
    except ValueError as e:
        print(e)
        return np.array([-0.5, 0.6, 1.0, -0.2])  # Default parameters