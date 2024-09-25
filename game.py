
import time
import pygame
import numpy as np
import signal
import sys
from tetris import draw_preview, check_collision, spawn_piece, rotate, lock_piece, clear_lines, create_empty_grid, SHAPES, update_score, GRID_WIDTH, GRID_HEIGHT
from utils import *
from ai import *

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 400, 700
PREVIEW_X, PREVIEW_Y = SCREEN_WIDTH - 100, 50

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris Game")

# Define colors
RED = (255, 0, 0)  #Color for the game over message
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def signal_handler(sig, frame):
    print(f"{Colors.WARNING}Exiting... Saving AI parameters.{Colors.ENDC}")
    save_parameters(best_parameters)  #Save the best parameters before exiting
    pygame.quit()
    sys.exit(0)  #Ensure the program exits cleanly

def display_game_over(screen):
    font = pygame.font.SysFont(None, 55)
    text = font.render("Game Over", True, RED)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))

def draw_scoreboard(screen, score, high_score, level, total_completed_lines, time_played):
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    lines_text = font.render(f"Lines: {total_completed_lines}", True, WHITE)
    time_text = font.render(f"Time: {int(time_played)}s", True, WHITE)
    
    screen.blit(score_text, (10, SCREEN_HEIGHT - 50))
    screen.blit(high_score_text, (10, SCREEN_HEIGHT - 90))
    screen.blit(level_text, (10, SCREEN_HEIGHT - 130))
    screen.blit(lines_text, (10, SCREEN_HEIGHT - 170))
    screen.blit(time_text, (10, SCREEN_HEIGHT - 210))

def reset_game():
    grid = create_empty_grid()
    shape, piece_x, piece_y = spawn_piece()
    next_shape, next_piece_x, next_piece_y = spawn_piece()
    return grid, shape, piece_x, piece_y, next_shape, next_piece_x, next_piece_y

def load_parameters_from_file():
    try:
        parameters = np.load("best_parameters.npy")  # Load from .npy file
        if parameters.shape == (4,):  # Ensure the correct shape
            return parameters
        else:
            print(f"{Colors.WARNING}Parameter file has incorrect shape. Using default parameters.{Colors.ENDC}")
            return np.array([-0.5, 0.6, 1.0, -0.2])

    except IOError:
        print(f"{Colors.WARNING}Parameter file not found. Using default parameters.{Colors.ENDC}")
        return np.array([-0.5, 0.6, 1.0, -0.2])


def run_game_with_parameters(parameters, iteration_count):
    grid, shape, piece_x, piece_y, next_shape, next_piece_x, next_piece_y = reset_game()
    score = 0
    level = 5
    total_completed_lines = 0
    game_over = False
    start_time = time.time()
    last_fall_time = pygame.time.get_ticks()

    while not game_over:
        current_time = pygame.time.get_ticks()
        current_fall_speed = 500 - (level - 1) * 50

        if current_time - last_fall_time > current_fall_speed:
            last_fall_time = current_time
            #Get the best move from the AI
            rotation, best_x, best_y = get_best_move(grid, shape, piece_x, piece_y, parameters)
            for _ in range(rotation):
                shape = rotate(shape)  #Rotate the piece the correct number of times

            piece_x = best_x
            piece_y = best_y

            if not check_collision(grid, shape, piece_x, piece_y + 1):
                piece_y += 1
            else:
                lock_piece(grid, shape, piece_x, piece_y)
                num_lines_cleared = clear_lines(grid)
                total_completed_lines += num_lines_cleared
                score = update_score(score, num_lines_cleared)

                if total_completed_lines >= level * 10:
                    level += 1

                shape, piece_x, piece_y = next_shape, next_piece_x, next_piece_y
                next_shape, next_piece_x, next_piece_y = spawn_piece()
                if check_collision(grid, shape, piece_x, piece_y):
                    game_over = True

    #Print iteration status and AI parameters
    print(f"{Colors.HEADER}Game Iteration: {iteration_count}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}AI Parameters: {parameters}{Colors.ENDC}")
    print(f"{Colors.OKGREEN}Total Lines Cleared: {total_completed_lines}{Colors.ENDC}")

    return total_completed_lines  #Return the total number of lines cleared as fitness score

#Main game loop for AI play
if __name__ == "__main__":
    #Register the signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    #Load parameters from file or use defaults
    best_parameters = load_parameters_from_file()
    print(f"Loaded parameters: {best_parameters}")

    high_score = load_high_score()  #Load high score once
    game_counter = 0

    while True:
        #Reset game state
        grid, shape, piece_x, piece_y, next_shape, next_piece_x, next_piece_y = reset_game()
        score = 0
        level = 5
        total_completed_lines = 0
        start_time = time.time()
        last_fall_time = pygame.time.get_ticks()
        game_over = False

        while not game_over:
            screen.fill(BLACK)
            draw_grid(screen, grid)
            draw_piece(screen, shape, piece_x, piece_y, WHITE)
            draw_preview(screen, next_shape, PREVIEW_X, PREVIEW_Y)

            current_time = pygame.time.get_ticks()
            time_played = time.time() - start_time

            if current_time - last_fall_time > 500 - (level - 1) * 50:
                last_fall_time = current_time
                rotation, best_x, best_y = get_best_move(grid, shape, piece_x, piece_y, best_parameters)
                for _ in range(rotation):
                    shape = rotate(shape)

                piece_x = best_x
                piece_y = best_y

                if not check_collision(grid, shape, piece_x, piece_y + 1):
                    piece_y += 1
                else:
                    lock_piece(grid, shape, piece_x, piece_y)
                    num_lines_cleared = clear_lines(grid)
                    total_completed_lines += num_lines_cleared
                    score = update_score(score, num_lines_cleared)
                    #Log game status
                    print(f"{Colors.OKGREEN}Current Score: {score}{Colors.ENDC}")
                    print(f"{Colors.OKBLUE}Level: {level}{Colors.ENDC}")
                    print(f"{Colors.WARNING}Total Lines Cleared: {total_completed_lines}{Colors.ENDC}")
                    print(f"{Colors.BOLD}Time Played: {int(time_played)} seconds{Colors.ENDC}")

                    if total_completed_lines >= level * 10:
                        level += 1

                    shape, piece_x, piece_y = next_shape, next_piece_x, next_piece_y
                    next_shape, next_piece_x, next_piece_y = spawn_piece()
                    if check_collision(grid, shape, piece_x, piece_y):
                        high_score = update_high_score(score, high_score)
                        display_game_over(screen)
                        pygame.display.flip()

                        game_over = True

            draw_scoreboard(screen, score, high_score, level, total_completed_lines, time_played)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_parameters(best_parameters)  #Save parameters when quitting
                    save_high_score(high_score)  #Save high score when quitting
                    pygame.quit()
                    exit()