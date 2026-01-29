# Import necessary libraries.
import pygame, sys, math, time, random, os
from pygame.locals import *

pygame.init()

# Window setup.
window_width = 1200
window_height = 700
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('Ghost Rush')
clock = pygame.time.Clock()
FPS = 60

# Screens Setup.
game_window = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
instructions = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
levels_screen = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
game_over_screen = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
home_screen = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
choose_leaderboard_screen = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
leaderboard = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
choose_name_screen = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
blur_background_screen = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
level_text_screen = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
paused_game_screen = pygame.Surface((window_width, window_height), pygame.SRCALPHA)

# Set up colors.
black = (0, 0, 0)
white = (255, 255, 255)
dark_gray = (50, 50, 50)
light_gray = (200, 200, 200)
blue = (0, 0, 255)
transparent = (0, 0, 0, 0)
gold = (212, 175, 55)

# Set up character (player and ghost) images.
player_standing = pygame.transform.scale(pygame.image.load('character_standing.png'), (50, 113)).convert_alpha()
# Left
player_standing_left = player_standing
# Right (flipped left)
player_standing_right = pygame.transform.flip(player_standing, True, False)

# Repeat with most of the other images.
player_walking_1 = pygame.transform.scale(pygame.image.load('character_walking_1.png'), (50, 113)).convert_alpha()
player_walking_2 = pygame.transform.scale(pygame.image.load('character_walking_2.png'), (50, 113)).convert_alpha()
player_walking_3 = pygame.transform.scale(pygame.image.load('character_walking_3.png'), (50, 113)).convert_alpha()
player_walking_4 = pygame.transform.scale(pygame.image.load('character_walking_4.png'), (50, 113)).convert_alpha()
player_walking_5 = pygame.transform.scale(pygame.image.load('character_walking_5.png'), (50, 113)).convert_alpha()
player_walking_6 = pygame.transform.scale(pygame.image.load('character_walking_6.png'), (50, 113)).convert_alpha()
player_walking_frames_left = [player_walking_1, player_walking_2, player_walking_3, player_walking_4, player_walking_5, player_walking_6]
player_walking_frames_right = []
for frame in player_walking_frames_left[:]:
    player_walking_frames_right.append(pygame.transform.flip(frame, True, False))
    
player_arm = pygame.transform.scale(pygame.image.load('character_arm.png'), (15, 15)).convert_alpha()
player_arm_left = player_arm
player_arm_right = pygame.transform.flip(player_arm, True, False)
player_sword = pygame.transform.scale(pygame.image.load('character_sword.png'), (40, 90)).convert_alpha()

ghost_image_1 = pygame.transform.scale(pygame.image.load('ghost1.png'), (75, 100)).convert_alpha()
ghost_image_left_1 = ghost_image_1
ghost_image_right_1 = pygame.transform.flip(ghost_image_1, True, False)

ghost_image_2 = pygame.transform.scale(pygame.image.load('ghost2.png'), (75, 100)).convert_alpha()
ghost_image_left_2 = ghost_image_2
ghost_image_right_2 = pygame.transform.flip(ghost_image_2, True, False)

ghost_image_3 = pygame.transform.scale(pygame.image.load('ghost3.png'), (75, 100)).convert_alpha()
ghost_image_left_3 = ghost_image_3
ghost_image_right_3 = pygame.transform.flip(ghost_image_3, True, False)

ghost_image_4 = pygame.transform.scale(pygame.image.load('ghost4.png'), (75, 100)).convert_alpha()
ghost_image_left_4 = ghost_image_4
ghost_image_right_4 = pygame.transform.flip(ghost_image_4, True, False)

ghost_hurt = pygame.transform.scale(pygame.image.load('ghost_hurt.png'), (75, 100)).convert_alpha()
ghost_hurt_left = ghost_hurt
ghost_hurt_right = pygame.transform.flip(ghost_hurt, True, False)

ghost_sword = pygame.transform.scale(pygame.image.load('ghost_sword.png'), (15, 75)).convert_alpha()
ghost_arm = pygame.transform.scale(pygame.image.load('ghost_arm.png'), (20, 20)).convert_alpha()
ghost_arm_left = ghost_arm
ghost_arm_right = pygame.transform.flip(ghost_arm, True, False)

ghost_arm_hurt = pygame.transform.scale(pygame.image.load('ghost_arm_hurt.png'), (20, 20)).convert_alpha()
ghost_arm_hurt_left = ghost_arm_hurt
ghost_arm_hurt_right = pygame.transform.flip(ghost_arm_hurt, True, False)


# Set up some game values.
available_fonts = pygame.font.get_fonts()
map_width = 3200; map_height = 1800
background = pygame.transform.scale(pygame.image.load('background.jpg'), (map_width, map_height))
bg_rect = background.get_rect()
scores_level_1 = []
scores_level_2 = []
scores_level_3 = []
level = 1
level_1_complete = level_2_complete = level_3_complete = False
game_tick_num = 0
spawn_speed = 600
level_text_alpha = 255
paused = False

# Set up some button images.
pause_button_image = pygame.transform.scale(pygame.image.load('pause_button.png'), (40, 40))
unpause_button_image = pygame.transform.scale(pygame.image.load('unpause_button.png'), (100, 100))
home_button_image = pygame.transform.scale(pygame.image.load('home_button.png'), (100, 100))

# Set up ability to draw text easily.
def draw_text(text, font_type, font_size, text_color, surface, x, y, position):
    if font_type in available_fonts:
        font = pygame.font.SysFont(font_type, font_size)
    else:
        font = pygame.font.Font(font_type, font_size)
    textobj = font.render(text, True, text_color)
    textrect = textobj.get_rect()
    if position == 'topleft':
        textrect.topleft = (x, y)
    elif position == 'center':
        textrect.center = (x, y)
    surface.blit(textobj, textrect)

# Set up ability to clamp.
def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))

# Get health color.
def get_health_color(health, max_health):
    health_ratio = max(0, min(1, health / max_health))
    if health_ratio >= 0.5:
        red = int(255 * (1 - health_ratio) * 2)
        green = 255
    else:
        red = 255
        green = int(255 * health_ratio * 2)
        if health_ratio <= 0.3:
            fade_ratio = health_ratio / 0.3
            green = int(green * fade_ratio)
    if health_ratio <= 0.15:
        pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) / 2 # Red pulsing effect.
        brightness = 0.6 + 0.4 * pulse
        red = int(red * brightness)
        green = int(green * brightness)
    return (red, green, 0)

# Set up health bar.
def draw_health_bar(surface, x, y, bar_width, bar_height, health, max_health):
    fill = (health / max_health) * bar_width
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    unfilled_rect = pygame.Rect(fill_rect.right, y, bar_width - fill_rect.width, bar_height)
    pygame.draw.rect(surface, dark_gray, unfilled_rect)
    pygame.draw.rect(surface, get_health_color(health, max_health), fill_rect)

# Set up the HUD.
def drawHUD():
    draw_health_bar(game_window, 45, 13, 1100, 10, player.health, player.max_health)
    draw_text(f'0{player.lives}', 'LiberationSans-Regular.ttf', 25, white, game_window, 10, 4, 'topleft')
    draw_text(f'Time Survived: {game_tick_num // FPS}', 'LiberationSans-Regular.ttf', 25, white, game_window, 10, 30, 'topleft')
    draw_text(f'Score: {player.score}', 'LiberationSans-Regular.ttf', 25, white, game_window, 10, 56, 'topleft')

# For buttons in menus.
class Button:
    def __init__(self, text, font_type, font_size, color, surface, scale, x, y, position):
        self.text = text
        self.font_type = font_type
        self.font_size = font_size
        self.color = color
        self.surface = surface
        self.scale = scale
        self.target_scale = scale
        self.x = x
        self.y = y
        self.position = position

        # Load font
        if font_type in available_fonts:
            self.font = pygame.font.SysFont(font_type, font_size)
        else:
            self.font = pygame.font.Font(font_type, font_size)

        # Base text surface
        self.base_surf = self.font.render(text, True, color)
        self.current_surf = self.base_surf
        self.rect = self.base_surf.get_rect()

        if position == 'topleft':
            self.rect.topleft = (x, y)
        elif position == 'center':
            self.rect.center = (x, y)

    def update(self, mouse_pos):
        # Hover detection > scale
        if self.rect.collidepoint(mouse_pos):
            self.target_scale = 1.1
        else:
            self.target_scale = 1.0

        # Smooth scale animation
        self.scale += (self.target_scale - self.scale) * 0.2

        # Re-scale text
        new_w = int(self.base_surf.get_width() * self.scale)
        new_h = int(self.base_surf.get_height() * self.scale)
        self.current_surf = pygame.transform.smoothscale(self.base_surf, (new_w, new_h))

        # Update rect to stay centered
        self.rect = self.current_surf.get_rect(center=(self.x, self.y))

    def is_clicked(self, mouse_pos, click):
        if click and self.rect.collidepoint(mouse_pos):
            click_sound_effect.play()
        return click and self.rect.collidepoint(mouse_pos)

    def draw(self):
        self.surface.blit(self.current_surf, self.rect)

# For buttons with images instead of text.
class Button_Image:
    def __init__(self, image, surface, x, y, position):
        self.image = image
        self.surface = surface
        self.x = x
        self.y = y
        self.position = position

        self.rect = self.image.get_rect()
        
        if position == 'topleft':
            self.rect.topleft = (x, y)
        elif position == 'center':
            self.rect.center = (x, y)

    def is_clicked(self, mouse_pos, click):
        if click and self.rect.collidepoint(mouse_pos):
            click_sound_effect.play()
        return click and self.rect.collidepoint(mouse_pos)

    def draw(self):
        self.surface.blit(self.image, self.rect)

# Make all buttons.
play_button = Button('Start Game', 'Creepster-Regular.ttf', 90, white, home_screen, 1.0, window_width // 2, 210, 'center')
how_to_play_button = Button('How To Play', 'Creepster-Regular.ttf', 90, white, home_screen, 1.0, window_width // 2, 320, 'center')
view_leaderboard_button = Button('View Leaderboard', 'Creepster-Regular.ttf', 90, white, home_screen, 1.0, window_width // 2, 430, 'center')
quit_button = Button('Quit', 'Creepster-Regular.ttf', 90, white, home_screen, 1.0, window_width // 2, 540, 'center')
okay_instructions_button = Button('Okay', 'Creepster-Regular.ttf', 100, white, instructions, 1.0, window_width // 2, 550, 'center')
okay_leaderboard_button = Button('Okay', 'Creepster-Regular.ttf', 100, white, leaderboard, 1.0, window_width // 2, 550, 'center')
okay_choose_name_button = Button('Okay', 'Creepster-Regular.ttf', 100, white, choose_name_screen, 1.0, window_width // 2, 550, 'center')
okay_game_over_button = Button('Okay', 'Creepster-Regular.ttf', 100, white, game_over_screen, 1.0, window_width // 3 * 2, 550, 'center')
level_1_button = Button('Level 1', 'Creepster-Regular.ttf', 100, white, levels_screen, 1.0, window_width // 2, 280, 'center')
level_2_button = Button('Level 2', 'Creepster-Regular.ttf', 100, white, levels_screen, 1.0, window_width // 2, 380, 'center')
level_3_button = Button('Level 3', 'Creepster-Regular.ttf', 100, white, levels_screen, 1.0, window_width // 2, 480, 'center')
back_levels_screen_button = Button('Back', 'Creepster-Regular.ttf', 100, white, levels_screen, 1.0, window_width // 2, 600, 'center')
leaderboard_level_1_button = Button('Level 1', 'Creepster-Regular.ttf', 100, white, choose_leaderboard_screen, 1.0, window_width // 2, 200, 'center')
leaderboard_level_2_button = Button('Level 2', 'Creepster-Regular.ttf', 100, white, choose_leaderboard_screen, 1.0, window_width // 2, 320, 'center')
leaderboard_level_3_button = Button('Level 3', 'Creepster-Regular.ttf', 100, white, choose_leaderboard_screen, 1.0, window_width // 2, 440, 'center')
back_choose_leaderboard_button = Button('Back', 'Creepster-Regular.ttf', 100, white, choose_leaderboard_screen, 1.0, window_width // 2, 570, 'center')
pause_button = Button_Image(pause_button_image, game_window, 1150, 10, 'topleft')
unpause_button = Button_Image(unpause_button_image, paused_game_screen, window_width // 2, window_height // 2, 'center')
home_button = Button_Image(home_button_image, paused_game_screen, window_width // 2 + 150, window_height // 2, 'center')

# Click sound effect.
click_sound_effect = pygame.mixer.Sound('click_sound_effect.wav')

# Game menu music.
pygame.mixer.music.load('game_menu_music.mp3')
pygame.mixer.music.play(-1)

# Assign buttons into groups.
home_screen_buttons = [play_button, how_to_play_button, view_leaderboard_button, quit_button]
level_buttons = [level_1_button, level_2_button, level_3_button, back_levels_screen_button]
choose_leaderboard_buttons = [leaderboard_level_1_button, leaderboard_level_2_button, leaderboard_level_3_button, back_choose_leaderboard_button]

# Check if leaderboard files exist and make new ones if they don't.
if not os.path.exists('leaderboard_level_1.txt'):
    open('leaderboard_level_1.txt', 'w').close()
if not os.path.exists('leaderboard_level_2.txt'):
    open('leaderboard_level_2.txt', 'w').close()
if not os.path.exists('leaderboard_level_3.txt'):
    open('leaderboard_level_3.txt', 'w').close()

# This runs the menu.
def run_menu_loop():
    global window_state
    window_state = home_screen
    running_menu = True
    while running_menu:
        home_screen.fill(black)
        mouse_pos = pygame.mouse.get_pos()
        click = False

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                click = True

        # Draw titles.
        draw_text('Ghost Rush', 'Creepster-Regular.ttf', 150, white, home_screen, window_width // 2, 90, 'center')
        draw_text('Made By Marcus Chung', 'Creepster-Regular.ttf', 110, white, home_screen, window_width // 2, 640, 'center')

        # Update & draw buttons
        for button in home_screen_buttons:
            button.update(mouse_pos)
            button.draw()

        window.blit(window_state, (0, 0))

        # Click actions
        if play_button.is_clicked(mouse_pos, click):
            choose_name()
            running_menu = False

        if how_to_play_button.is_clicked(mouse_pos, click):
            show_instructions()
            running_menu = False

        if view_leaderboard_button.is_clicked(mouse_pos, click):
            choose_leaderboard()
            running_menu = False

        if quit_button.is_clicked(mouse_pos, click):
            pygame.quit()
            sys.exit()
        
        pygame.display.update()
        clock.tick(FPS)

# For the name choosing screen.
def choose_name():
    # Reset variables before starting a new round.
    global window_state, player_name, ghosts
    player.lives = 3
    player.health = player.max_health
    player.score = 0
    ghosts = []
    player.show_weapon = False
    player.side = 'right'
    player.offset_x = player.offset_y = 0
    player.world_x, player.world_y = map_width // 2, map_height // 2
    player.arm.weapon.attack = None

    # Check if player already entered their name in. (if not choose a name)
    if not 'player_name' in globals():
        window_state = choose_name_screen
        player_name = ''
        choose_name_running = True
        while choose_name_running:
            choose_name_screen.fill(black)
            mouse_pos = pygame.mouse.get_pos()
            click = False
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    click = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    else:
                        player_name += event.unicode

            # Draw instructions.
            draw_text('Choose A Username', 'Creepster-Regular.ttf', 50, white, choose_name_screen, window_width // 2, 100, 'center')
            draw_text('Max of 20 characters', 'Creepster-Regular.ttf', 50, white, choose_name_screen, window_width // 2, 180, 'center')
            draw_text('Type to start', 'Creepster-Regular.ttf', 50, white, choose_name_screen, window_width // 2, 260, 'center')
            draw_text('You may not choose a name that has alreday been used.', 'Creepster-Regular.ttf', 50, white, choose_name_screen, window_width // 2, 340, 'center')
            draw_text(f'{player_name}', 'Creepster-Regular.ttf', 50, white, choose_name_screen, window_width // 2, 420, 'center')
            
            okay_choose_name_button.update(mouse_pos)
            okay_choose_name_button.draw()

            window.blit(window_state, (0, 0))

            # Check if name chosen is already in game files.
            not_in_leaderboard_level_1 = True
            not_in_leaderboard_level_2 = True
            not_in_leaderboard_level_3 = True
            
            with open('leaderboard_level_1.txt', 'r') as file:
                for line in file:
                    parts = line.strip().split()
                    if not parts:
                        continue

                    name = parts[0]
                    if name == player_name:
                        not_in_leaderboard_level_1 = False
                        break

            with open('leaderboard_level_2.txt', 'r') as file:
                for line in file:
                    parts = line.strip().split()
                    if not parts:
                        continue

                    name = parts[0]
                    if name == player_name:
                        not_in_leaderboard_level_2 = False
                        break

            with open('leaderboard_level_3.txt', 'r') as file:
                for line in file:
                    parts = line.strip().split()
                    if not parts:
                        continue

                    name = parts[0]
                    if name == player_name:
                        not_in_leaderboard_level_3 = False
                        break

            if (
                okay_choose_name_button.is_clicked(mouse_pos, click) and player_name != '' and len(player_name) <= 20
                and not_in_leaderboard_level_1 and not_in_leaderboard_level_2 and not_in_leaderboard_level_3
                ):
                # If name not already in game files continue to choosing level.
                choose_level()
                choose_name_running = False
        
            pygame.display.update()
            clock.tick(FPS)

    else:
        # Skip right to choosing level if name already chosen.
        choose_level()

# Show how to play/instructions.
def show_instructions():
    global window_state
    window_state = instructions
    
    instructions_running = True
    while instructions_running:
        instructions.fill(black)
        mouse_pos = pygame.mouse.get_pos()
        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                click = True

        # Draw instructions.
        draw_text('Use arrow keys to move around the screen.', 'Creepster-Regular.ttf', 40, white, instructions, window_width // 2, 80, 'center')
        draw_text('You can see your lives, health, and score at the top of the screen.', 'Creepster-Regular.ttf', 40, white, instructions, window_width // 2, 140, 'center')
        draw_text('Survive waves of ghosts coming to attack you and defeat them.', 'Creepster-Regular.ttf', 40, white, instructions, window_width // 2, 200, 'center')
        draw_text('Ghosts with more blood marks are stronger, faster, and use better attacks.', 'Creepster-Regular.ttf', 40, white, instructions, window_width // 2, 260, 'center')
        draw_text('Attack Keys are A, S, and D for thrust, slash up, and slash down.', 'Creepster-Regular.ttf', 40, white, instructions, window_width // 2, 320, 'center')
        draw_text('F and G are special attacks and have longer cooldowns.', 'Creepster-Regular.ttf', 40, white, instructions, window_width // 2, 380, 'center')
        draw_text('Complete all three levels for victory!', 'Creepster-Regular.ttf', 40, white, instructions, window_width // 2, 440, 'center')

        okay_instructions_button.update(mouse_pos)
        okay_instructions_button.draw()

        window.blit(window_state, (0, 0))

        if okay_instructions_button.is_clicked(mouse_pos, click):
            run_menu_loop()
            instructions_running = False
        
        pygame.display.update()
        clock.tick(FPS)

# For choosing which leaderboard to view.
def choose_leaderboard():
    global window_state
    window_state = choose_leaderboard_screen
    
    choose_leaderboard_running = True
    while choose_leaderboard_running:
        choose_leaderboard_screen.fill(black)
        mouse_pos = pygame.mouse.get_pos()
        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                click = True
                
        draw_text('Choose which leaderboard to view', 'Creepster-Regular.ttf', 80, white, choose_leaderboard_screen, window_width // 2, 100, 'center')
        
        # Update and draw buttons
        for button in choose_leaderboard_buttons:
            button.update(mouse_pos)
            button.draw()

        window.blit(window_state, (0, 0))

        # Click actions
        if leaderboard_level_1_button.is_clicked(mouse_pos, click):
            view_leaderboard(1)
            choose_leaderboard_running = False

        if leaderboard_level_2_button.is_clicked(mouse_pos, click):
            view_leaderboard(2)
            choose_leaderboard_running = False

        if leaderboard_level_3_button.is_clicked(mouse_pos, click):
            view_leaderboard(3)
            choose_leaderboard_running = False

        if back_choose_leaderboard_button.is_clicked(mouse_pos, click):
            run_menu_loop()
            choose_leaderboard_running = False

        pygame.display.update()
        clock.tick(FPS)

# View chosen leaderboard.
def view_leaderboard(level):
    global window_state, scores_level_1, scores_level_2, scores_level_3
    if level == 1:
        scores_level_1 = []
        with open('leaderboard_level_1.txt', 'r') as file:
            for line in file:
                # Use rsplit() instead of split() so if there are spaces in the name it doen't mess things up.
                parts = line.strip()
                if not parts:
                    continue
                name, score = parts.rsplit(' ', 1)
                scores_level_1.append([name, int(score)])

    # Sort by score instead of by name.
    scores_level_1.sort(key=lambda x: x[1], reverse=True)
    # Keep the top ten scores.
    scores_level_1 = scores_level_1[:10]

    # Repeat with different files for the other levels.
    if level == 2:
        scores_level_2 = []
        with open('leaderboard_level_2.txt', 'r') as file:
            for line in file:
                parts = line.strip()
                if not parts:
                    continue
                name, score = parts.rsplit(' ', 1)
                scores_level_2.append([name, int(score)])

        scores_level_2.sort(key=lambda x: x[1], reverse=True)
        scores_level_2 = scores_level_2[:10]

    if level == 3:
        scores_level_3 = []
        with open('leaderboard_level_3.txt', 'r') as file:
            for line in file:
                parts = line.strip()
                if not parts:
                    continue
                name, score = parts.rsplit(' ', 1)
                scores_level_3.append([name, int(score)])

        scores_level_3.sort(key=lambda x: x[1], reverse=True)
        scores_level_3 = scores_level_3[:10]
            
    window_state = leaderboard
    
    leaderboard_running = True
    while leaderboard_running:
        leaderboard.fill(black)
        mouse_pos = pygame.mouse.get_pos()
        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                click = True

        scores_level = scores_level_1 if level == 1 else scores_level_2 if level == 2 else scores_level_3

        # Depending on level use different score lists.
        for num, (name, score) in enumerate(scores_level):
            # And draw place, name, and score.
            draw_text(f'{num + 1}. {name}', 'Creepster-Regular.ttf', 40, white, leaderboard, 100, 50 + 40 * num, 'topleft')
            draw_text(f'{score}', 'Creepster-Regular.ttf', 40, white, leaderboard, 600, 50 + 40 * num, 'topleft')
        
        okay_leaderboard_button.update(mouse_pos)
        okay_leaderboard_button.draw()

        window.blit(window_state, (0, 0))

        if okay_leaderboard_button.is_clicked(mouse_pos, click):
            choose_leaderboard()
            leaderboard_running = False
        
        pygame.display.update()
        clock.tick(FPS)

# For choosing level to play.
def choose_level():
    global window_state, level, game_tick_num
    window_state = levels_screen
    
    requirement = False
    
    levels_running = True
    while levels_running:
        levels_screen.fill(black)
        mouse_pos = pygame.mouse.get_pos()
        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                click = True

        # Draw instuctions.
        draw_text('Choose your difficulty', 'Creepster-Regular.ttf', 100, white, levels_screen, window_width // 2, 100, 'center')
        if requirement:
            draw_text('You must complete all previous levels to access this level.', 'Creepster-Regular.ttf', 40, white, levels_screen, window_width // 2, 200, 'center')

        # Update and draw buttons
        for button in level_buttons:
            button.update(mouse_pos)
            button.draw()

        window.blit(window_state, (0, 0))

        game_tick_num = 0

        # Click actions
        if level_1_button.is_clicked(mouse_pos, click):
            level = 1
            window_state = game_window
            # Stop current music and switch it to the game music (on repeat).
            pygame.mixer.music.stop()
            pygame.mixer.music.load('game_music.mp3')
            pygame.mixer.music.play(-1)
            levels_running = False

        # Repeat with next two levels.
        if level_2_button.is_clicked(mouse_pos, click):
            if level_1_complete:
                level = 2
                window_state = game_window
                pygame.mixer.music.stop()
                pygame.mixer.music.load('game_music.mp3')
                pygame.mixer.music.play(-1)
                levels_running = False
            else:
                requirement = True

        if level_3_button.is_clicked(mouse_pos, click):
            if level_1_complete and level_2_complete:
                level = 3
                window_state = game_window
                pygame.mixer.music.stop()
                pygame.mixer.music.load('game_music.mp3')
                pygame.mixer.music.play(-1)
                levels_running = False
            else:
                requirement = True

        if back_levels_screen_button.is_clicked(mouse_pos, click):
            window_state = home_screen
            levels_running = False

        pygame.display.update()
        clock.tick(FPS)

# After death in the game show place on leaderboard (for that level) and execute game over.
def game_over(level):
    global window_state, scores_level_1, scores_level_2, scores_level_3

    # Open leaderboard files like in view_leaderboard def.
    if level == 1:
        scores_level_1 = []
        with open('leaderboard_level_1.txt', 'r') as file:
            for line in file:
                parts = line.strip()
                if not parts:
                    continue
                name, score = parts.rsplit(' ', 1)
                scores_level_1.append([name, int(score)])
                
        scores_level_1.sort(key=lambda x: x[1], reverse=True)
        scores_level_1 = scores_level_1[:10]

    if level == 2:
        scores_level_2 = []
        with open('leaderboard_level_2.txt', 'r') as file:
            for line in file:
                parts = line.strip()
                if not parts:
                    continue
                name, score = parts.rsplit(' ', 1)
                scores_level_2.append([name, int(score)])
                
        scores_level_2.sort(key=lambda x: x[1], reverse=True)
        scores_level_2 = scores_level_2[:10]

    if level == 3:
        scores_level_3 = []
        with open('leaderboard_level_3.txt', 'r') as file:
            for line in file:
                parts = line.strip()
                if not parts:
                    continue
                name, score = parts.rsplit(' ', 1)
                scores_level_3.append([name, int(score)])
                
        scores_level_3.sort(key=lambda x: x[1], reverse=True)
        scores_level_3 = scores_level_3[:10]
        
    window_state = game_over_screen
    
    game_over_running = True
    while game_over_running:
        game_over_screen.fill(black)
        mouse_pos = pygame.mouse.get_pos()
        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                click = True
                
        draw_text('Game Over', 'Creepster-Regular.ttf', 100, white, game_over_screen, window_width // 2, 100, 'center')

        scores_level = scores_level_1 if level == 1 else scores_level_2 if level == 2 else scores_level_3
        # Check if player is in top ten and draw a message accordingly.
        if any(name == player_name and score == player.score for name, score in scores_level):
            draw_text(f'You scored {player.score} and you placed in the top 10! Great job!', 'Creepster-Regular.ttf', 50, white, game_over_screen, window_width // 2, 200, 'center')
            for index, (name, score) in enumerate(scores_level):
                if name == player_name and score == player.score:
                    place = index + 1  # + 1 because place starts at 1 not 0
                    break
            # Draw exact place if in top ten. For example: #3
            draw_text(f'#{place}', 'Creepster-Regular.ttf', 200, white, game_over_screen, 850, 350, 'center')
        else:
            # Draw a different message and show player's score in big if not in top ten.
            draw_text(f'You didn\'t place in the top 10. Better luck next time!', 'Creepster-Regular.ttf', 50, white, game_over_screen, window_width // 2, 200, 'center')
            draw_text(f'Score {score}', 'Creepster-Regular.ttf', 100, white, game_over_screen, 900, 350, 'center')
        for num, (name, score) in enumerate(scores_level):
            draw_text(f'{num + 1}. {name}', 'Creepster-Regular.ttf', 40, white, game_over_screen, 100, 250 + 40 * num, 'topleft')
            draw_text(f'{score}', 'Creepster-Regular.ttf', 40, white, game_over_screen, 600, 250 + 40 * num, 'topleft')

        okay_game_over_button.update(mouse_pos)
        okay_game_over_button.draw()

        window.blit(window_state, (0, 0))

        if okay_game_over_button.is_clicked(mouse_pos, click):
            run_menu_loop()
            game_over_running = False
        
        pygame.display.update()
        clock.tick(FPS)

# Set up surface rotation.
def rotate_surface(surface, pivot_pos_world, pivot_pos_local, angle):
    rotated_surface = pygame.transform.rotate(surface, -angle) # -angle so I don't have to convert clockwise to counterclockwise every time.
    rotated_rect = rotated_surface.get_rect()
    orig_center = pygame.Vector2(surface.get_rect().center)
    pivot_to_center = pivot_pos_local - orig_center
    rotated_pivot_to_center = pivot_to_center.rotate(angle)
    blit_pos = pivot_pos_world - rotated_pivot_to_center - pygame.Vector2(rotated_rect.width / 2, rotated_rect.height / 2)

    return rotated_surface, blit_pos

# Set up arm class. (for both player and ghosts)
class Arm:
    def __init__(self, controller, controller_name, side):
        # Set up some variables.
        self.angle = 0
        self.attack_timer = 0
        self.attack_duration = 0
        self.pause_timer = self.set_pause_timer = 5
        self.controller = controller
        self.controller_name = controller_name
        self.side = side
        
        # If player use player_arm else use ghost_arm.
        if self.controller_name == 'player':
            self.rect = player_arm.get_rect()
        else:
            self.rect = ghost_arm.get_rect()

        # Set up a surface for the image and blit image on.
        self.surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)

        if self.controller_name == 'player':
            self.surface.blit(player_arm_right, (0, 0))
        else:
            self.surface.blit(ghost_arm_right, (0, 0))
            
        # Set the pivot poin on the arm where it will rotate on. (center)
        self.pivot_local = pygame.Vector2(self.rect.width // 2, self.rect.height // 2)

        # Set arm to desired angle.
        self.get_rotated_arm(self.angle)

        # Set up sword using the Weapon class.
        self.weapon = Weapon(self.controller_name, self, self.side)

    # Update the arm. (runs every frame)
    def update(self):
        if self.attack_timer > 0: # If attacking:
            progress = 1 - (self.attack_timer / self.attack_duration) # Set angle progress * destination.
            self.angle = self.start_angle + (self.end_angle - self.start_angle) * progress
            self.attack_timer -= 1 # Decrease timer.

            if self.attack_timer == 0: # If attack is finished:
                self.angle = self.end_angle # Set angle to destination if already haven't.
                self.pause_timer = self.set_pause_timer + 1 # Stay for 5 frames.

        if self.pause_timer > 0:
            self.pause_timer -= 1 # Decrease timer.
            
        elif self.attack_timer == 0: # If attack is finished and the slight pause is done:
            self.static_rotate(0) # Set arm back to normal position.

        self.side = self.controller.side # Set side to controller side. For example, ghost is facing right > arm is now facing right.
        
        self.surface.fill((0, 0, 0, 0)) # Transparent
        # If controller is player use player_arm else use ghost_arm.
        # And also determine which image to use (left or right) depending on side.
        if self.side == 'left':
            if self.controller_name == 'player':
                self.surface.blit(player_arm_left, (0, 0))
            else:
                if self.controller.hit_timer > 0: # If ghost got hit by player the ghost turns red to show it. (uses another image)
                    self.surface.blit(ghost_arm_hurt_left, (0, 0)) # Arm also needs to match and turn red. (uses another image)
                else:
                    self.surface.blit(ghost_arm_left, (0, 0))
        else:
            if self.controller_name == 'player':
                self.surface.blit(player_arm_right, (0, 0))
            else:
                if self.controller.hit_timer > 0:
                    self.surface.blit(ghost_arm_hurt_right, (0, 0))
                else:
                    self.surface.blit(ghost_arm_right, (0, 0))
                    
        self.get_rotated_arm(self.angle) # Rotate arm to the angle determined earlier.
        self.weapon.pivot_world = self.pivot_world # Set the weapon to the correct pivot spot.
        self.weapon.side = self.side # Set weapons side to self.side.

        self.weapon.update()

    # Rotate straight to angle chosen. No animation.
    def static_rotate(self, angle):
        self.angle = angle

    # Rotate according to duration start angle and end angle. Handled in the arm.update() as well.
    def rotate_over_time(self, start_angle, end_angle, attack_duration): # (Duration in ticks)
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.attack_timer = self.attack_duration = attack_duration
        self.static_rotate(self.start_angle)

    # This rotates the actual arm setting the new point to rotate on. (pivot world)
    def get_rotated_arm(self, angle):
        # Set x and y points to a place on the controller's rect.
        x = self.controller.rect.left + self.controller.rect.width / 3 if self.side == 'left' else self.controller.rect.right - self.controller.rect.width / 3
        y = self.controller.rect.centery + self.controller.rect.height / 10
                                                                                                     
        self.pivot_world = pygame.Vector2(x, y)
        self.rotated_arm, self.pos = rotate_surface(self.surface, self.pivot_world, self.pivot_local, angle if self.side == 'right' else -angle)

    # Draw the arm onto the screen.
    def draw(self):
        self.draw_pos_x = self.pos[0] - player.cam_x + window_width // 2
        self.draw_pos_y = self.pos[1] - player.cam_y + window_height // 2
        game_window.blit(self.rotated_arm, (self.draw_pos_x, self.draw_pos_y))

# Set up weapon class. (for player and ghosts)
class Weapon:
    def __init__(self, controller_name, arm, side):
        # Set up some variables.
        self.cooldowns = [0 for _ in range(10)] # 10 for the number of different attack slots. Not all will be used.
        self.main_cooldown = self.set_main_cooldown = 10 # For setting cooldown to main cooldown when resetting.
        self.attack_timer = 0
        self.pause_timer = self.set_pause_timer = 5 # For setting pause timer back when resetting.
        self.attack = None # Current attack.
        self.show_weapon = False
        self.arm_angle = 45
        self.angle = 15
        self.controller_name = controller_name
        self.arm = arm
        self.side = side
        self.rect = pygame.Rect(0, 0, 0, 0)

        # Determine whether player or ghost.
        if self.controller_name == 'player':
            self.rect = player_sword.get_rect()
        else:
            self.rect = ghost_sword.get_rect()

        # Make a surface for the image.
        self.weapon = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)

        # Draw accordingly to controller.
        if self.controller_name == 'player':
            self.weapon.blit(player_sword, (0, 0))
        else:
            self.weapon.blit(ghost_sword, (0, 0))

        # Set pivot location on sword and in world coordinates.
        self.pivot_local = pygame.Vector2(self.rect.width // 2, self.rect.height - self.rect.height // 10)
        self.pivot_world = self.arm.pivot_world

        # Set weapon to desired orientation and position.
        self.rotated_weapon, self.weapon_pos = rotate_surface(self.weapon, self.pivot_world, self.pivot_local, self.angle if self.side == 'right' else -self.angle)

        # Set variable only for either player or ghosts.
        if self.controller_name == 'player':
            self.dash_speed = 30
            self.dash_velocity_x = 0
        else:
            self.player_already_hit = False

    # Update the weapon. (runs every frame)
    def update(self):
        if self.attack_timer > 0: # If attacking:
            self.show_weapon = True # Show the weapon.
            self.progress = 1 - (self.attack_timer / self.attack_duration) # Determine weapon angle from progress, start, and end position.
            self.angle = self.attack_start + (self.attack_end - self.attack_start) * self.progress

            # If player check if dash_slash() is happening
            if self.controller_name == 'player':
                if self.attack == 'dash_slash':
                    # Register extra speed from dashing but either left or right.
                    self.dash_velocity_x = self.dash_speed if self.side == 'right' else -self.dash_speed
            else:
                # If self.rect touches player, inflict damage.
                if self.rect.colliderect(player.rect) and self.show_weapon:
                    if not self.player_already_hit:
                        player.take_damage(self.damage)
                        self.player_already_hit = True
                else:
                    self.player_already_hit = False

            self.attack_timer -= 1

            # Same pause timer as in the Arm class.
            if self.attack_timer == 0:
                self.attack = None
                self.angle = self.attack_end
                self.pause_timer = self.set_pause_timer + 1
                
        if self.pause_timer > 0:
            self.pause_timer -= 1

        # Handle cooldowns for each attack.
        elif self.attack_timer == 0:
            for cooldown in range(len(self.cooldowns)):
                if self.cooldowns[cooldown] > 0:
                    self.cooldowns[cooldown] -= 1
            if self.main_cooldown > 0:
                self.main_cooldown -= 1
            self.show_weapon = False

        # If attack isn't dash_slash(), remove extra speed.
        if self.attack != 'dash_slash':
            self.dash_velocity_x = 0

        # Set weapon to the angle determined earlier.
        self.rotated_weapon, self.weapon_pos = rotate_surface(self.weapon, self.pivot_world, self.pivot_local, self.angle if self.side == 'right' else -self.angle)
        self.rect = self.rotated_weapon.get_rect(topleft=self.weapon_pos)

    # Attacks
    def thrust(self):
        if self.cooldowns[0] <= 0 and self.main_cooldown <= 0: # If this attack's cooldown and the main cooldown are at 0:
            self.cooldowns[0] = 10 # Set attacks's cooldown.
            if self.controller_name != 'player': # If controller is a ghost:
                self.player_already_hit = False # Set the player_already_hit variable to False. (Starting a new attack means player was not hit already this new attack)
            self.attack_duration = self.attack_timer = 5 if self.controller_name == 'player' else 5 * 3 # Setting the speed of the attack (higher = slower) times 3 for ghosts, because ghosts are slower.
            self.attack_start = 80 # State where the attack will start and end. (angles not position)
            self.attack_end = 90
            self.arm.rotate_over_time(self.attack_start, self.attack_end, self.attack_duration) # Use arm.rotate_over_time to make the arm move while the weapon does.
            self.main_cooldown = self.set_main_cooldown # Set the main cooldown back again.
            self.damage = 10 # State how much damage the enemy takes if weapon hits them.
            self.attack = 'thrust' # Which attack is happening.

    # Repeat with other attacks, just different angles and durations.
    def slash_down(self):
        if self.cooldowns[1] <= 0 and self.main_cooldown <= 0:
            if self.controller_name != 'player':
                self.player_already_hit = False
            self.cooldowns[1] = 10
            self.attack_duration = self.attack_timer = 10 if self.controller_name == 'player' else 10 * 3
            self.attack_start = 0
            self.attack_end = 135
            self.arm.rotate_over_time(self.attack_start, self.attack_end, self.attack_duration)
            self.main_cooldown = self.set_main_cooldown
            self.damage = 15
            self.attack = 'slash_down'

    def slash_up(self):
        if self.cooldowns[2] <= 0 and self.main_cooldown <= 0:
            if self.controller_name != 'player':
                self.player_already_hit = False
            self.cooldowns[2] = 10
            self.attack_duration = self.attack_timer = 10 if self.controller_name == 'player' else 10 * 3
            self.attack_start = 195
            self.attack_end = 45
            self.arm.rotate_over_time(self.attack_start, self.attack_end, self.attack_duration)
            self.main_cooldown = self.set_main_cooldown
            self.damage = 15
            self.attack = 'slash_up'

    def spin_attack(self):
        if self.cooldowns[3] <= 0 and self.main_cooldown <= 0:
            if self.controller_name != 'player':
                self.player_already_hit = False
            self.cooldowns[3] = 30
            self.attack_duration = self.attack_timer = 20 if self.controller_name == 'player' else 20 * 3
            self.attack_start = 0
            self.attack_end = 450
            self.arm.rotate_over_time(self.attack_start, self.attack_end, self.attack_duration)
            self.main_cooldown = self.set_main_cooldown
            self.damage = 15
            self.attack = 'spin_attack'

    # Not used by ghosts, so slightly different construction.
    def dash_slash(self):
        if self.cooldowns[4] <= 0 and self.main_cooldown <= 0:
            self.cooldowns[4] = 50
            self.attack_duration = self.attack_timer = 10
            self.attack_start = 195
            self.attack_end = 45
            self.arm.rotate_over_time(self.attack_start, self.attack_end, self.attack_duration)
            self.main_cooldown = self.set_main_cooldown
            self.damage = 25
            self.attack = 'dash_slash'

    # Draw the weapon onto the screen.
    def draw(self):
        if self.show_weapon:
            self.weapon_draw_pos_x = self.weapon_pos[0] - player.cam_x + window_width // 2
            self.weapon_draw_pos_y = self.weapon_pos[1] - player.cam_y + window_height // 2
            game_window.blit(self.rotated_weapon, (self.weapon_draw_pos_x, self.weapon_draw_pos_y))

# Set up player class.
class Player:
    def __init__(self):
        # Set up variables like health, score and positioning.
        self.health = self.max_health = 100
        self.lives = 3
        self.score = 0
        self.cam_x, self.cam_y = window_width // 2, window_height // 2
        self.world_x, self.world_y = map_width // 2, map_height // 2
        self.velocity_x = self.velocity_y = 0
        self.player_image = player_standing_right
        self.rect = pygame.Rect(self.world_x, self.world_y, self.player_image.get_width(), self.player_image.get_height())
        self.speed = 10
        self.on_ground = False
        self.jump_power = -25
        self.gravity = 1.2
        self.side = 'right'
        self.velocity_add_x = 0
        self.frame = 0

        # Set up the player's arm.
        self.arm = Arm(self, 'player', self.side)

    # Update (handling movement and keyboard inpjut)
    def update(self):
        # Always have keyboard input.
        self.handle_keyboard_input()
        if not paused: # If paused make sure player can't move and arm and weapon can't either.
            self.update_movement()
            self.arm.update()

    # Handle actions like typing and clicking.
    def handle_keyboard_input(self):
        global click, paused # Affecting global variables in the main game loop.

        # To make it easier to use key pressed actions by shortening it. 
        keys = pygame.key.get_pressed()

        # Set velocity to 0 before adding any.
        self.velocity_x = 0
        
        if keys[K_LEFT]: # Left key pressed:
            if self.player_image == player_standing_left or self.player_image == player_standing_right: # If not moving:
                self.frame = 0 # Set to the first frame.
            self.frame += 0.5 # Gradually add and flip through.
            self.player_image = player_walking_frames_left[int(str(self.frame)[0])] # And set image to determined frame.
            if self.frame >= 5: # If on last frame:
                self.frame = 1 # Set to first frame again.
            if self.arm.weapon.attack == None: # If not attacking: (so while attacking you can't switch back and forth)
                self.side = 'left' # Then switch sides.
            self.velocity_x = -self.speed -self.velocity_add_x # Add velocity for left.
            
         # Repeat with right side.
        if keys[K_RIGHT]:
            if self.player_image == player_standing_left or self.player_image == player_standing_right:
                self.frame = 0
            self.frame += 0.5
            self.player_image = player_walking_frames_right[int(str(self.frame)[0])]
            if self.frame >= 5:
                self.frame = 1
            if self.arm.weapon.attack == None:
                self.side = 'right'
            self.velocity_x = self.speed + self.velocity_add_x

        # If up key pressed and on a platform (or ground which is just a big platform): 
        if keys[K_UP] and self.on_ground:
            self.velocity_y = self.jump_power # Set velocity y to jump_power and increase velocity x a little too.
            self.velocity_add_x += 2
            if self.velocity_add_x >= 6: # Cap the extra speed from going above 6.
                self.velocity_add_x = 6

        # If trying to close the window then close it and safely exit.
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN: # If keydown:
                # Attack for respective attack keys.
                if event.key == K_a: self.arm.weapon.thrust()
                if event.key == K_s: self.arm.weapon.slash_up()
                if event.key == K_d: self.arm.weapon.slash_down()
                if event.key == K_f: self.arm.weapon.spin_attack()
                if event.key == K_g: self.arm.weapon.dash_slash()

                # I escape key pressed, pause or unpause the game.
                if event.key == K_ESCAPE:
                    if not paused:
                        # Blur game screen and draw some buttons.
                        unpause_button.draw()
                        home_button.draw()
                        blur_background_screen.fill((0, 0, 0, 100))
                        blur_background_screen.blit(paused_game_screen, (0, 0))
                        game_window.blit(blur_background_screen, (0, 0))
                        paused = True
                    else:
                        paused = False

            if not paused: # Prevents extra speed from being lost when game is paused.
                if event.type == KEYUP: # If keyup:
                    if event.key == K_LEFT:
                        self.player_image = player_standing_left # Set player_image to left facing standing player.
                        self.velocity_add_x = 0 # Set extra speed gained to 0.
                        if self.velocity_x < 0: self.velocity_x = 0 # Set regular speed to 0 if speed was from left side.

                    # Repeat with right side.
                    if event.key == K_RIGHT:
                        self.player_image = player_standing_right
                        self.velocity_add_x = 0
                        if self.velocity_x > 0: self.velocity_x = 0

                    if event.key == K_UP: # # Set velocity y to 0 if speed was from going up and set extra speed gained to 0.
                        if self.velocity_y < 0: self.velocity_y = 0
                        self.velocity_add_x = 0

            # if user clicks (left click)
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                click = True

    def update_movement(self):
        if self.arm.weapon.dash_velocity_x == 0: # If not dashing:
            proposed_x = self.world_x + self.velocity_x # Use regular velocity.
        else: # Otherwise:
            proposed_x = self.world_x + self.arm.weapon.dash_velocity_x # Use the extra speed from dashing.

        # Factor in gravity.
        self.velocity_y += self.gravity
        proposed_y = self.world_y + self.velocity_y

        # Use only proposed_x and regular y so it only handles collision on the x axis.
        self.rect.topleft = (proposed_x, self.world_y)

        # For every platform check if player has collided and mangage that.
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_x > 0: # Right
                    self.rect.right = platform.rect.left
                elif self.velocity_x < 0:  # Left
                    self.rect.left = platform.rect.right
                    self.arm.weapon.dash_velocity_x = 0
                    
        new_x = self.rect.x

        # Same thing as before but with the y axis.
        self.rect.topleft = (self.world_x, proposed_y)

        self.on_ground = False

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:  # Falling
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:  # Jumping up
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0
                    
        new_y = self.rect.y

        # Clamp position to world boundaries.
        self.world_x = clamp(new_x, 0, map_width - self.rect.height // 2)
        self.world_y = clamp(new_y, 0, map_height - self.rect.width // 2)

        # Clamp the camera to world boundaries.
        self.cam_x = clamp(self.world_x, window_width // 2, map_width - window_width // 2)
        self.cam_y = clamp(self.world_y, window_height // 2, map_height - window_height // 2)

        self.rect.topleft = (self.world_x, self.world_y)

    # For easily taking damage while looking at invincibility, lives, and running the game.
    def take_damage(self, damage):
        if self.arm.weapon.attack == 'dash_slash': # If dash_slash():
            if self.arm.weapon.attack_timer == 0: # If finished dash_slash() and on pause_timer:
                self.health -= damage # Inflict damage.
        else:
            self.health -= damage # Inflict damage regularly.

        if self.health <= 0: # If health is 0:
            self.lives -= 1 # Next life.
            if self.lives == 0: # If no more lives:
                global game_running # Stop the game.
                game_running = False
            else:
                self.health = self.max_health # Reset health for next life.

    # Draw the player, player arm, and player weapon.
    def draw(self):
        game_window.blit(self.player_image, (int(self.world_x - self.cam_x + window_width // 2), int(self.world_y - self.cam_y + window_height // 2)))
        self.arm.weapon.draw()
        self.arm.draw()
        drawHUD() # Heads-up-display

# Set player to player class.
player = Player()

# Set up the ghost class.
class Ghost:
    def __init__(self, x, y, type):
        # Set up some variables.
        self.type = type
        self.rect = pygame.Rect(x, y, 75, 100)

        # Depending on type, give the ghosts different attributes. (speed, strength)
        if self.type == 1 or self.type == 2:
            self.speed = 2
        else:
            self.speed = 3

        if self.type == 1 or self.type == 2:
            self.health = self.max_health = 50
        elif self.type == 3:
            self.health = self.max_health = 75
        elif self.type == 4:
            self.health = self.max_health = 100
        
        self.world_x = x
        self.world_y = y
        self.buffer = 2
        self.hit_timer = 0
        self.already_hit = False
        self.can_damage = True
        self.new_x = self.new_y = 0
        self.side = 'right'
        self.draw_rect = pygame.Rect(int(self.world_x - player.cam_x + window_width // 2), int(self.world_y - player.cam_y + window_height // 2), 40, 80)
        
        # Set up the ghost's arm.
        self.arm = Arm(self, 'ghost', self.side)

    def update(self):

        self.move()
        self.arm.update()

        # Handle collision with players weapon.
        if player.arm.weapon.rect.colliderect(self.rect) and player.arm.weapon.attack != None:
            if not self.already_hit:
                # Take damage if not already hit during attack.
                self.health -= player.arm.weapon.damage
                self.hit_timer = 5 # 5 frames. This is how long the ghost turns red for indicating damage taken.
                self.already_hit = True
                
                # Knockback from getting hit.
                if self.side == 'left':
                    self.rect.x += 10
                    self.world_x = self.rect.x
                if self.side == 'right':
                    self.rect.x -= 10
                    self.world_x = self.rect.x
        else:
            self.already_hit = False
    
        # Attack with weapon if close enough. Attacks vary based on type.
        if self.type > 1:
            if 100 < abs(self.distance_x) < 150 and abs(self.distance_y) < 70:
                if self.type == 3:
                    if random.randint(0, 1) == 1: # 50% of the time slash_down.
                        self.attack('slash_down')
                    else:
                        self.attack('slash_up') # 50% of the time slash_up.
                else:
                    self.attack('slash_down')

        if self.type > 2:
            if 50 < abs(self.distance_x) < 100 and abs(self.distance_y) < 50:
                self.attack('thrust')
                
        if self.type == 4:
            if 50 < abs(self.distance_x) < 100 and abs(self.distance_y) < 100:
                self.attack('spin_attack')

        # Damage the player just by touching.
        if self.rect.colliderect(player.rect):
            if self.type == 1 or self.type == 2:
                player.take_damage(0.1)
            else:
                player.take_damage(0.2)
            
    def move(self):
        # Distances (x and y) between player rect and this rect.
        self.distance_x = player.world_x - self.world_x
        self.distance_y = player.world_y - self.world_y
        
        # Left, right, up, and down movement. No collision detection with platforms because ghosts can go through them.
        # Use buffers so the ghost doesn't jitter around.
        if self.distance_x + self.buffer < 0:
            self.new_x = self.world_x - self.speed
            if self.arm.weapon.attack == None:
                self.side = 'left'
        elif self.distance_x - self.buffer > 0:
            self.new_x = self.world_x + self.speed
            if self.arm.weapon.attack == None:
                self.side = 'right'
        self.arm.side = self.side
            
        if self.distance_y + self.buffer < 0:
            self.new_y = self.world_y - self.speed
        elif self.distance_y - self.buffer > 0:
            self.new_y = self.world_y + self.speed

        self.world_x = clamp(self.new_x, 0, map_width - self.rect.width // 2)
        self.world_y = clamp(self.new_y, 0, map_height - self.rect.height // 2)

        self.rect.topleft = (self.world_x, self.world_y)

    # USe to easily attack with the ghost.
    def attack(self, attack):
        if attack == 'thrust':
            self.arm.weapon.thrust()
        if attack == 'slash_down':
            self.arm.weapon.slash_down()
        if attack == 'slash_up':
            self.arm.weapon.slash_up()
        if attack == 'spin_attack':
            self.arm.weapon.spin_attack()

    def draw(self, drawing):
        # Convert world coordinates to screen coordinates for visulization.
        self.draw_rect.x = int(self.world_x - player.cam_x + window_width // 2)
        self.draw_rect.y = int(self.world_y - player.cam_y + window_height // 2)
        # Manage which image to use, left or right and which type. 
        if drawing == 'ghost':
            if self.hit_timer > 0:
                self.hit_timer -= 1
                if self.side == 'left':
                    game_window.blit(ghost_hurt_left, (self.draw_rect.topleft))
                else:
                    game_window.blit(ghost_hurt_right, (self.draw_rect.topleft))
            else:
                if self.side == 'left':
                    if self.type == 1:
                        game_window.blit(ghost_image_left_1, (self.draw_rect.topleft))
                    if self.type == 2:
                        game_window.blit(ghost_image_left_2, (self.draw_rect.topleft))
                    if self.type == 3:
                        game_window.blit(ghost_image_left_3, (self.draw_rect.topleft))
                    if self.type == 4:
                        game_window.blit(ghost_image_left_4, (self.draw_rect.topleft))
                else:
                    if self.type == 1:
                        game_window.blit(ghost_image_right_1, (self.draw_rect.topleft))
                    if self.type == 2:
                        game_window.blit(ghost_image_right_2, (self.draw_rect.topleft))
                    if self.type == 3:
                        game_window.blit(ghost_image_right_3, (self.draw_rect.topleft))
                    if self.type == 4:
                        game_window.blit(ghost_image_right_4, (self.draw_rect.topleft))
            self.arm.draw()
            self.arm.weapon.draw()

        # There are two parts to draw() either the ghost or the health bar above it.
        if drawing == 'health':
            draw_health_bar(game_window, self.draw_rect.left, self.draw_rect.y - self.draw_rect.height * 0.75, self.draw_rect.width, 4, self.health, self.max_health)

# Set up the platform class.
class Platform:
    def __init__(self, x, y, width, height):
        # Set up some variables.
        self.world_x = x
        self.world_y = y
        self.width = width
        self.total_width = int(self.width / 100)
        self.height = height
        self.rect = pygame.Rect(self.world_x, self.world_y, width, height)
        self.platform_image = pygame.transform.scale(pygame.image.load('platform_image.jpg'), (100, self.rect.height))

    # Draw the platform onto the screen.
    def draw(self):
        screen_x = int(self.world_x - player.cam_x + window_width / 2) # Convert world to screen coordinates.
        screen_y = int(self.world_y - player.cam_y + window_height / 2)
        for small_width in range(self.total_width): # Image is 100 pixels long so just draw the image multiple times to acheive desired length.
            game_window.blit(self.platform_image, (screen_x + 100 * small_width, screen_y))

# Set up the spikes class.
class Spikes:
    def __init__(self, x, y, width, height):
        # Set up some variables.
        self.world_x = x
        self.world_y = y
        self.width = width
        self.total_width = int(self.width / 100)
        self.height = height
        self.rect = pygame.Rect(self.world_x, self.world_y, width, height)
        self.spikes_image = pygame.transform.scale(pygame.image.load('game_spikes.png'), (100, 50))

    # Draw the spikes onto the screen.
    def draw(self):
        # Same thing as with the platform class.
        screen_x = int(self.world_x - player.cam_x + window_width / 2)
        screen_y = int(self.world_y - player.cam_y + window_height / 2)
        for small_width in range(self.total_width):
            game_window.blit(self.spikes_image, (screen_x + 100 * small_width, screen_y))

# Set up all platforms in a list.
platforms = [
    Platform(0, 1773, 3200, 50),
    Platform(1900, 1723, 200, 50),
    Platform(1100, 1723, 200, 50),
    Platform(1500, 1573, 200, 50),
    Platform(1050, 1423, 200, 50),
    Platform(2000, 1423, 200, 50),
    Platform(1500, 1223, 200, 50),
    Platform(400, 1523, 500, 50),
    Platform(200, 1673, 100, 50),
    Platform(2400, 1223, 400, 50),
    Platform(2800, 1323, 200, 50),
    Platform(3000, 1223, 100, 50),
    Platform(3100, 1123, 100, 50),
    Platform(2800, 923, 200, 50),
    Platform(2200, 823, 200, 50),
    Platform(1800, 623, 200, 50),
    Platform(100, 1323, 200, 50)
    ]

# Set up all spikes into a list.
spikes_list = [Spikes(1300, 1723, 600, 50), Spikes(2800, 1273, 200, 50)]

# Set up the ghosts list. (empty for now but gets filled in the main loop)
ghosts = []

# Set window_state to home_screen to start.
window_state = home_screen

# Game Loop.
game_running = False
while True:
    if window_state == home_screen: # If on home_screen, show the menu.
        run_menu_loop()

    if window_state == game_window: # if on game_window, run the game.
        game_running = True

        mouse_pos = pygame.mouse.get_pos() # Set click actions to False before checking for clicks.
        click = False

        # Update player and draw the background and other objects.
        player.update()
        if not paused:
            # Background
            game_window.blit(background, (-player.cam_x + window_width // 2, -player.cam_y + window_height // 2))
            # Platforms
            for platform in platforms:
                platform.draw()
                # Spikes
                for spikes in spikes_list:
                    spikes.draw()
                    if spikes.rect.colliderect(player.rect):
                        player.take_damage(0.2)
            player.draw()
            
            if level_text_alpha > 0: # This shows which level you are on when you start and fades away.
                draw_text(f'Level {level}', 'Creepster-Regular.ttf', 150, white, level_text_screen, window_width // 2, window_height // 2, 'center')
                level_text_alpha -= 3
                level_text_screen.set_alpha(level_text_alpha)
                game_window.blit(level_text_screen, (0, 0))

            # This controls ghost spawning. (different ghosts for each level for difficulty)
            if game_tick_num % spawn_speed == 0:
                if level == 1:
                    for _ in range(2):
                        ghosts.append(Ghost(random.randint(0, map_width - 20), random.randint(0, map_height - 20), 1))
                    for _ in range(2):
                        ghosts.append(Ghost(random.randint(0, map_width - 20), random.randint(0, map_height - 20), 2))
                if level == 2:
                    for _ in range(2):
                        ghosts.append(Ghost(random.randint(0, map_width - 20), random.randint(0, map_height - 20), 2))
                    for _ in range(2):
                        ghosts.append(Ghost(random.randint(0, map_width - 20), random.randint(0, map_height - 20), 3))
                if level == 3:
                    ghosts.append(Ghost(random.randint(0, map_width - 20), random.randint(0, map_height - 20), 2))
                    for _ in range(1):
                        ghosts.append(Ghost(random.randint(0, map_width - 20), random.randint(0, map_height - 20), 3))
                    for _ in range(2):
                        ghosts.append(Ghost(random.randint(0, map_width - 20), random.randint(0, map_height - 20), 4))

            game_tick_num += 1

            # Update and draw ghosts.
            for ghost in ghosts:
                ghost.update()
                ghost.draw('ghost')
            for ghost in ghosts[:]: # Two ghost list actions so that it draws the health bar on top of other ghost rects in case of overlap.
                ghost.draw('health')
                if ghost.health <= 0:
                    ghosts.remove(ghost)
                    player.score += 5 * ghost.type

            # Draw the pause button and register if it's clicked.
            pause_button.draw()
            if pause_button.is_clicked(mouse_pos, click):
                # Then draw unpause button and blur the screen.
                unpause_button.draw()
                home_button.draw()
                blur_background_screen.fill((0, 0, 0, 100))
                blur_background_screen.blit(paused_game_screen, (0, 0))
                game_window.blit(blur_background_screen, (0, 0))
                paused = True

        # If paused and player navigates back home, stop the music and play the menu music. (on repeat)
        if paused:
            if unpause_button.is_clicked(mouse_pos, click):
                paused = False
            if home_button.is_clicked(mouse_pos, click):
                pygame.mixer.music.stop()
                pygame.mixer.music.load('game_menu_music.mp3')
                pygame.mixer.music.play(-1)
                window_state = home_screen
                paused = False

        # If game stops running (by player death):
        if not game_running:
            
            # Reset some variables. 
            level_text_screen.fill((0, 0, 0, 0))
            level_text_alpha = 255
            
            # Set to menu music.
            pygame.mixer.music.stop()
            pygame.mixer.music.load('game_menu_music.mp3')
            pygame.mixer.music.play(-1)

            # Enter scores in leaderboard files. (depending on level)
            if level == 1:
                level_1_complete = True
                with open('leaderboard_level_1.txt', 'a') as file:
                    file.write(f'{player_name} {player.score}\n')
            if level == 2:
                level_2_complete = True
                with open('leaderboard_level_2.txt', 'a') as file:
                    file.write(f'{player_name} {player.score}\n')
            if level == 3:
                level_3_complete = True
                with open('leaderboard_level_3.txt', 'a') as file:
                    file.write(f'{player_name} {player.score}\n')

            # Run the game_over function.
            window_state = game_over_screen
            game_over(level)

    # Update screen and ticks.
    window.blit(window_state, (0, 0))
    pygame.display.update()
    clock.tick(FPS)
