# Tetris AI with Genetic Algorithm

## Overview

This project involves a classic game of Tetris enhanced with an AI that uses a Genetic Algorithm (GA) to optimize its performance. The AI plays Tetris using a set of parameters, which are evolved through the GA to improve the AI's gameplay over time.

## Project Structure

- **`ai.py`**: Implements the Genetic Algorithm that evolves AI parameters to maximize its score in Tetris. It includes logic for population initialization, fitness evaluation, crossover, mutation, and selection of the best individuals across generations.
- **`game.py`**: Manages the Tetris game loop and integrates the AI's decision-making. The game runs based on the parameters provided by the AI and displays visual feedback using Pygame.
- **`tetris.py`**: Defines the core mechanics of Tetris, including grid management, piece movement, collision detection, and line clearing. It handles the fundamental game logic.
- **`utils.py`**: Contains utility functions to evaluate AI performance, including scoring based on the grid's state (e.g., aggregate height, holes, bumpiness). This is crucial for the AI's decision-making.
- **`best_parameters.npy`**: Stores the best AI parameters found by the Genetic Algorithm during training.
- **`high_score.txt`**: Stores the highest score achieved in the game.
- **`__pycache__/`**: A directory containing compiled Python files.

## How to Run

1. Ensure you have Python and Pygame installed on your system. You can install Pygame using pip:

    ```bash
    pip install pygame
    ```

2. To run the Tetris game with the AI, execute the `game.py` file:

    ```bash
    python game.py
    ```

   This will start the Tetris game and use the current best parameters to control the AI.

3. To train the AI using the Genetic Algorithm, execute the `ai.py` file:

    ```bash
    python ai.py
    ```

   This will start the GA process, which will evolve the parameters and save the best ones found.

## How It Works

- **Tetris Game**: The game is a classic Tetris implementation where pieces fall from the top of the screen and the player must fit them into a grid.
- **AI Control**: The AI controls the pieces based on parameters optimized through a Genetic Algorithm.
- **Genetic Algorithm**: The GA evolves a population of parameter sets over several generations to find the most effective parameters for the AI.

## Files and Functions

- `ai.py`
  - `fitness(parameters)`: Evaluates how well a set of parameters performs.
  - `initialize_population()`: Initializes the population for the GA.
  - `evaluate_population(population)`: Evaluates the fitness of each individual in the population.
  - `select_parents(population, scores)`: Selects parents for crossover.
  - `crossover(parent1, parent2)`: Performs crossover to generate new individuals.
  - `mutate(individual)`: Applies mutations to individuals.
  - `delete_n_last_replacement(population, scores, offspring)`: Replaces the weakest individuals with new offspring.
  - `genetic_algorithm()`: Main function to run the GA.

- `game.py`
  - `signal_handler(sig, frame)`: Handles signals to save parameters and exit gracefully.
  - `display_game_over(screen)`: Displays the game over message.
  - `draw_scoreboard(screen, score, high_score, level, total_completed_lines, time_played)`: Draws the scoreboard.
  - `reset_game()`: Resets the game state.
  - `load_parameters_from_file()`: Loads AI parameters from a file.
  - `run_game_with_parameters(parameters, iteration_count)`: Runs the game with specified parameters and returns the fitness score.

- `tetris.py`
  - `create_empty_grid()`: Creates an empty game grid.
  - `update_high_score(score, high_score)`: Updates the high score if necessary.
  - `load_high_score()`: Loads the high score from a file.
  - `save_high_score(score)`: Saves the high score to a file.
  - `draw_grid(screen, grid)`: Draws the game grid.
  - `spawn_piece()`: Spawns a new Tetris piece.
  - `draw_piece(screen, shape, x, y, color=WHITE)`: Draws a Tetris piece on the screen.
  - `draw_preview(screen, shape, preview_x, preview_y)`: Draws the next piece preview.
  - `check_collision(grid, shape, x, y)`: Checks for collisions.
  - `lock_piece(grid, shape, x, y)`: Locks a piece in place.
  - `display_final_score(screen, score, high_score)`: Displays the final score.
  - `handle_end_of_game(score)`: Handles game over conditions and updates the score.
