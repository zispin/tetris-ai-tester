import random
import os
import pygame

#Screen and grid dimensions
GRID_WIDTH, GRID_HEIGHT = 10, 20
BLOCK_SIZE = 20
HIGH_SCORE_FILE = "high_score.txt"
lines = 0

#Define the shapes of the Tetriminos
SHAPES = [
    [[1, 1, 1, 1]],  #I shape
    [[1, 1], [1, 1]],  #O shape
    [[0, 1, 0], [1, 1, 1]],  #T shape
    [[1, 1, 0], [0, 1, 1]],  #S shape
    [[0, 1, 1], [1, 1, 0]],  #Z shape
    [[1, 1, 1], [0, 0, 1]],  #L shape
    [[1, 1, 1], [1, 0, 0]]   #J shape
]

#Basic colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def create_empty_grid():
    #Create an empty grid filled with zeros
    return [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def update_high_score(score, high_score):
    #Update the high score if the current score is higher
    if score > high_score:
        high_score = score
        save_high_score(high_score)
    return high_score

def load_high_score():
    #Load the high score from a file, default to 0 if file does not exist
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as file:
            return int(file.read())
    return 0

def save_high_score(score):
    #Save the high score to a file
    with open(HIGH_SCORE_FILE, "w") as file:
        file.write(str(score))

def draw_grid(screen, grid):
    #Draw the game grid on the screen
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(screen, WHITE, rect, 1 if grid[y][x] == 0 else 0)

def spawn_piece():
    #Randomly select a Tetrimino shape and initialize its position
    shape = random.choice(SHAPES)
    piece_x = GRID_WIDTH // 2 - len(shape[0]) // 2
    piece_y = 0
    return shape, piece_x, piece_y

def draw_piece(screen, shape, x, y, color=WHITE):
    #Draw the Tetrimino piece on the screen
    for row_idx, row in enumerate(shape):
        for col_idx, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, color, pygame.Rect((x + col_idx) * BLOCK_SIZE, (y + row_idx) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

def draw_preview(screen, shape, preview_x, preview_y):
    #Draw a preview of the upcoming Tetrimino
    for row_idx, row in enumerate(shape):
        for col_idx, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, WHITE, pygame.Rect(preview_x + col_idx * BLOCK_SIZE, preview_y + row_idx * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

def check_collision(grid, shape, x, y):
    #Check if the Tetrimino piece collides with the grid boundaries or other pieces
    for row_idx, row in enumerate(shape):
        for col_idx, cell in enumerate(row):
            if cell:
                grid_x = x + col_idx
                grid_y = y + row_idx
                if grid_x < 0 or grid_x >= GRID_WIDTH or grid_y >= GRID_HEIGHT or grid[grid_y][grid_x]:
                    return True
    return False

def lock_piece(grid, shape, x, y):
    #Lock the Tetrimino piece into the grid
    for row_idx, row in enumerate(shape):
        for col_idx, cell in enumerate(row):
            if cell:
                grid[y + row_idx][x + col_idx] = 1

def display_final_score(screen, score, high_score):
    #Display the final score and high score on the screen
    font = pygame.font.SysFont(None, 55)
    text = font.render(f"Final Score: {score}", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    
    screen.fill(BLACK)  #Clear the screen
    screen.blit(text, (GRID_WIDTH * BLOCK_SIZE / 2 - text.get_width() / 2, GRID_HEIGHT * BLOCK_SIZE / 2 - text.get_height() / 2 - 30))
    screen.blit(high_score_text, (GRID_WIDTH * BLOCK_SIZE / 2 - high_score_text.get_width() / 2, GRID_HEIGHT * BLOCK_SIZE / 2 - high_score_text.get_height() / 2 + 30))
    
    pygame.display.flip()
    pygame.time.wait(3000)  #Wait for 3 seconds to let the player see the final score

def handle_end_of_game(score):
    #Handle the end of the game, update and display high score
    high_score = load_high_score()
    
    #Update high score if necessary
    if score > high_score:
        save_high_score(score)
        high_score = score  #Update local high_score to the new high score
    
    #Initialize Pygame screen to display the final score
    screen = pygame.display.set_mode((GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE))
    pygame.display.set_caption("Game Over")
    display_final_score(screen, score, high_score)

def drop_piece(grid, shape, piece_x, piece_y):
    #Drop the Tetrimino piece down to the lowest possible position
    while not check_collision(grid, shape, piece_x, piece_y + 1):
        piece_y += 1
    lock_piece(grid, shape, piece_x, piece_y)
    return spawn_piece()

def is_game_over(grid):
    #Check if the game is over by checking if any blocks are in the top row
    return any(grid[0][x] for x in range(GRID_WIDTH))

def rotate(shape):
    #Rotate the Tetrimino piece 90 degrees clockwise
    return [list(row) for row in zip(*shape[::-1])]

def clear_lines(grid):
    #Clear complete lines from the grid and return the number of lines cleared
    lines_to_clear = [i for i, row in enumerate(grid) if all(row)]
    num_lines_cleared = len(lines_to_clear)
    lines_cleared = num_lines_cleared  #Update lines_cleared locally
    
    for line in lines_to_clear:
        del grid[line]
        grid.insert(0, [0] * GRID_WIDTH)
    
    return lines_cleared

def update_score(score, num_lines_cleared):
    #Update the score based on the number of lines cleared
    if num_lines_cleared == 1:
        score += 100
    elif num_lines_cleared == 2:
        score += 300
    elif num_lines_cleared == 3:
        score += 600
    elif num_lines_cleared >= 4:
        score += 1000
    return score

def draw_ghost_piece(screen, grid, shape, piece_x, piece_y):
    #Draw a ghost piece to show where the Tetrimino would land
    ghost_y = piece_y
    while not check_collision(grid, shape, piece_x, ghost_y + 1):
        ghost_y += 1
    draw_piece(screen, shape, piece_x, ghost_y, color=(200, 200, 200))  #Gray color for the ghost piece
