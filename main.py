import pygame
import random
import math
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
Screen_width = 1300
Screen_Height = 800
screen = pygame.display.set_mode((Screen_width, Screen_Height))

# Colors
WHITE = (255, 255, 255)
RED = (250, 0, 0)
GREEN = (0, 250, 0)
BLUE = (0, 0, 250)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
SILVER = (192, 192, 192)  # Silver color for player bullets
YELLOW = (255, 255, 0)  # Yellow color for coins

# Font setup
font = pygame.font.Font(None, 74)
game_over_text = font.render("Game Over!", True, WHITE)  # Changed to WHITE
exit_button_text = font.render("Exit", True, WHITE)  # Changed to WHITE
score_text_font = pygame.font.Font(None, 36)

# Position game over message and exit button
exit_button_rect = pygame.Rect(Screen_width // 2 - 100, Screen_Height // 2, 200, 60)

# Game variables
player_speed = 5
bullet_speed = 7
enemy_bullet_speed = 5
enemy_spawn_interval = 30
coin_spawn_interval = 300  # Increased interval to spawn coins less frequently
score = 0  # Initialize score
can_shoot = True  # Ensure one bullet per key press
high_score = 0  # Initialize high score

# File to store high score
high_score_file = "high_score.txt"

# Load high score from file if it exists
if os.path.exists(high_score_file):
    with open(high_score_file, "r") as file:
        high_score = int(file.read().strip())

# Load the "BloodMoon" background image
background_image = pygame.image.load("bloodmoon.jpg")
background_image = pygame.transform.scale(background_image, (Screen_width, Screen_Height))

# Function to reset game state
def reset_game():
    global player, bullets, enemies, enemy_bullets, player_alive, spawn_timer, score, can_shoot, coins
    player = pygame.Rect(Screen_width // 2 - 10, Screen_Height // 2 - 10, 20, 20)
    bullets = []
    enemies = []
    enemy_bullets = []
    coins = []  # Initialize coins list
    player_alive = True
    spawn_timer = 0
    score = 0  # Reset score on game start
    can_shoot = True  # Reset the shooting ability

# Initialize game state
reset_game()

# Game loop control
run = True
clock = pygame.time.Clock()

# Player rotation surface setup
player_image = pygame.Surface((20, 20))
player_image.fill(BLUE)  # Changed to BLUE
player_rect = player_image.get_rect()

# Function to spawn coins
def spawn_coin():
    while True:
        coin_x = random.randint(0, Screen_width - 15)  # Coin width adjusted to 15
        coin_y = random.randint(0, Screen_Height - 15)  # Coin height adjusted to 15
        coin_rect = pygame.Rect(coin_x, coin_y, 15, 15)  # Coin size changed to 15x15
        
        # Ensure coin doesn't spawn on player or enemies
        if not player.colliderect(coin_rect) and not any(enemy.colliderect(coin_rect) for enemy in enemies):
            return coin_rect

# Game loop
while run:
    # Fill the screen with the "BloodMoon" background
    screen.blit(background_image, (0, 0))

    # Draw player if alive
    if player_alive:
        # Find the nearest enemy
        nearest_enemy = min(enemies, key=lambda e: math.hypot(player.centerx - e.centerx, player.centery - e.centery)) if enemies else None

        if nearest_enemy:
            # Calculate angle to the nearest enemy
            dx = nearest_enemy.centerx - player.centerx
            dy = nearest_enemy.centery - player.centery
            angle = math.atan2(dy, dx)

            # Rotate the player image to face the enemy
            rotated_player_image = pygame.transform.rotate(player_image, -math.degrees(angle))
            rotated_rect = rotated_player_image.get_rect(center=player.center)
            screen.blit(rotated_player_image, rotated_rect.topleft)
        else:
            # If no enemy, just draw player
            screen.blit(player_image, player.topleft)

        # Display score
        score_text = score_text_font.render(f"Score: {score}", True, WHITE)  # Changed to WHITE
        screen.blit(score_text, (10, 10))

        # Handle movement with border limitations
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.left > 0:
            player.move_ip(-player_speed, 0)
        if keys[pygame.K_d] and player.right < Screen_width:
            player.move_ip(player_speed, 0)
        if keys[pygame.K_w] and player.top > 0:
            player.move_ip(0, -player_speed)
        if keys[pygame.K_s] and player.bottom < Screen_Height:
            player.move_ip(0, player_speed)

        # Fire bullets toward the nearest enemy, limit to one per key press
        if keys[pygame.K_SPACE] and enemies and can_shoot:
            can_shoot = False  # Disable shooting until space is released
            # Find the closest enemy
            nearest_enemy = min(enemies, key=lambda e: math.hypot(player.centerx - e.centerx, player.centery - e.centery))
            dx = nearest_enemy.centerx - player.centerx
            dy = nearest_enemy.centery - player.centery
            angle = math.atan2(dy, dx)
            bullet = {
                "rect": pygame.Rect(player.centerx, player.centery, 5, 5),
                "dx": math.cos(angle) * bullet_speed,
                "dy": math.sin(angle) * bullet_speed
            }
            bullets.append(bullet)

    # Update player bullets
    for bullet in bullets[:]:
        bullet["rect"].move_ip(bullet["dx"], bullet["dy"])
        if not screen.get_rect().colliderect(bullet["rect"]):  # Remove bullet if it goes off-screen
            bullets.remove(bullet)
        else:
            pygame.draw.rect(screen, SILVER, bullet["rect"])  # Player bullets in silver

    # Spawn stationary enemies within screen boundaries
    spawn_timer += 1
    if spawn_timer > enemy_spawn_interval:
        enemy_x = random.randint(0, Screen_width - 20)
        enemy_y = random.randint(0, Screen_Height // 2 - 20)  # Upper half of the screen
        enemy = pygame.Rect(enemy_x, enemy_y, 20, 20)
        enemies.append(enemy)
        spawn_timer = 0

    # Enemies shoot bullets toward player
    for enemy in enemies:
        pygame.draw.rect(screen, GREEN, enemy)

        # Enemy shoots bullets at the player periodically
        if random.randint(0, 60) == 0:  # Adjust frequency
            dx = player.centerx - enemy.centerx
            dy = player.centery - enemy.centery
            angle = math.atan2(dy, dx)
            enemy_bullet = {
                "rect": pygame.Rect(enemy.centerx, enemy.centery, 5, 5),
                "dx": math.cos(angle) * enemy_bullet_speed,
                "dy": math.sin(angle) * enemy_bullet_speed
            }
            enemy_bullets.append(enemy_bullet)

    # Update enemy bullets
    for bullet in enemy_bullets[:]:
        bullet["rect"].move_ip(bullet["dx"], bullet["dy"])
        if not screen.get_rect().colliderect(bullet["rect"]):
            enemy_bullets.remove(bullet)
        else:
            pygame.draw.rect(screen, WHITE, bullet["rect"])  # Enemy bullets in white

        # Check if enemy bullet hits player
        if player_alive and bullet["rect"].colliderect(player):
            player_alive = False  # Player dies if hit by enemy bullet
            break

    # Check for collisions between player bullets and enemies
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if bullet["rect"].colliderect(enemy):
                bullets.remove(bullet)
                enemies.remove(enemy)
                score += 100  # Increase score by 100 for each enemy killed
                break

    # Check for collisions between player and enemies
    if player_alive:
        for enemy in enemies:
            if player.colliderect(enemy):
                player_alive = False
                break

    # Spawn coins periodically
    if random.randint(0, coin_spawn_interval) == 0:
        coin_rect = spawn_coin()
        coins.append(coin_rect)

    # Check for player collecting coins
    for coin in coins[:]:
        if player.colliderect(coin):
            coins.remove(coin)  # Remove the coin
            score += 50  # Add 50 to score for collecting a coin
        pygame.draw.rect(screen, YELLOW, coin)  # Draw the coin (yellow)

    # Display "Game Over", score, and Exit button if the player is dead
    if not player_alive:
        # Position "Game Over" text at the top center
        screen.blit(game_over_text, (Screen_width // 2 - game_over_text.get_width() // 2, 50))
        
        # Display final score
        final_score_text = score_text_font.render(f"Score: {score}", True, WHITE)  # Changed to WHITE
        screen.blit(final_score_text, (Screen_width // 2 - final_score_text.get_width() // 2, 150))

        # Display High Score
        high_score_text = score_text_font.render(f"High Score: {high_score}", True, WHITE)  # Changed to WHITE
        screen.blit(high_score_text, (Screen_width // 2 - high_score_text.get_width() // 2, 200))

        # Draw the "Exit" button in the center
        pygame.draw.rect(screen, GRAY, exit_button_rect)
        screen.blit(exit_button_text, (exit_button_rect.x + 50, exit_button_rect.y + 10))

        # Check if the current score is higher than the high score and update if necessary
        if score > high_score:
            high_score = score
            with open(high_score_file, "w") as file:
                file.write(str(high_score))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif not player_alive:
            if event.type == pygame.KEYDOWN:
                reset_game()  # Restart the game on any key press
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button_rect.collidepoint(event.pos):
                    run = False  # Exit the game if the "Exit" button is clicked

        # Release spacebar to allow next shot
        if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            can_shoot = True  # Allow the player to shoot again

    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
