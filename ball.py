# Bouncing Ball Game

# Imports
import pygame # type: ignore
import sys
import random

# Initialize Pygame
pygame.init()

# Set Screen Dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball Game")

# Define Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

# Circle Variables
circle_center = (WIDTH // 2, HEIGHT // 2)
circle_radius = 250

# Game variables
balls = []
bounce_count = 0
speed_increase = 1.015 # Default, will be overridden by mode
game_mode = ""

# Game Modes
GAME_MODES = ["Classic", "Frenzy", "Rainbow", "Multi-ball"]

def create_ball(radius=20, pos=None, velocity=None):
    if pos is None:
        pos = [WIDTH // 2, HEIGHT // 2]
    if velocity is None:
        velocity = [random.choice([-5, 5]), random.choice([-5, 5])]
    return {
        'radius': radius,
        'pos': list(pos),
        'velocity': list(velocity),
        'color': random.choice(colors)
    }

def setup_game():
    global balls, bounce_count, speed_increase, game_mode

    # Select a game mode if one isn't already selected (for the first run)
    if not game_mode:
        game_mode = random.choice(GAME_MODES)

    # Reset variables
    balls = []
    bounce_count = 0

    # Mode-specific setup
    if game_mode == "Classic":
        speed_increase = 1.015
        balls.append(create_ball(velocity=[random.choice([-5, 5]), random.choice([-5, 5])]))
    elif game_mode == "Frenzy":
        speed_increase = 1.05
        balls.append(create_ball(velocity=[random.choice([-10, 10]), random.choice([-10, 10])]))
    elif game_mode == "Rainbow":
        speed_increase = 1.015
        balls.append(create_ball())
    elif game_mode == "Multi-ball":
        speed_increase = 1.015
        for _ in range(3):
            balls.append(create_ball(velocity=[random.uniform(-5, 5), random.uniform(-5, 5)]))

def reset_game():
    # Keep the same game mode for "Play Again"
    setup_game()

def display_end_screen():
    font = pygame.font.Font(None, 74)
    text = font.render("Play Again?", True, WHITE)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    yes_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 10, 80, 50)
    no_button = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 10, 80, 50)

    while True:
        screen.fill(BLACK)
        screen.blit(text, text_rect)
        pygame.draw.rect(screen, WHITE, yes_button)
        pygame.draw.rect(screen, WHITE, no_button)

        yes_text = pygame.font.Font(None, 50).render("Yes", True, BLACK)
        no_text = pygame.font.Font(None, 50).render("No", True, BLACK)
        screen.blit(yes_text, yes_text.get_rect(center=yes_button.center))
        screen.blit(no_text, no_text.get_rect(center=no_button.center))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if yes_button.collidepoint(event.pos):
                    reset_game()
                    return
                elif no_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

# Initial game setup
setup_game()

# Calculate Max Ball Radius
max_ball_radius = circle_radius - 10

# Loop The Game
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear Screen
    screen.fill(BLACK)

    # Draw Circle Perimeter
    pygame.draw.circle(screen, WHITE, circle_center, circle_radius, 2)

    # Rainbow mode color update
    if game_mode == "Rainbow":
        for ball in balls:
            ball['color'] = random.choice(colors)

    for ball in balls:
        # Ball Movement
        ball['pos'][0] += ball['velocity'][0]
        ball['pos'][1] += ball['velocity'][1]

        # Check for collision
        dist_x = ball['pos'][0] - circle_center[0]
        dist_y = ball['pos'][1] - circle_center[1]
        distance = (dist_x**2 + dist_y**2)**0.5

        if distance + ball['radius'] >= circle_radius:
            # Normalize Distance Vector
            normal = [dist_x / distance, dist_y / distance]

            # Calculate Dot Product
            velocity_dot_normal = ball['velocity'][0] * normal[0] + ball['velocity'][1] * normal[1]

            # Reflect Ball Velocity Vector
            ball['velocity'][0] -= 2 * velocity_dot_normal * normal[0]
            ball['velocity'][1] -= 2 * velocity_dot_normal * normal[1]

            # Add Small Random Perturbation
            ball['velocity'][0] += random.uniform(-1, 2)
            ball['velocity'][1] += random.uniform(-1, 2)

            # Increase The Speed Of The Ball
            ball['velocity'][0] *= speed_increase
            ball['velocity'][1] *= speed_increase

            # Increase Radius Of Ball
            if ball['radius'] < max_ball_radius:
                ball['radius'] += 1
                if game_mode != "Rainbow": # In rainbow mode color changes every frame
                    ball['color'] = random.choice(colors)

            # Set Position To Ensure Ball Stays In The Circle
            ball['pos'][0] = circle_center[0] + (circle_radius - ball['radius']) * normal[0]
            ball['pos'][1] = circle_center[1] + (circle_radius - ball['radius']) * normal[1]

            # Increment bounce count
            bounce_count += 1

        # Draw The Ball
        pygame.draw.circle(screen, ball['color'], ball['pos'], ball['radius'])

        # Check If Circle Has Been Filled
        if ball['radius'] >= max_ball_radius:
            display_end_screen()

    # Display Bounce Count and Game Mode
    font = pygame.font.Font(None, 36)
    bounce_text = font.render(f"Bounces: {bounce_count}", True, WHITE)
    screen.blit(bounce_text, (10, 10))
    mode_text = font.render(f"Mode: {game_mode}", True, WHITE)
    screen.blit(mode_text, (10, 40))


    # Update Display
    pygame.display.flip()

    # Set Frame Rate
    pygame.time.Clock().tick(60)

# Outside Main Loop
pygame.quit()
sys.exit()
