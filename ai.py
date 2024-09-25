import sys
import numpy as np
import pygame
from game import get_best_move, save_parameters
from tetris import check_collision, spawn_piece, rotate, lock_piece, clear_lines, create_empty_grid, SHAPES, update_score, GRID_WIDTH, GRID_HEIGHT
from utils import score_parameters, load_parameters
import os
import signal

#Genetic Algorithm parameters
POPULATION_SIZE = 50  #Further reduced population size for quicker testing
GENERATIONS = 50      #Fewer generations to evolve
MUTATION_RATE = 0.05  #Keep mutation rate the same
CROSSOVER_RATE = 0.5  #Keep crossover rate the same
TOURNAMENT_SIZE = 50  #Reduce the size of the tournament for parent selection
OFFSPRING_SIZE = int(0.3 * POPULATION_SIZE)  #Number of offspring to be generated
REPLACEMENT_RATE = 0.3  #Keep replacement rate the same
NUM_GAMES = 5         #Reduce the number of games for faster testing
MAX_MOVES = 500       #Reduce the maximum number of moves allowed per game


# Colors for the Tetrimino shapes and background
COLORS = {
    "I": (0, 255, 255),  #Cyan
    "O": (255, 255, 0),  #Yellow
    "T": (128, 0, 128),  #Purple
    "S": (0, 255, 0),    #Green
    "Z": (255, 0, 0),    # Red
    "L": (255, 165, 0),  #Orange
    "J": (0, 0, 255),    #Blue
    "BACKGROUND": (0, 0, 0),  #Black
    "GRID": (50, 50, 50),      #Dark grey for grid lines
    "WHITE": (255, 255, 255),  #White for the grid cells
    "TEXT": (255, 255, 255),   #White for text
}


#Define shape names for coloring
SHAPE_NAMES = ["I", "O", "T", "S", "Z", "L", "J"]


def print_colored(text, color_code):
    """Helper function to print text in specified color."""
    print(f"\033[{color_code}m{text}\033[0m")  #Reset color after printing
    
    
def draw_piece(screen, shape, x, y, color):  #Add color as a parameter
    #Draw the piece at its position with the assigned color
    for row_idx, row in enumerate(shape):
        for col_idx, cell in enumerate(row):
            if cell:
                rect = pygame.Rect((x + col_idx) * BLOCK_SIZE, (y + row_idx) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(screen, color, rect.inflate(-2, -2), border_radius=5)


#Initialize Pygame
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 400, 700
BLOCK_SIZE = 30
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris AI Game")
clock = pygame.time.Clock()  #Create a clock to control the frame rate

#Scoreboard position
SCOREBOARD_X = SCREEN_WIDTH - 100
SCOREBOARD_Y = 10

#Define shape names for coloring
SHAPE_NAMES = ["I", "O", "T", "S", "Z", "L", "J"]
HIGH_SCORE_FILE = "high_score.txt"

def load_high_score():
    #Load the high score from a file, default to 0 if the file does not exist or is empty
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as file:
            content = file.read().strip()
            if content:  #Check if the content is not empty
                return int(content)
    return 0  #Return default score if file doesn't exist or is empty



def save_game_results(parameters, score):
    with open("game_results.txt", "a") as file:
        file.write(f"{parameters.tolist()},{score}\n")

def load_game_results():
    results = []
    try:
        with open("game_results.txt", "r") as file:
            for line in file:
                line = line.strip()  #Remove any leading/trailing whitespace
                if line:  #Only process non-empty lines
                    try:
                        param_str, score = line.split(',')
                        results.append((np.array(eval(param_str)), float(score)))  #Convert to numpy array and score
                    except ValueError:
                        print(f"Skipping line due to ValueError: {line.strip()}")
                    except SyntaxError:
                        print(f"Skipping line due to SyntaxError: {line.strip()}")
    except FileNotFoundError:
        print("The file 'game_results.txt' was not found.")
        return []
    
    return results



def update_high_score(score, high_score):
    #Update the high score if the current score is higher
    if score > high_score:
        high_score = score
        save_high_score(high_score)
    return high_score

def save_high_score(high_score):
    #Save the high score to a file
    with open(HIGH_SCORE_FILE, "w") as file:
        file.write(str(high_score))
        
def draw_grid(screen, grid):
    #Draw the grid background
    screen.fill(COLORS["BACKGROUND"])

    #Draw the grid cells with borders
    for x in range(GRID_WIDTH): # type: ignore
        for y in range(GRID_HEIGHT): # type: ignore
            rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(screen, COLORS["GRID"], rect, border_radius=5)
            if grid[y][x]:
                pygame.draw.rect(screen, COLORS["WHITE"], rect.inflate(-2, -2), border_radius=5)


def draw_scoreboard(screen, score, high_score, generation, individual, moves, lines_cleared):
    font = pygame.font.SysFont(None, 28)
    score_text = font.render(f"Score: {score}", True, COLORS["TEXT"])
    high_score_text = font.render(f"High Score: {high_score}", True, COLORS["TEXT"])
    generation_text = font.render(f"Gen: {generation}", True, COLORS["TEXT"])
    individual_text = font.render(f"Ind: {individual}", True, COLORS["TEXT"])
    moves_text = font.render(f"Moves: {moves}", True, COLORS["TEXT"])
    lines_text = font.render(f"Lines: {lines_cleared}", True, COLORS["TEXT"])

    screen.blit(score_text, (20, 660))
    screen.blit(high_score_text, (20, 600))
    screen.blit(generation_text, (SCOREBOARD_X, SCOREBOARD_Y + 60))
    screen.blit(individual_text, (SCOREBOARD_X, SCOREBOARD_Y + 90))
    screen.blit(moves_text, (SCOREBOARD_X, SCOREBOARD_Y + 120))
    screen.blit(lines_text, (SCOREBOARD_X, SCOREBOARD_Y + 150))

def fitness(parameters, individual_idx, generation_idx):
    total_lines_cleared = 0
    high_score = load_high_score()  #Load the high score at the beginning
    print(f"\n{'-'*50}")
    print_colored(f"Evaluating Individual {individual_idx + 1} in Generation {generation_idx + 1}", '34')  # Blue
    print_colored(f"Using Parameters: {parameters}", '32')  #Green
    print(f"{'-'*50}")

    for game_idx in range(NUM_GAMES):
        print_colored(f"  Playing Game {game_idx + 1} for Individual {individual_idx + 1}", '36')

        grid = create_empty_grid()  #Initialize a new game grid
        shape, piece_x, piece_y = spawn_piece()  #Spawn a new piece
        moves = 0
        game_score = 0
        game_over = False

        while moves < MAX_MOVES and not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            screen.fill(COLORS["BACKGROUND"])  #Clear screen
            draw_grid(screen, grid)  #Draw the grid

            shape_color = COLORS[SHAPE_NAMES[SHAPES.index(shape)]]
            draw_piece(screen, shape, piece_x, piece_y, shape_color)  #Draw the piece

            #Get the best move
            rotation, best_x, best_y = get_best_move(grid, shape, piece_x, piece_y, parameters)

            #Rotate the piece if needed
            for _ in range(rotation):
                shape = rotate(shape)

            piece_x = best_x
            piece_y = best_y

            #Check for collision
            if not check_collision(grid, shape, piece_x, piece_y + 1):
                piece_y += 1
            else:
                lock_piece(grid, shape, piece_x, piece_y)  #Lock the piece in place
                num_lines_cleared = clear_lines(grid)  #Clear completed lines
                game_score = update_score(game_score, num_lines_cleared)  #Update score
                total_lines_cleared += num_lines_cleared
                shape, piece_x, piece_y = spawn_piece()  #Spawn a new piece

                #Check for game over condition
                if check_collision(grid, shape, piece_x, piece_y):
                    game_over = True  #End game if new piece collides

            moves += 1

            #Draw the scoreboard
            draw_scoreboard(screen, game_score, high_score, generation_idx + 1, individual_idx + 1, moves, total_lines_cleared)

            pygame.display.flip()  #Update the display
            clock.tick(60)  #Limit to 60 frames per second

        #Update high score if needed
        high_score = update_high_score(game_score, high_score)

        #Save the game results after each game
        save_game_results(parameters, game_score)

    print_colored(f"Finished Evaluating Individual {individual_idx + 1}", '35')
    print_colored(f"  Total Lines Cleared: {total_lines_cleared}", '33')
    print_colored(f"  High Score: {high_score}", '31')
    print(f"{'-'*50}\n")

    return high_score


def initialize_population():
    population = []
    previous_results = load_game_results()
    if previous_results:
        best_parameters = max(previous_results, key=lambda x: x[1])[0]  #Best parameter from past games
        population.append(best_parameters)  #Start with the best found
    for _ in range(POPULATION_SIZE - 1):
        vec = np.random.randn(4)  #Create a random 4-dimensional vector
        vec /= np.linalg.norm(vec)  #Normalize the vector
        population.append(vec)
    return population


def evaluate_population(population, generation_idx):
    scores = [fitness(individual, i, generation_idx) for i, individual in enumerate(population)]
    return scores

def select_parents(population, scores):
    tournament_size = min(TOURNAMENT_SIZE, len(population))
    tournament_indices = np.random.choice(len(population), size=tournament_size, replace=False)
    tournament_scores = [scores[i] for i in tournament_indices]
    best_indices = np.argsort(tournament_scores)[-2:]  # Get the indices of the two best scores
    return population[tournament_indices[best_indices[0]]], population[tournament_indices[best_indices[1]]]


def crossover(parent1, parent2):
    point = np.random.randint(1, 4)  #Choose a crossover point
    child = np.concatenate((parent1[:point], parent2[point:]))  #Combine parents
    child = child / np.linalg.norm(child)  #Normalize the child vector
    return child

def mutate(individual):
    mutation = np.random.randn(4) * MUTATION_RATE  #Generate mutation noise
    individual += mutation  #Apply mutation
    individual = individual / np.linalg.norm(individual)  #Normalize the mutated vector
    return individual

def delete_n_last_replacement(population, scores, offspring):
    num_to_replace = int(REPLACEMENT_RATE * POPULATION_SIZE)  #calculate number to replace
    sorted_indices = np.argsort(scores)  #Sort individuals by fitness scores
    weakest_indices = sorted_indices[:num_to_replace]  # ndices of weakest individuals
    new_population = [ind for i, ind in enumerate(population) if i not in weakest_indices]
    new_population.extend(offspring)  #Add new offspring to the population
    return new_population


def genetic_algorithm():
    population = initialize_population()
    high_score = load_high_score()
    best_parameters = None
    best_score = -float('inf')
    
    try:
        for generation in range(GENERATIONS):
            print(f"Generation: {generation + 1}/{GENERATIONS}")
            scores = evaluate_population(population, generation)

            # Check if the best score in this generation is better than the current best
            generation_best_idx = np.argmax(scores)
            generation_best_score = scores[generation_best_idx]
            print(f"Best score this generation: {generation_best_score}")

            if generation_best_score > best_score:
                best_score = generation_best_score
                best_parameters = population[generation_best_idx]
                print(f"New best parameters found: {best_parameters}")
                save_parameters(best_parameters)  # Save the best parameters found so far

        print("Final Best Parameters:", best_parameters)
        return best_parameters

    except KeyboardInterrupt:
        print("Genetic Algorithm interrupted. Saving best parameters found so far.")
        if best_parameters is not None:
            save_parameters(best_parameters)
        sys.exit(0)

if __name__ == "__main__":
    best_params = genetic_algorithm()
    loaded_params = load_parameters()  # Load parameters at the end
    print("Best Parameters loaded after running GA:", loaded_params)