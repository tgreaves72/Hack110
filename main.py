import pygame
import random
import math
import os
import sys

pygame.init()

Screen_width = 1300
Screen_Height = 800
screen = pygame.display.set_mode((Screen_width, Screen_Height))

WHITE = (255, 255, 255)
RED = (250, 0, 0)
GREEN = (0, 250, 0)
BLUE = (0, 0, 250)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
SILVER = (192, 192, 192)
YELLOW = (255, 255, 0)

font = pygame.font.Font(None, 74)
game_over_text = font.render("Game Over!", True, WHITE)
exit_button_text = font.render("Exit", True, WHITE)
score_text_font = pygame.font.Font(None, 36)

exit_button_rect = pygame.Rect(Screen_width // 2 - 100, Screen_Height // 2, 200, 60)

player_speed = 5
bullet_speed = 7
enemy_bullet_speed = 5
enemy_spawn_interval = 30
coin_spawn_interval = 300
score = 0
can_shoot = True
high_score = 0

high_score_file = "high_score.txt"

if os.path.exists(high_score_file):
    with open(high_score_file, "r") as file:
        high_score = int(file.read().strip())

background_image = pygame.image.load("bloodmoon.jpg")
background_image = pygame.transform.scale(background_image, (Screen_width, Screen_Height))

title_font = pygame.font.Font(None, 120)
button_font = pygame.font.Font(None, 50)

title_text = title_font.render("Blood Moon", True, RED)
button_text = button_font.render("Press to Start", True, BLACK)

button_rect = pygame.Rect(Screen_width // 2 - 150, Screen_Height // 2 + 100, 300, 60)

def start_screen():
    while True:
        screen.fill(BLACK)
        screen.blit(title_text, (Screen_width // 2 - title_text.get_width() // 2, 200))
        pygame.draw.rect(screen, GRAY, button_rect)
        screen.blit(button_text, (button_rect.x + 20, button_rect.y + 15))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return
        pygame.display.flip()

def reset_game():
    global player, bullets, enemies, enemy_bullets, player_alive, spawn_timer, score, can_shoot, coins
    player = pygame.Rect(Screen_width // 2 - 10, Screen_Height // 2 - 10, 20, 20)
    bullets = []
    enemies = []
    enemy_bullets = []
    coins = []
    player_alive = True
    spawn_timer = 0
    score = 0
    can_shoot = True

reset_game()

run = True
clock = pygame.time.Clock()

player_image = pygame.Surface((20, 20))
player_image.fill(BLUE)
player_rect = player_image.get_rect()

def spawn_coin():
    while True:
        coin_x = random.randint(0, Screen_width - 15)
        coin_y = random.randint(0, Screen_Height - 15)
        coin_rect = pygame.Rect(coin_x, coin_y, 15, 15)
        if not player.colliderect(coin_rect) and not any(enemy.colliderect(coin_rect) for enemy in enemies):
            return coin_rect

start_screen()

while run:
    screen.blit(background_image, (0, 0))

    if player_alive:
        nearest_enemy = min(enemies, key=lambda e: math.hypot(player.centerx - e.centerx, player.centery - e.centery)) if enemies else None
        if nearest_enemy:
            dx = nearest_enemy.centerx - player.centerx
            dy = nearest_enemy.centery - player.centery
            angle = math.atan2(dy, dx)
            rotated_player_image = pygame.transform.rotate(player_image, -math.degrees(angle))
            rotated_rect = rotated_player_image.get_rect(center=player.center)
            screen.blit(rotated_player_image, rotated_rect.topleft)
        else:
            screen.blit(player_image, player.topleft)

        score_text = score_text_font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.left > 0:
            player.move_ip(-player_speed, 0)
        if keys[pygame.K_d] and player.right < Screen_width:
            player.move_ip(player_speed, 0)
        if keys[pygame.K_w] and player.top > 0:
            player.move_ip(0, -player_speed)
        if keys[pygame.K_s] and player.bottom < Screen_Height:
            player.move_ip(0, player_speed)

        if keys[pygame.K_SPACE] and enemies and can_shoot:
            can_shoot = False
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

    for bullet in bullets[:]:
        bullet["rect"].move_ip(bullet["dx"], bullet["dy"])
        if not screen.get_rect().colliderect(bullet["rect"]):
            bullets.remove(bullet)
        else:
            pygame.draw.rect(screen, SILVER, bullet["rect"])

    spawn_timer += 1
    if spawn_timer > enemy_spawn_interval:
        enemy_x = random.randint(0, Screen_width - 20)
        enemy_y = random.randint(0, Screen_Height // 2 - 20)
        enemy = pygame.Rect(enemy_x, enemy_y, 20, 20)
        enemies.append(enemy)
        spawn_timer = 0

    for enemy in enemies:
        pygame.draw.rect(screen, GREEN, enemy)
        if random.randint(0, 60) == 0:
            dx = player.centerx - enemy.centerx
            dy = player.centery - enemy.centery
            angle = math.atan2(dy, dx)
            enemy_bullet = {
                "rect": pygame.Rect(enemy.centerx, enemy.centery, 5, 5),
                "dx": math.cos(angle) * enemy_bullet_speed,
                "dy": math.sin(angle) * enemy_bullet_speed
            }
            enemy_bullets.append(enemy_bullet)

    for bullet in enemy_bullets[:]:
        bullet["rect"].move_ip(bullet["dx"], bullet["dy"])
        if not screen.get_rect().colliderect(bullet["rect"]):
            enemy_bullets.remove(bullet)
        else:
            pygame.draw.rect(screen, WHITE, bullet["rect"])
        if player_alive and bullet["rect"].colliderect(player):
            player_alive = False
            break

    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if bullet["rect"].colliderect(enemy):
                bullets.remove(bullet)
                enemies.remove(enemy)
                score += 100
                break

    if player_alive:
        for enemy in enemies:
            if player.colliderect(enemy):
                player_alive = False
                break

    if random.randint(0, coin_spawn_interval) == 0:
        coin_rect = spawn_coin()
        coins.append(coin_rect)

    for coin in coins[:]:
        if player.colliderect(coin):
            coins.remove(coin)
            score += 50
        pygame.draw.rect(screen, YELLOW, coin)

    if not player_alive:
        screen.blit(game_over_text, (Screen_width // 2 - game_over_text.get_width() // 2, 50))
        final_score_text = score_text_font.render(f"Score: {score}", True, WHITE)
        screen.blit(final_score_text, (Screen_width // 2 - final_score_text.get_width() // 2, 150))
        high_score_text = score_text_font.render(f"High Score: {high_score}", True, WHITE)
        screen.blit(high_score_text, (Screen_width // 2 - high_score_text.get_width() // 2, 200))
        pygame.draw.rect(screen, GRAY, exit_button_rect)
        screen.blit(exit_button_text, (exit_button_rect.x + 50, exit_button_rect.y + 10))

        if score > high_score:
            high_score = score
            with open(high_score_file, "w") as file:
                file.write(str(high_score))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif not player_alive:
            if event.type == pygame.KEYDOWN:
                reset_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button_rect.collidepoint(event.pos):
                    run = False

        if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            can_shoot = True

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
