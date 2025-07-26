import pygame
import sys
import random

# --- Helper Function for Restart Prompt ---
def prompt_restart():
    """Prompts the user in the console to restart or quit."""
    while True:
        choice = input("\nGame Over! Play again? (y/n): ").strip().lower()
        if choice == 'y':
            return True  # Restart
        elif choice == 'n':
            return False # Quit
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

# --- Game Initialization ---
pygame.init()
pygame.display.set_caption("Atari Pong")
screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 74)
small_font = pygame.font.SysFont(None, 36) # For game over message

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Paddle & Ball properties
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 60
BALL_SIZE = 10
PADDLE_SPEED = 5
BALL_SPEED_X, BALL_SPEED_Y = 4, 4
FPS = 60
WINNING_SCORE = 5 # First to 5 points wins

# Simple sound placeholders (beep for hit, oops for miss)
# Using pygame's sound array capabilities for zero external files
try:
    import numpy as np
    def create_beep(frequency=440, duration=0.1, sample_rate=22050):
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2)) # Stereo
        for i in range(frames):
            wave = 4096 * np.sin(2 * np.pi * frequency * i / sample_rate) # Amplitude
            arr[i][0] = wave # Left channel
            arr[i][1] = wave # Right channel
        sound = pygame.sndarray.make_sound(arr.astype(np.int16))
        return sound
    BEEP_SOUND = create_beep(440, 0.1) # Higher pitch beep
    OOPS_SOUND = create_beep(220, 0.3) # Lower pitch, longer "oops"
    SOUND_AVAILABLE = True
except ImportError:
    print("Warning: Numpy not found. Sound effects disabled.")
    SOUND_AVAILABLE = False
    BEEP_SOUND = None
    OOPS_SOUND = None

# --- Game Reset Function ---
def reset_game():
    """Resets game state to initial values."""
    global player_paddle, opponent_paddle, ball, ball_speed_x, ball_speed_y
    global player_score, opponent_score, game_over, winner_text

    player_paddle = pygame.Rect(20, 240 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    opponent_paddle = pygame.Rect(640 - 20 - PADDLE_WIDTH, 240 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(320 - BALL_SIZE//2, 240 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)
    ball_speed_x = BALL_SPEED_X * random.choice((1, -1))
    ball_speed_y = BALL_SPEED_Y * random.choice((1, -1))
    player_score = 0
    opponent_score = 0
    game_over = False
    winner_text = None

# Initialize game objects and state
reset_game()

# --- Main Game Loop ---
running = True
while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
        # --- Player Input (only if game is active) ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            player_paddle.y -= PADDLE_SPEED
        if keys[pygame.K_DOWN]:
            player_paddle.y += PADDLE_SPEED

        # --- Keep player paddle on screen ---
        player_paddle.y = max(0, min(player_paddle.y, 480 - PADDLE_HEIGHT))

        # --- Simple AI for opponent paddle ---
        if opponent_paddle.centery < ball.centery:
            opponent_paddle.y += PADDLE_SPEED
        if opponent_paddle.centery > ball.centery:
            opponent_paddle.y -= PADDLE_SPEED
        opponent_paddle.y = max(0, min(opponent_paddle.y, 480 - PADDLE_HEIGHT))

        # --- Move the ball ---
        ball.x += ball_speed_x
        ball.y += ball_speed_y

        # --- Ball collision with top/bottom walls ---
        if ball.top <= 0 or ball.bottom >= 480:
            ball_speed_y *= -1
            if SOUND_AVAILABLE and pygame.mixer.get_init():
                BEEP_SOUND.play() # Atari wall hit beep

        # --- Ball collision with paddles ---
        # Check for collision and ensure the ball is moving towards the paddle
        if ball.colliderect(player_paddle) and ball_speed_x < 0:
            ball_speed_x *= -1
            if SOUND_AVAILABLE and pygame.mixer.get_init():
                BEEP_SOUND.play() # Paddle hit beep
        if ball.colliderect(opponent_paddle) and ball_speed_x > 0:
            ball_speed_x *= -1
            if SOUND_AVAILABLE and pygame.mixer.get_init():
                BEEP_SOUND.play() # Paddle hit beep

        # --- Scoring ---
        if ball.left <= 0:
            opponent_score += 1
            if SOUND_AVAILABLE and pygame.mixer.get_init():
                OOPS_SOUND.play() # Player missed ("oops")
            # Check for win condition
            if opponent_score >= WINNING_SCORE:
                game_over = True
                winner_text = "OPPONENT WINS!"
            else:
                # Reset ball
                ball.center = (320, 240)
                ball_speed_x = BALL_SPEED_X * random.choice((1, -1))
                ball_speed_y = BALL_SPEED_Y * random.choice((1, -1))

        if ball.right >= 640:
            player_score += 1
            if SOUND_AVAILABLE and pygame.mixer.get_init():
                OOPS_SOUND.play() # Opponent missed ("oops")
            # Check for win condition
            if player_score >= WINNING_SCORE:
                game_over = True
                winner_text = "PLAYER WINS!"
            else:
                # Reset ball
                ball.center = (320, 240)
                ball_speed_x = BALL_SPEED_X * random.choice((1, -1))
                ball_speed_y = BALL_SPEED_Y * random.choice((1, -1))

    # --- Drawing ---
    screen.fill(BLACK)
    if not game_over:
        pygame.draw.rect(screen, WHITE, player_paddle)
        pygame.draw.rect(screen, WHITE, opponent_paddle)
        pygame.draw.ellipse(screen, WHITE, ball)
    pygame.draw.aaline(screen, WHITE, (320, 0), (320, 480))

    # Draw scores
    player_text = font.render(str(player_score), True, WHITE)
    opponent_text = font.render(str(opponent_score), True, WHITE)
    screen.blit(player_text, (250, 10))
    screen.blit(opponent_text, (370, 10))

    # Draw Game Over message
    if game_over and winner_text:
        win_text_surface = font.render(winner_text, True, WHITE)
        text_rect = win_text_surface.get_rect(center=(320, 200))
        screen.blit(win_text_surface, text_rect)
        
        restart_text_surface = small_font.render("Check console to restart (y/n)", True, WHITE)
        restart_rect = restart_text_surface.get_rect(center=(320, 250))
        screen.blit(restart_text_surface, restart_rect)
        
        pygame.display.flip()
        clock.tick(FPS) # Still tick to update display
        
        # Prompt for restart
        if prompt_restart():
            reset_game()
            # Clear the event queue to prevent key presses from the menu from affecting the new game
            pygame.event.clear() 
        else:
            running = False # Quit the game loop

    if not game_over:
        pygame.display.flip()
        clock.tick(FPS) # Maintain 60 FPS

pygame.quit()
sys.exit()
