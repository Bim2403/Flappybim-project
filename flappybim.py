import pygame
import sys
import random

# --- 1. GAME CONFIGURATION ---
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (70, 130, 180)       # Steel Blue
BUTTON_HOVER = (100, 149, 237)      # Cornflower Blue
BUTTON_ACTIVE = (255, 140, 0)       # Dark Orange
TEXT_COLOR = (255, 255, 255)
COIN_COLOR = (255, 215, 0)          # Gold

# HITBOX CONFIGURATION
HITBOX_WIDTH = 25   # The width of the area that kills the bird (Fair size)
IMAGE_WIDTH = 250  # The width of the visible column picture (Visual size)
# offset calculates how much to shift the image left to center it on the hitbox
IMAGE_OFFSET_X = (IMAGE_WIDTH - HITBOX_WIDTH) // 2

# Difficulty Levels
DIFFICULTIES = {
    "EASY":   {"gap": 200, "speed": 3, "gravity": 0.3, "frequency": 1800},
    "NORMAL": {"gap": 150, "speed": 4, "gravity": 0.4, "frequency": 1500},
    "HARD":   {"gap": 115, "speed": 5, "gravity": 0.5, "frequency": 1000}
}

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bim - By Nam Khanh & Hien Anh")
clock = pygame.time.Clock()

# Fonts
font_title = pygame.font.Font(None, 60)
font_ui = pygame.font.Font(None, 40)
font_small = pygame.font.Font(None, 30)
font_supersmall = pygame.font.Font(None, 20)
# --- 2. GLOBAL VARIABLES ---
game_state = "MENU"
current_difficulty = "NORMAL"
score = 0        # Pipe Score
coin_score = 0   # Coin Score (New)
high_score = 0

# Physics Variables
bird_rect = None
bird_movement = 0
pipes = []
coins = []  # List to store coin rectangles
last_pipe_time = 0

# Background Variables
current_bg_index = 0
pipes_since_switch = 0

# --- 3. ASSET LOADING ---
def load_asset(filename, size, colorkey=None):
    """Helper function to load images safely."""
    try:
        img = pygame.image.load(filename).convert_alpha()
        if colorkey: img.set_colorkey(colorkey)
        return pygame.transform.scale(img, size)
    except (FileNotFoundError, pygame.error):
        # Fallback if file is missing
        fallback = pygame.Surface(size)
        fallback.fill((34, 139, 34)) # Green fallback
        return fallback

# Load Bird
try:
    bird_original = pygame.image.load("bim.png").convert_alpha()
except:
    try:
        bird_original = pygame.image.load("bim.jpg").convert()
        bird_original.set_colorkey((86, 186, 127))
    except:
        bird_original = pygame.Surface((50,50))
        bird_original.fill((255, 255, 0))

bird_img = pygame.transform.scale(bird_original, (50, 50))

# Load Backgrounds
bg_day = load_asset("hoguomsang.jpg", (SCREEN_WIDTH, SCREEN_HEIGHT))
bg_night = load_asset("hoguomtoi.jpeg", (SCREEN_WIDTH, SCREEN_HEIGHT))
backgrounds = [bg_day, bg_night]
column_original = load_asset("column.png", (IMAGE_WIDTH, SCREEN_HEIGHT))


column_original.set_colorkey((255, 255, 255)) 

# Create the Bottom Pipe (Normal)
pipe_img_bottom = column_original

# Create the Top Pipe (Flipped vertically)
pipe_img_top = pygame.transform.flip(column_original, False, True)

# Load Coin Image (Simple circle fallback if image not found)
try:
    coin_img_original = pygame.image.load("coin.png").convert_alpha()
    coin_img = pygame.transform.scale(coin_img_original, (30, 30))
except:
    coin_img = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(coin_img, COIN_COLOR, (15, 15), 15)
    pygame.draw.circle(coin_img, (218, 165, 32), (15, 15), 15, 2) # Darker border


# --- 4. BUTTON CLASS ---
class Button:
    def __init__(self, text, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.special_color = None

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            color = BUTTON_HOVER
        elif self.special_color:
            color = self.special_color
        else:
            color = BUTTON_COLOR
        
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        
        text_surf = font_small.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

# Buttons
btn_start = Button("START", 100, 300, 200, 45)
btn_diff  = Button("DIFFICULTY", 100, 355, 200, 45)
btn_quit  = Button("QUIT", 100, 410, 200, 45)
btn_retry = Button("RETRY", 100, 320, 200, 50)
btn_menu  = Button("MENU", 100, 380, 200, 50)

# --- 5. GAME FUNCTIONS ---
def reset_game():
    global bird_rect, bird_movement, pipes, coins, score, coin_score, current_bg_index, pipes_since_switch, last_pipe_time
    bird_rect = bird_img.get_rect(center=(100, SCREEN_HEIGHT // 2))
    bird_movement = 0
    pipes.clear()
    coins.clear()
    score = 0
    coin_score = 0 # Reset coin score
    last_pipe_time = pygame.time.get_ticks()
    current_bg_index = 0
    pipes_since_switch = 0

def draw_text_centered(text, font, y, color=WHITE):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(SCREEN_WIDTH // 2, y))
    screen.blit(surf, rect)

def draw_coin_score(surface, count):
    """Draws the coin score in the top-left corner."""
    score_surf = font_small.render(f"{count}", True, WHITE)
    # Draw icon
    surface.blit(coin_img, (10, 10))
    # Draw text next to icon
    surface.blit(score_surf, (45, 15))

# --- 6. MAIN GAME LOOP ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if game_state == "MENU":
            if btn_start.is_clicked(event):
                reset_game()
                game_state = "PLAYING"
            elif btn_diff.is_clicked(event):
                modes = list(DIFFICULTIES.keys())
                idx = (modes.index(current_difficulty) + 1) % len(modes)
                current_difficulty = modes[idx]
            elif btn_quit.is_clicked(event):
                running = False
        
        elif game_state == "PLAYING":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bird_movement = -7
        
        elif game_state == "GAMEOVER":
            if btn_retry.is_clicked(event):
                reset_game()
                game_state = "PLAYING"
            elif btn_menu.is_clicked(event):
                game_state = "MENU"

    # --- DRAWING & LOGIC ---
    bg_to_draw = backgrounds[0] if game_state == "MENU" else backgrounds[current_bg_index]
    screen.blit(bg_to_draw, (0, 0))

    if game_state == "MENU":
        draw_text_centered("FLAPPY BIM", font_title, 80, WHITE)
        draw_text_centered("By Hien Anh & Nam Khanh", font_supersmall, 160, )
        draw_text_centered(f"Mode: {current_difficulty}", font_small, 130, )
        screen.blit(bird_img, (SCREEN_WIDTH//2 - 25, 200))
        btn_start.draw(screen)
        btn_diff.draw(screen)
        btn_quit.draw(screen)

    elif game_state == "PLAYING":
        settings = DIFFICULTIES[current_difficulty]
        
        # 1. Physics
        bird_movement += settings['gravity']
        bird_rect.centery += bird_movement
        
        rotated_bird = pygame.transform.rotozoom(bird_img, -bird_movement * 3, 1)
        screen.blit(rotated_bird, bird_rect)
        
        # 2. Pipe and Coin Spawning
        current_time = pygame.time.get_ticks()
        if current_time - last_pipe_time > settings['frequency']:
            height = random.randint(200, 450)
            gap = settings['gap']
            
            # --- IMPORTANT: Collision Rect (Hitbox) ---
            btm_pipe = pygame.Rect(SCREEN_WIDTH, height, HITBOX_WIDTH, SCREEN_HEIGHT)
            top_pipe = pygame.Rect(SCREEN_WIDTH, height - gap - SCREEN_HEIGHT, HITBOX_WIDTH, SCREEN_HEIGHT)
            
            pipes.append(btm_pipe)
            pipes.append(top_pipe)

            # Spawn Coin (50% Chance)
            if random.choice([True, False]): 
                # Coin appears in the middle of the gap
                coin_y = height - (gap // 2) - 15 
                coin_rect = pygame.Rect(SCREEN_WIDTH + (HITBOX_WIDTH // 2) - 15, coin_y, 30, 30)
                coins.append(coin_rect)

            last_pipe_time = current_time

        # 3. Collision & Drawing
        for pipe in pipes:
            pipe.centerx -= settings['speed']
            
            # Draw visual pipes
            draw_x = pipe.x - IMAGE_OFFSET_X
            if pipe.top < 0:
                screen.blit(pipe_img_top, (draw_x, pipe.y))
            else:
                screen.blit(pipe_img_bottom, (draw_x, pipe.y))
            
            if bird_rect.colliderect(pipe):
                game_state = "GAMEOVER"
        
        # Coin Logic
        for coin in coins[:]: 
            coin.centerx -= settings['speed']
            screen.blit(coin_img, coin)
            
            if bird_rect.colliderect(coin):
                coin_score += 1 # Add to individual coin score
                coins.remove(coin)
            elif coin.right < 0:
                coins.remove(coin)

        # Remove off-screen pipes
        if pipes and pipes[0].right < 0:
            pipes.pop(0)
            pipes.pop(0)
            score += 1
            pipes_since_switch += 1
            if pipes_since_switch >= 5:
                pipes_since_switch = 0
                current_bg_index = 1 - current_bg_index

        if bird_rect.top <= 0 or bird_rect.bottom >= SCREEN_HEIGHT:
            game_state = "GAMEOVER"

        # Draw Scores
        draw_text_centered(str(score), font_title, 50)
        draw_coin_score(screen, coin_score)

        if score > high_score: high_score = score

    elif game_state == "GAMEOVER":
        for pipe in pipes:
            draw_x = pipe.x - IMAGE_OFFSET_X
            if pipe.top < 0:
                screen.blit(pipe_img_top, (draw_x, pipe.y))
            else:
                screen.blit(pipe_img_bottom, (draw_x, pipe.y))
        
        for coin in coins:
            screen.blit(coin_img, coin)
                
        screen.blit(rotated_bird, bird_rect)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(160)
        overlay.fill(BLACK)
        screen.blit(overlay, (0,0))
        
        draw_text_centered("GAME OVER", font_title, 130)
        draw_text_centered(f"Score: {score}", font_ui, 200)
        draw_text_centered(f"Best: {high_score}", font_small, 240)
        
        # Show Coin Score Summary
        draw_text_centered(f"Coins Collected: {coin_score}", font_small, 280, COIN_COLOR)

        btn_retry.draw(screen)
        btn_menu.draw(screen)

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
sys.exit()
