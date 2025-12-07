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
score = 0
high_score = 0
autopilot = False

# Physics Variables
bird_rect = None
bird_movement = 0
pipes = []
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
btn_auto  = Button("AUTO: OFF", 100, 410, 200, 45)
btn_quit  = Button("QUIT", 100, 465, 200, 45)
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
    current_bg_index = 0
    pipes_since_switch = 0

def draw_text_centered(text, font, y, color=WHITE):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(SCREEN_WIDTH // 2, y))
    screen.blit(surf, rect)

# --- AI SIMULATION FUNCTION ---
def get_best_move(bird_rect, bird_movement, pipes, settings):
    # 1. Identify Target Pipe
    target_pipe = None
    closest_x = 9999
    target_y = SCREEN_HEIGHT // 2
    
    for pipe in pipes:
        if pipe.right > bird_rect.left and pipe.top > 0: # Find bottom pipe
            if pipe.left < closest_x:
                closest_x = pipe.left
                target_pipe = pipe

    if target_pipe:
        gap_center = target_pipe.top - (settings['gap'] / 2)
        target_y = gap_center

    # 2. Simulation Physics
    def simulate(start_y, start_vel, action_jump):
        sim_y = start_y
        sim_vel = start_vel
        sim_rect = pygame.Rect(bird_rect.x, 0, bird_rect.width, bird_rect.height)
        
        if action_jump: sim_vel = -7
        
        for i in range(40):
            sim_vel += settings['gravity']
            sim_y += sim_vel
            sim_rect.y = int(sim_y)
            
            if sim_rect.top <= 0 or sim_rect.bottom >= SCREEN_HEIGHT:
                return False, 9999
            
            current_pipe_offset = i * settings['speed']
            for p in pipes:
                p_shifted = p.copy()
                p_shifted.x -= current_pipe_offset
                if sim_rect.colliderect(p_shifted):
                    return False, 9999
        
        dist = abs(sim_y - target_y)
        return True, dist

    # 3. Evaluate Options
    alive_glide, score_glide = simulate(bird_rect.y, bird_movement, False)
    alive_jump, score_jump = simulate(bird_rect.y, bird_movement, True)
    
    if alive_glide and not alive_jump: return False
    elif alive_jump and not alive_glide: return True
    elif alive_jump and alive_glide:
        if score_jump < score_glide - 5: return True
        return False
    else: return True

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
            elif btn_auto.is_clicked(event):
                autopilot = not autopilot
                if autopilot:
                    btn_auto.text = "AUTO: ON"
                    btn_auto.special_color = BUTTON_ACTIVE
                else:
                    btn_auto.text = "AUTO: OFF"
                    btn_auto.special_color = None
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
        btn_auto.draw(screen)
        btn_quit.draw(screen)

    elif game_state == "PLAYING":
        settings = DIFFICULTIES[current_difficulty]
        
        # --- AUTOPILOT LOGIC ---
        if autopilot:
            should_jump = get_best_move(bird_rect, bird_movement, pipes, settings)
            if should_jump:
                bird_movement = -7

        # 1. Physics
        bird_movement += settings['gravity']
        bird_rect.centery += bird_movement
        
        rotated_bird = pygame.transform.rotozoom(bird_img, -bird_movement * 3, 1)
        screen.blit(rotated_bird, bird_rect)
        
        # 2. Pipe Spawning
        current_time = pygame.time.get_ticks()
        if current_time - last_pipe_time > settings['frequency']:
            height = random.randint(200, 450)
            gap = settings['gap']
            
            # --- IMPORTANT: Collision Rect (Hitbox) ---
            # We use HITBOX_WIDTH (50px) for the logic so it's fair.
            btm_pipe = pygame.Rect(SCREEN_WIDTH, height, HITBOX_WIDTH, SCREEN_HEIGHT)
            top_pipe = pygame.Rect(SCREEN_WIDTH, height - gap - SCREEN_HEIGHT, HITBOX_WIDTH, SCREEN_HEIGHT)
            
            pipes.append(btm_pipe)
            pipes.append(top_pipe)
            last_pipe_time = current_time

        # 3. Collision & Drawing
        for pipe in pipes:
            pipe.centerx -= settings['speed']
            
            # --- VISUAL DRAWING FIX ---
            # Calculate the centered position for the image relative to the hitbox
            draw_x = pipe.x - IMAGE_OFFSET_X
            
            if pipe.top < 0:
                # Top pipe
                screen.blit(pipe_img_top, (draw_x, pipe.y))
            else:
                # Bottom pipe
                screen.blit(pipe_img_bottom, (draw_x, pipe.y))
            
            # Debug: Uncomment below to see the Red Hitbox vs The Image
            # pygame.draw.rect(screen, (255, 0, 0), pipe, 1)
            
            if bird_rect.colliderect(pipe):
                game_state = "GAMEOVER"
        
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

        draw_text_centered(str(score), font_title, 50)
        if autopilot:
            draw_text_centered("AUTO AI", font_supersmall, 85, (255, 165, 0))

        if score > high_score: high_score = score

    elif game_state == "GAMEOVER":
        for pipe in pipes:
            draw_x = pipe.x - IMAGE_OFFSET_X
            if pipe.top < 0:
                screen.blit(pipe_img_top, (draw_x, pipe.y))
            else:
                screen.blit(pipe_img_bottom, (draw_x, pipe.y))
                
        screen.blit(rotated_bird, bird_rect)
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
