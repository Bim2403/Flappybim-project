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
SKY_BLUE = (135, 206, 235)
PIPE_GREEN = (34, 139, 34)
BUTTON_COLOR = (70, 130, 180)       # Steel Blue
BUTTON_HOVER = (100, 149, 237)      # Cornflower Blue
TEXT_COLOR = (255, 255, 255)

# Difficulty Levels
DIFFICULTIES = {
    "EASY":   {"gap": 200, "speed": 3, "gravity": 0.15, "frequency": 1800},
    "NORMAL": {"gap": 150, "speed": 4, "gravity": 0.25, "frequency": 1500},
    "HARD":   {"gap": 120, "speed": 5, "gravity": 0.40, "frequency": 1000}
}

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bim")
clock = pygame.time.Clock()

# Fonts
font_title = pygame.font.Font(None, 60)
font_ui = pygame.font.Font(None, 40)
font_small = pygame.font.Font(None, 30)
font_supersmall = pygame.font.Font(None, 20)

# --- 2. GLOBAL VARIABLES ---
game_state = "MENU"         # Options: MENU, PLAYING, GAMEOVER
current_difficulty = "NORMAL"
score = 0
high_score = 0

# Physics Variables
bird_rect = None
bird_movement = 0
pipes = []
last_pipe_time = 0

# Background Variables
current_bg_index = 0        # 0 = Day, 1 = Night
pipes_since_switch = 0      # Counts how many pipes passed to trigger switch

# --- 3. ASSET LOADING ---
def load_asset(filename, size, colorkey=None):
    """Helper function to load images safely."""
    try:
        img = pygame.image.load(filename).convert_alpha()
        if colorkey: img.set_colorkey(colorkey)
        return pygame.transform.scale(img, size)
    except (FileNotFoundError, pygame.error):
        print(f"Missing file: {filename}. Creating fallback square.")
        fallback = pygame.Surface(size)
        fallback.fill((200, 50, 50)) # Red square if file missing
        return fallback

# Load Bird (Try png first, then jpg)
try:
    bird_original = pygame.image.load("bim.png").convert_alpha()
except:
    try:
        bird_original = pygame.image.load("bim.jpg").convert()
        bird_original.set_colorkey((86, 186, 127)) # Attempt to remove green background
    except:
        bird_original = pygame.Surface((50,50))
        bird_original.fill((255, 255, 0))

bird_img = pygame.transform.scale(bird_original, (50, 50))

# Load Backgrounds
bg_day = load_asset("hoguomsang.jpg", (SCREEN_WIDTH, SCREEN_HEIGHT))
bg_night = load_asset("hoguomtoi.jpeg", (SCREEN_WIDTH, SCREEN_HEIGHT))
backgrounds = [bg_day, bg_night] # List to easily swap them

# --- 4. BUTTON CLASS ---
class Button:
    def __init__(self, text, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self, surface):
        # Change color if mouse is hovering
        mouse_pos = pygame.mouse.get_pos()
        color = BUTTON_HOVER if self.rect.collidepoint(mouse_pos) else BUTTON_COLOR
        
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        
        text_surf = font_small.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

# Create Buttons
btn_start = Button("START", 100, 300, 200, 50)
btn_diff  = Button("DIFFICULTY", 100, 360, 200, 50)
btn_quit  = Button("QUIT", 100, 420, 200, 50)
btn_retry = Button("RETRY", 100, 320, 200, 50)
btn_menu  = Button("MENU", 100, 380, 200, 50)

# --- 5. GAME FUNCTIONS ---
def reset_game():
    global bird_rect, bird_movement, pipes, score, current_bg_index, pipes_since_switch, last_pipe_time
    
    bird_rect = bird_img.get_rect(center=(100, SCREEN_HEIGHT // 2))
    bird_movement = 0
    pipes.clear()
    score = 0
    last_pipe_time = pygame.time.get_ticks()
    
    # Reset Cycle
    current_bg_index = 0 # Start with Day
    pipes_since_switch = 0

def draw_text_centered(text, font, y, color=WHITE):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(SCREEN_WIDTH // 2, y))
    screen.blit(surf, rect)

# --- 6. MAIN GAME LOOP ---
running = True
while running:
    
    # --- EVENT HANDLING ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # Menu Controls
        if game_state == "MENU":
            if btn_start.is_clicked(event):
                reset_game()
                game_state = "PLAYING"
            elif btn_diff.is_clicked(event):
                # Cycle difficulty
                modes = list(DIFFICULTIES.keys())
                idx = (modes.index(current_difficulty) + 1) % len(modes)
                current_difficulty = modes[idx]
            elif btn_quit.is_clicked(event):
                running = False
        
        # Playing Controls
        elif game_state == "PLAYING":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bird_movement = -7 # Jump strength
                
        # Game Over Controls
        elif game_state == "GAMEOVER":
            if btn_retry.is_clicked(event):
                reset_game()
                game_state = "PLAYING"
            elif btn_menu.is_clicked(event):
                game_state = "MENU"

    # --- DRAWING & LOGIC ---
    
    # Draw Background (Always visible)
    # If in menu, force Day background (index 0). If playing, use current cycle.
    bg_to_draw = backgrounds[0] if game_state == "MENU" else backgrounds[current_bg_index]
    screen.blit(bg_to_draw, (0, 0))

    if game_state == "MENU":
        # Title Screen
        draw_text_centered("FLAPPY BIM", font_title, 100)
        draw_text_centered("By Hien Anh & Nam Khanh", font_supersmall, 180)
        draw_text_centered(f"Mode: {current_difficulty}", font_small, 140)
        
        # Show Bim floating
        screen.blit(bird_img, (SCREEN_WIDTH//2 - 25, 220))
        
        # Draw Buttons
        btn_start.draw(screen)
        btn_diff.draw(screen)
        btn_quit.draw(screen)

    elif game_state == "PLAYING":
        settings = DIFFICULTIES[current_difficulty]
        
        # 1. Bird Physics
        bird_movement += settings['gravity']
        bird_rect.centery += bird_movement
        
        # Rotate bird for effect
        rotated_bird = pygame.transform.rotozoom(bird_img, -bird_movement * 3, 1)
        screen.blit(rotated_bird, bird_rect)
        
        # 2. Pipe Spawning
        current_time = pygame.time.get_ticks()
        if current_time - last_pipe_time > settings['frequency']:
            height = random.randint(200, 450)
            gap = settings['gap']
            
            btm_pipe = pygame.Rect(SCREEN_WIDTH, height, 50, SCREEN_HEIGHT)
            top_pipe = pygame.Rect(SCREEN_WIDTH, height - gap - SCREEN_HEIGHT, 50, SCREEN_HEIGHT)
            
            pipes.append(btm_pipe)
            pipes.append(top_pipe)
            last_pipe_time = current_time

        # 3. Pipe Movement & Collision
        for pipe in pipes:
            pipe.centerx -= settings['speed']
            pygame.draw.rect(screen, PIPE_GREEN, pipe)
            
            if bird_rect.colliderect(pipe):
                game_state = "GAMEOVER"
        
        # 4. Score & Background Switching
        if pipes and pipes[0].right < 0:
            pipes.pop(0)
            pipes.pop(0) # Remove pair
            score += 1
            pipes_since_switch += 1
            
            # CHECK: Switch background every 5 points
            if pipes_since_switch >= 5:
                pipes_since_switch = 0
                current_bg_index = 1 - current_bg_index # Flips 0->1 or 1->0

        # 5. Floor/Ceiling Death
        if bird_rect.top <= 0 or bird_rect.bottom >= SCREEN_HEIGHT:
            game_state = "GAMEOVER"

        # Draw Score
        draw_text_centered(str(score), font_title, 50)
        
        # Update High Score
        if score > high_score: high_score = score

    elif game_state == "GAMEOVER":
        # Draw pipes and bird frozen in background
        for pipe in pipes:
            pygame.draw.rect(screen, PIPE_GREEN, pipe)
        screen.blit(rotated_bird, bird_rect)
        
        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(160)
        overlay.fill(BLACK)
        screen.blit(overlay, (0,0))
        
        draw_text_centered("GAME OVER", font_title, 150)
        draw_text_centered(f"Score: {score}", font_ui, 220)
        draw_text_centered(f"Best: {high_score}", font_small, 260)
        
        btn_retry.draw(screen)
        btn_menu.draw(screen)

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
sys.exit()