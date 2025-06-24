import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GAME_WIDTH = 600
GAME_HEIGHT = 400
GRID_SIZE = 20
GRID_WIDTH = GAME_WIDTH // GRID_SIZE
GRID_HEIGHT = GAME_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (39, 174, 96)
LIGHT_GREEN = (46, 204, 113)
RED = (231, 76, 60)
BLUE = (52, 152, 219)
ORANGE = (230, 126, 34)
GRAY = (149, 165, 166)
DARK_GRAY = (44, 62, 80)
LIGHT_GRAY = (236, 240, 241)

class MathSnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Math Snake Game")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # Game state
        self.reset_game()
        
        # Sound generation
        self.generate_sounds()
        
    def generate_sounds(self):
        """Generate sound effects using pygame"""
        try:
            import numpy as np
            # Create sound arrays for different effects
            sample_rate = 22050
            
            # Success sound (ascending notes)
            duration = 0.2
            frames = int(duration * sample_rate)
            wave = 4096 * np.sin(2 * np.pi * 523 * np.arange(frames) / sample_rate)  # C note
            stereo_wave = np.column_stack((wave, wave)).astype(np.int16)
            stereo_wave = np.ascontiguousarray(stereo_wave)
            self.success_sound = pygame.sndarray.make_sound(stereo_wave)
            
            # Error sound (low buzz)
            duration = 0.3
            frames = int(duration * sample_rate)
            wave = 2048 * np.sin(2 * np.pi * 200 * np.arange(frames) / sample_rate)
            stereo_wave = np.column_stack((wave, wave)).astype(np.int16)
            stereo_wave = np.ascontiguousarray(stereo_wave)
            self.error_sound = pygame.sndarray.make_sound(stereo_wave)
            
            # Game over sound
            duration = 0.5
            frames = int(duration * sample_rate)
            wave = 3072 * np.sin(2 * np.pi * 150 * np.arange(frames) / sample_rate)
            stereo_wave = np.column_stack((wave, wave)).astype(np.int16)
            stereo_wave = np.ascontiguousarray(stereo_wave)
            self.game_over_sound = pygame.sndarray.make_sound(stereo_wave)
            
        except (ImportError, Exception) as e:
            # Fallback: create dummy sound objects that don't play anything
            print(f"Sound generation failed ({e}), sounds disabled")
            self.success_sound = None
            self.error_sound = None
            self.game_over_sound = None
    
    def reset_game(self):
        """Reset game to initial state"""
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (0, 0)
        self.score = 0
        self.level = 0
        self.lives = 2  # Player gets 2 wrong eggs before game over
        self.base_speed = 8  # FPS divisor
        self.current_speed = self.base_speed
        self.wrong_egg_penalty = False
        self.penalty_timer = 0
        self.game_over = False
        self.paused = False
        self.numbers_to_collect = []
        self.collected_numbers = []
        
        # Timer system
        self.level_time_limit = self.get_time_limit_for_level(self.level)
        self.time_remaining = self.level_time_limit
        self.timer_running = False
        
        self.generate_equation()
        self.generate_eggs()
    
    def get_time_limit_for_level(self, level):
        """Get time limit in seconds for each level"""
        base_time = 45  # 45 seconds for level 0
        return max(20, base_time - (level * 3))  # Decrease by 3 seconds per level, minimum 20 seconds
    
    def generate_equation(self):
        """Generate a random math equation based on current level"""
        if self.level == 0:
            # Level 0: Simple addition/subtraction (single operation)
            operations = ['+', '-']
            operation = random.choice(operations)
            
            if operation == '+':
                num1 = random.randint(1, 10)
                num2 = random.randint(1, 10)
                answer = num1 + num2
            else:  # subtraction
                num1 = random.randint(10, 20)
                num2 = random.randint(1, num1 - 1)
                answer = num1 - num2
            
            self.current_equation = {
                'equation': f"{num1} {operation} {num2} = ?",
                'answer': answer,
                'numbers': [num1, num2],
                'operations': [operation]
            }
            
        elif self.level == 1:
            # Level 1: Add multiplication and division
            operations = ['+', '-', '*', '/']
            operation = random.choice(operations)
            
            if operation == '+':
                num1 = random.randint(5, 15)
                num2 = random.randint(5, 15)
                answer = num1 + num2
            elif operation == '-':
                num1 = random.randint(15, 25)
                num2 = random.randint(1, num1 - 1)
                answer = num1 - num2
            elif operation == '*':
                num1 = random.randint(2, 8)
                num2 = random.randint(2, 8)
                answer = num1 * num2
            else:  # division
                answer = random.randint(2, 12)
                num2 = random.randint(2, 6)
                num1 = answer * num2
            
            self.current_equation = {
                'equation': f"{num1} {operation} {num2} = ?",
                'answer': answer,
                'numbers': [num1, num2],
                'operations': [operation]
            }
            
        else:
            # Level 2+: Complex equations with multiple operations
            complexity = min(self.level, 5)  # Cap complexity at level 5
            
            if complexity == 2:
                # Two operations: a + b - c = ?
                num1 = random.randint(10, 20)
                num2 = random.randint(1, 10)
                num3 = random.randint(1, min(10, num1 + num2 - 1))
                answer = num1 + num2 - num3
                
                self.current_equation = {
                    'equation': f"{num1} + {num2} - {num3} = ?",
                    'answer': answer,
                    'numbers': [num1, num2, num3],
                    'operations': ['+', '-']
                }
                
            elif complexity == 3:
                # Three operations: a * b + c - d = ?
                num1 = random.randint(2, 5)
                num2 = random.randint(2, 5)
                num3 = random.randint(5, 15)
                num4 = random.randint(1, 10)
                answer = num1 * num2 + num3 - num4
                
                self.current_equation = {
                    'equation': f"{num1} × {num2} + {num3} - {num4} = ?",
                    'answer': answer,
                    'numbers': [num1, num2, num3, num4],
                    'operations': ['*', '+', '-']
                }
                
            elif complexity == 4:
                # Four operations with division: a * b / c + d = ?
                num3 = random.randint(2, 4)  # divisor
                num1 = random.randint(2, 6)
                num2 = num3 * random.randint(2, 4)  # ensure clean division
                num4 = random.randint(1, 10)
                answer = (num1 * num2) // num3 + num4
                
                self.current_equation = {
                    'equation': f"{num1} × {num2} ÷ {num3} + {num4} = ?",
                    'answer': answer,
                    'numbers': [num1, num2, num3, num4],
                    'operations': ['*', '/', '+']
                }
                
            else:  # complexity >= 5
                # Complex: a + b * c - d / e = ?
                num1 = random.randint(5, 15)
                num2 = random.randint(2, 5)
                num3 = random.randint(2, 5)
                num5 = random.randint(2, 4)  # divisor
                num4 = num5 * random.randint(2, 6)  # ensure clean division
                answer = num1 + (num2 * num3) - (num4 // num5)
                
                self.current_equation = {
                    'equation': f"{num1} + {num2} × {num3} - {num4} ÷ {num5} = ?",
                    'answer': answer,
                    'numbers': [num1, num2, num3, num4, num5],
                    'operations': ['+', '*', '-', '/']
                }
    
    def generate_eggs(self):
        """Generate eggs with numbers on the field"""
        self.eggs = []
        self.numbers_to_collect = self.current_equation['numbers'].copy()
        self.collected_numbers = []
        
        # Add target number eggs (the ones we need to collect)
        for target_num in self.numbers_to_collect:
            pos = self.get_random_position()
            while pos in [egg['pos'] for egg in self.eggs] or pos in self.snake:
                pos = self.get_random_position()
            
            self.eggs.append({
                'pos': pos,
                'number': target_num,
                'is_target': True,
                'collected': False
            })
        
        # Add decoy eggs (wrong numbers) - more decoys for higher levels
        decoy_count = 6 + self.level  # More decoys as level increases
        decoy_numbers = set()
        max_decoy_value = max(20, max(self.numbers_to_collect) + 10)
        
        while len(decoy_numbers) < decoy_count:
            decoy_num = random.randint(1, max_decoy_value)
            if decoy_num not in self.numbers_to_collect:
                decoy_numbers.add(decoy_num)
        
        for decoy_num in decoy_numbers:
            pos = self.get_random_position()
            while pos in [egg['pos'] for egg in self.eggs] or pos in self.snake:
                pos = self.get_random_position()
            
            self.eggs.append({
                'pos': pos,
                'number': decoy_num,
                'is_target': False,
                'collected': False
            })
    
    def get_random_position(self):
        """Get a random position on the grid"""
        return (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                if self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                    continue
                
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                    continue
                
                if not self.paused:
                    # Movement controls
                    if event.key == pygame.K_UP and self.direction != (0, 1):
                        self.direction = (0, -1)
                    elif event.key == pygame.K_DOWN and self.direction != (0, -1):
                        self.direction = (0, 1)
                    elif event.key == pygame.K_LEFT and self.direction != (1, 0):
                        self.direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
                        self.direction = (1, 0)
        
        return True
    
    def update(self):
        """Update game state"""
        if self.game_over or self.paused or self.direction == (0, 0):
            return
        
        # Start timer when player starts moving
        if not self.timer_running and self.direction != (0, 0):
            self.timer_running = True
        
        # Update timer
        if self.timer_running:
            self.time_remaining -= 1/60  # Decrease by 1/60 second each frame (60 FPS)
            if self.time_remaining <= 0:
                self.end_game("Time's up!")
                return
        
        # Handle penalty timer
        if self.wrong_egg_penalty:
            self.penalty_timer -= 1
            if self.penalty_timer <= 0:
                self.wrong_egg_penalty = False
                self.current_speed = self.base_speed
        
        # Move snake
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        
        # Check wall collision
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or 
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            self.end_game("Hit the wall!")
            return
        
        # Check self collision
        if new_head in self.snake:
            self.end_game("Hit yourself!")
            return
        
        self.snake.insert(0, new_head)
        
        # Check egg collision
        eaten_egg = None
        for egg in self.eggs:
            if egg['pos'] == new_head and not egg.get('collected', False):
                eaten_egg = egg
                break
        
        if eaten_egg:
            if eaten_egg['is_target']:
                # Correct target number
                if self.success_sound:
                    self.success_sound.play()
                
                eaten_egg['collected'] = True
                self.collected_numbers.append(eaten_egg['number'])
                
                # Check if all target numbers are collected
                if len(self.collected_numbers) == len(self.numbers_to_collect):
                    # All numbers collected - equation solved!
                    self.score += 1
                    
                    # Check for level up (every 3 equations solved)
                    if self.score % 3 == 0:
                        self.level += 1
                        self.level_time_limit = self.get_time_limit_for_level(self.level)
                        self.time_remaining = self.level_time_limit
                        self.base_speed = max(4, self.base_speed - 1)
                        self.current_speed = self.base_speed
                    
                    self.generate_equation()
                    self.generate_eggs()
                    
                    # Reset penalty
                    self.wrong_egg_penalty = False
                    self.penalty_timer = 0
                
            else:
                # Wrong number (decoy) - LOSE A LIFE!
                if self.error_sound:
                    self.error_sound.play()
                
                self.lives -= 1
                eaten_egg['collected'] = True  # Mark as collected to remove from field
                
                # Check if game over (no lives left)
                if self.lives <= 0:
                    self.end_game("No lives left!")
                    return
                
                self.wrong_egg_penalty = True
                self.penalty_timer = 120  # 2 seconds at 60 FPS
                self.current_speed = self.base_speed + 4  # Slow down
        else:
            # Remove tail if no egg eaten
            self.snake.pop()
    
    def end_game(self, reason="Game Over"):
        """End the game"""
        self.game_over = True
        self.game_over_reason = reason
        if self.game_over_sound:
            self.game_over_sound.play()
    
    def draw(self):
        """Draw everything on screen"""
        self.screen.fill(DARK_GRAY)
        
        # Draw game area background
        game_rect = pygame.Rect(100, 150, GAME_WIDTH, GAME_HEIGHT)
        pygame.draw.rect(self.screen, LIGHT_GRAY, game_rect)
        pygame.draw.rect(self.screen, BLACK, game_rect, 2)
        
        # Draw game info header
        header_y = 20
        
        # Draw equation
        equation_text = self.font_large.render(self.current_equation['equation'], True, BLUE)
        equation_rect = equation_text.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.blit(equation_text, equation_rect)
        
        # Draw level, score, lives, and timer
        level_text = self.font_medium.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (20, header_y))
        
        score_text = self.font_medium.render(f"Score: {self.score}", True, RED)
        score_rect = score_text.get_rect(topright=(WINDOW_WIDTH - 20, header_y))
        self.screen.blit(score_text, score_rect)
        
        lives_text = self.font_medium.render(f"Lives: {self.lives}", True, RED)
        self.screen.blit(lives_text, (20, header_y + 25))
        
        # Timer with color coding
        timer_color = RED if self.time_remaining < 10 else ORANGE if self.time_remaining < 20 else WHITE
        timer_text = self.font_medium.render(f"Time: {int(self.time_remaining)}s", True, timer_color)
        timer_rect = timer_text.get_rect(topright=(WINDOW_WIDTH - 20, header_y + 25))
        self.screen.blit(timer_text, timer_rect)
        
        # Draw speed indicator
        speed_text = self.font_small.render(f"Speed: {11 - self.base_speed}", True, GRAY)
        self.screen.blit(speed_text, (20, header_y + 50))
        
        if not self.game_over:
            # Draw snake
            snake_color = ORANGE if self.wrong_egg_penalty else GREEN
            head_color = RED if self.wrong_egg_penalty else LIGHT_GREEN
            
            for i, (x, y) in enumerate(self.snake):
                rect = pygame.Rect(100 + x * GRID_SIZE, 150 + y * GRID_SIZE, 
                                 GRID_SIZE - 1, GRID_SIZE - 1)
                color = head_color if i == 0 else snake_color
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, BLACK, rect, 1)
            
            # Draw eggs (all eggs now look the same - no color coding!)
            for egg in self.eggs:
                if not egg['collected']:
                    x, y = egg['pos']
                    center = (100 + x * GRID_SIZE + GRID_SIZE // 2, 
                             150 + y * GRID_SIZE + GRID_SIZE // 2)
                    
                    # Draw egg circle - all eggs are the same color now!
                    egg_color = BLUE  # Same color for all eggs
                    pygame.draw.circle(self.screen, egg_color, center, GRID_SIZE // 2 - 2)
                    pygame.draw.circle(self.screen, BLACK, center, GRID_SIZE // 2 - 2, 2)
                    
                    # Draw number
                    number_text = self.font_small.render(str(egg['number']), True, WHITE)
                    number_rect = number_text.get_rect(center=center)
                    self.screen.blit(number_text, number_rect)
        
        # Draw instructions
        if self.direction == (0, 0) and not self.game_over:
            instruction_text = self.font_medium.render("Collect ALL numbers from the equation! 2 wrong eggs = Game Over!", True, WHITE)
            instruction_rect = instruction_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 80))
            self.screen.blit(instruction_text, instruction_rect)
        
        # Draw collection progress
        if len(self.collected_numbers) > 0:
            progress_text = f"Collected: {', '.join(map(str, self.collected_numbers))}"
            progress_surface = self.font_small.render(progress_text, True, WHITE)
            self.screen.blit(progress_surface, (20, 100))
        
        # Draw what numbers are needed
        if len(self.numbers_to_collect) > 0:
            remaining_numbers = [n for n in self.numbers_to_collect if n not in self.collected_numbers]
            if remaining_numbers:
                needed_text = f"Still need: {', '.join(map(str, remaining_numbers))}"
                needed_surface = self.font_small.render(needed_text, True, BLUE)
                self.screen.blit(needed_surface, (20, 120))
        
        # Draw penalty indicator
        if self.wrong_egg_penalty:
            penalty_text = self.font_medium.render(f"WRONG NUMBER! Lives: {self.lives} | Snake slowed!", True, RED)
            penalty_rect = penalty_text.get_rect(center=(WINDOW_WIDTH // 2, 100))
            self.screen.blit(penalty_text, penalty_rect)
        
        # Draw pause indicator
        if self.paused:
            pause_text = self.font_large.render("PAUSED - Press P to continue", True, WHITE)
            pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            pygame.draw.rect(self.screen, BLACK, pause_rect.inflate(20, 10))
            self.screen.blit(pause_text, pause_rect)
        
        # Draw game over screen
        if self.game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            # Game over text
            game_over_text = self.font_large.render("GAME OVER!", True, RED)
            game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 80))
            self.screen.blit(game_over_text, game_over_rect)
            
            # Game over reason
            reason_text = self.font_medium.render(getattr(self, 'game_over_reason', 'Game Over'), True, WHITE)
            reason_rect = reason_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
            self.screen.blit(reason_text, reason_rect)
            
            # Final stats
            final_score_text = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
            final_score_rect = final_score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
            self.screen.blit(final_score_text, final_score_rect)
            
            final_level_text = self.font_medium.render(f"Reached Level: {self.level}", True, WHITE)
            final_level_rect = final_level_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10))
            self.screen.blit(final_level_text, final_level_rect)
            
            restart_text = self.font_medium.render("Press SPACE to play again or ESC to quit", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
            self.screen.blit(restart_text, restart_rect)
        
        # Draw controls
        controls = [
            "Controls:",
            "Arrow Keys - Move",
            "P - Pause",
            "ESC - Quit"
        ]
        
        for i, control in enumerate(controls):
            color = WHITE if i == 0 else GRAY
            font = self.font_small if i == 0 else self.font_small
            control_text = font.render(control, True, color)
            self.screen.blit(control_text, (20, WINDOW_HEIGHT - 100 + i * 20))
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        frame_count = 0
        
        while True:
            if not self.handle_events():
                break
            
            # Update game at reduced speed
            if frame_count % self.current_speed == 0:
                self.update()
            
            self.draw()
            self.clock.tick(60)  # 60 FPS
            frame_count += 1
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    try:
        game = MathSnakeGame()
        game.run()
    except Exception as e:
        print(f"Error running game: {e}")
        print("Make sure you have pygame installed: pip install pygame")
        sys.exit(1)
