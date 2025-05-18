## Pygame - Random Fractals in 2D
## Author: Alexander Art

import pygame, math, random


# SETTINGS

# Change screen settings here. Use ESC to close the program if in fullscreen.
FULLSCREEN_MODE = False
DISPLAY_RESOLUTION = (768, 432)

# Maximum number of branches per tree
MAX_BRANCH_COUNT = 1000000

# Minimum branch size before a branch stops branching out.
# The branch "size" is a variable that coorelates with the branch depth. (The branch depth isn't actually calculated. It is all based on the "size" variable.)
MINIMUM_BRANCH_SIZE = 0.0003 # Value between 0 and 1 (should be close to 0).

# Set fractal presets here.
presets = [
    3,          # Branch width
    0.3,        # How much the branch width is affected by the branch size (branch size starts at 1 and decreases the smaller the branch gets)
    15,         # Average branch length (at maximum size)
    5,          # Standard deviation of the branch length (at maximum size)
    0.3,        # How much the branch length is affected by the branch size
    math.pi/6,  # Average angle between new branches (at maximum size)
    math.pi/8,  # Standard deviation of the angle between new branches (at maximum size)
    0           # How much the angle between new branches is affected by branch size
]



pygame.init()
pygame.display.set_caption('Random Fractals in 2D')
display = pygame.display.set_mode(DISPLAY_RESOLUTION, pygame.SCALED + pygame.FULLSCREEN * FULLSCREEN_MODE)

# "Tree" object that keeps track of and generates all the branches of a self-similar fractal
class Tree:
    def __init__(self, surface, initial_pos, initial_direction, branch_width, branch_width_factor, branch_length_mean, branch_length_range, branch_length_factor, branch_angle_mean, branch_angle_range, branch_angle_factor):
        # surface - Surface to render the branches on
        # initial_pos - Position of the first branch
        # initial_direction - Direction of the first branch
        # branch_width - Initial branch width
        # branch_width_factor - How much branch size affects branch_width
        # branch_length_mean - Mean distance before the branch splits
        # branch_length_range - Std. dev. of branch_length_mean
        # branch_length_factor - How much branch size affects branch_length_mean and branch_length_range 
        # branch_angle_mean - Mean angle between split branches
        # branch_angle_range - Std. dev. of branch_angle_mean 
        # branch_angle_factor - How much branch size affects branch_angle_mean and branch_angle_range

        self.surface = surface
        
        self.branch_width = branch_width
        self.branch_width_factor = branch_width_factor
        self.branch_length_mean = branch_length_mean
        self.branch_length_range = branch_length_range
        self.branch_length_factor = branch_length_factor 
        self.branch_angle_mean = branch_angle_mean
        self.branch_angle_range = branch_angle_range 
        self.branch_angle_factor = branch_angle_factor

        # The first, initial branch that splits off into all the others (acts like a sprout)
        self.branches = [Branch(self, 0, initial_pos, 1, random.gauss(branch_length_mean, branch_length_range), initial_direction)]

    # Create two new branches.
    def branch_split(self, index, pos, prev_size, prev_direction):
        self.branches[index] = None

        proportion = random.gauss(0, 0.1)
        if proportion < 0:
            proportion = 1 + proportion
        proportion = max(min(proportion, 1), 0)

        branch_1_size = prev_size * proportion
        branch_2_size = prev_size * (1 - proportion)

        branch_1_length = random.gauss(self.branch_length_mean, self.branch_length_range) * (branch_1_size ** self.branch_length_factor)
        branch_2_length = random.gauss(self.branch_length_mean, self.branch_length_range) * (branch_2_size ** self.branch_length_factor)

        angle = random.gauss(self.branch_angle_mean, self.branch_angle_range) * (prev_size ** self.branch_angle_factor)
        branch_1_angle = prev_direction - angle * (1 - proportion)
        branch_2_angle = prev_direction + angle * proportion
        
        new_branch_1 = Branch(self, len(self.branches), pos, branch_1_size, branch_1_length, branch_1_angle)
        new_branch_2 = Branch(self, len(self.branches) + 1, pos, branch_2_size, branch_2_length, branch_2_angle)

        # Append the new branches to the end of the current branch list.
        self.branches.append(new_branch_1)
        self.branches.append(new_branch_2)

# "Branch" object that exists as part of a tree
class Branch:
    def __init__(self, parent, index, pos, branch_size, branch_length, branch_direction):
        # parent - Parent object (Tree)
        # index - Position of self in parent branches list
        # pos - Position of branch on screen
        # branch_size - Branch size, factor for many variables
        # branch_length - How long the branch will travel before splitting
        # branch_direction - Direction that this branch travels
        self.parent = parent
        self.index = index
        self.pos = pos
        self.branch_size = branch_size
        self.branch_length = branch_length
        self.branch_direction = branch_direction

    # When this function is called, the branch extends and splits off into two new branches.
    def activate(self):
        dx = math.cos(self.branch_direction) * self.branch_length
        dy = math.sin(self.branch_direction) * self.branch_length
        final_pos = [self.pos[0] + dx, self.pos[1] + dy]
        self.draw(self.parent.surface, [255, 255, 255], self.pos, final_pos, self.parent.branch_width * (self.branch_size ** self.parent.branch_width_factor))
        if self.branch_size > MINIMUM_BRANCH_SIZE:
            self.parent.branch_split(self.index, final_pos, self.branch_size, self.branch_direction)

    def draw(self, surface, color, pos1, pos2, width):
        if width < 1:
            color[0] *= width
            color[1] *= width
            color[2] *= width
            width = 1
        pygame.draw.line(surface, color, pos1, pos2, int(width))

# Class for button UI elements
class Button:
    def __init__(self, rect, action, text):
        self.rect = pygame.Rect(rect)
        self.action = action
        self.text = text

    def render(self, surface, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            color = (63, 127, 255)
        else:
            color = (0, 0, 63)
            
        pygame.draw.rect(surface, color, self.rect)
        
        surface.blit(font_large.render(self.text, True, (255, 255, 255)), (self.rect.x + 4, self.rect.y + 3))

    def left_mouse_down(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.action()

# Creates a new tree
def generate_tree(surface, pos, angle, presets):
    tree = Tree(surface, pos, angle, presets[0], presets[1], presets[2], presets[3], presets[4], presets[5], presets[6], presets[7])
    for i in range(MAX_BRANCH_COUNT):
        try:
            tree.branches[i].activate()
        except IndexError:
            break

# Clears the fractal surface
def clear_screen():
    fractal_surface.fill((0, 0, 0))

# Saves an image of the fractal surface
def save_image():
    global image_name
    image_name = str(random.random())[2:12] + ".png"
    pygame.image.save(fractal_surface, 'pygame_fractals_saved_screenshots/' + image_name)


font_large = pygame.font.Font(None, 16)
font_small = pygame.font.Font(None, 12) # Unused

# Pygame surface that the fractals are drawn on.
fractal_surface = pygame.Surface(display.get_size())

# Initial angle of the mouse pointer.
angle = 0

# Controls panel that displays the controls message and the two buttons. (Can be dragged around!)
controls_surface = pygame.Surface((120, 260))
controls_surface_pos = [600, 60]
controls_surface_dragged = False

# Clear screen button that appears in the controls panel.
clear_screen_button = Button((10, 200, 100, 16), clear_screen, "Clear Screen")

# Screenshot button that appears in the controls panel.
screenshot_button = Button((10, 225, 100, 16), save_image, "Save Screenshot")
image_name = ""

# List of button objects.
buttons = [
    clear_screen_button,
    screenshot_button
]


running = True
while running:

    # INPUT
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]:
            running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Detect if the controls panel is being dragged.
                if pygame.Rect(controls_surface_pos, (controls_surface.get_width(), 16)).collidepoint(pygame.mouse.get_pos()):
                    controls_surface_dragged = True

                # Detect if a button is pressed.
                for button in buttons:
                    button.left_mouse_down((pygame.mouse.get_pos()[0] - controls_surface_pos[0], pygame.mouse.get_pos()[1] - controls_surface_pos[1]))

                # If the screen is pressed anywhere except the controls panel, then draw a fractal.
                if not pygame.Rect(controls_surface_pos, controls_surface.get_size()).collidepoint(pygame.mouse.get_pos()):
                    generate_tree(fractal_surface, pygame.mouse.get_pos(), angle, presets)
                    
        if event.type == pygame.MOUSEBUTTONUP:
            controls_surface_dragged = False

    # If button R is being held, rotate the initial fractal direction.
    if pygame.key.get_pressed()[pygame.K_r]:
        angle -= 2 * math.pi / 60

    # If the controls panel is being dragged, make it follow the mouse movement.
    mouse_rel = pygame.mouse.get_rel()
    if controls_surface_dragged:
        controls_surface_pos[0] += mouse_rel[0]
        controls_surface_pos[1] += mouse_rel[1]


    # RENDERING

    display.fill((0, 0, 0))
    
    display.blit(fractal_surface, (0, 0))

    # Draw the arrow unless the mouse is over the controls panel.
    if not pygame.Rect(controls_surface_pos, controls_surface.get_size()).collidepoint(pygame.mouse.get_pos()):
        pygame.draw.line(display, (255, 0, 0), pygame.mouse.get_pos(), (pygame.mouse.get_pos()[0] + math.cos(angle) * 10, pygame.mouse.get_pos()[1] + math.sin(angle) * 10))
        pygame.draw.line(display, (255, 0, 0), (pygame.mouse.get_pos()[0] + math.cos(angle) * 10, pygame.mouse.get_pos()[1] + math.sin(angle) * 10), (pygame.mouse.get_pos()[0] + math.cos(angle - 0.4) * 8, pygame.mouse.get_pos()[1] + math.sin(angle - 0.4) * 8))
        pygame.draw.line(display, (255, 0, 0), (pygame.mouse.get_pos()[0] + math.cos(angle) * 10, pygame.mouse.get_pos()[1] + math.sin(angle) * 10), (pygame.mouse.get_pos()[0] + math.cos(angle + 0.4) * 8, pygame.mouse.get_pos()[1] + math.sin(angle + 0.4) * 8))

    # Render the controls surface.
    controls_surface.fill((0, 63, 127))

    pygame.draw.rect(controls_surface, (255, 255, 255), ((0, 0), (controls_surface.get_width(), 16)))
    controls_surface.blit(font_large.render("Controls", True, (0, 0, 0)), (4, 3))

    controls_surface.blit(font_large.render("Click on screen", True, (255, 255, 255)), (10, 26))
    controls_surface.blit(font_large.render("to generate new", True, (255, 255, 255)), (10, 40))
    controls_surface.blit(font_large.render("fractals.", True, (255, 255, 255)), (10, 54))
    
    controls_surface.blit(font_large.render("Hold R to change", True, (255, 255, 255)), (10, 74))
    controls_surface.blit(font_large.render("initial fractal", True, (255, 255, 255)), (10, 88))
    controls_surface.blit(font_large.render("direction.", True, (255, 255, 255)), (10, 102))

    controls_surface.blit(font_large.render("Open the Python", True, (255, 255, 255)), (10, 122))
    controls_surface.blit(font_large.render("file to change the", True, (255, 255, 255)), (10, 136))
    controls_surface.blit(font_large.render("fractal presets.", True, (255, 255, 255)), (10, 150))

    controls_surface.blit(font_large.render("Press ESC to exit.", True, (255, 255, 255)), (10, 170))

    controls_surface.blit(font_large.render(image_name, True, (255, 255, 255)), (10, 245))
    
    for button in buttons:
        button.render(controls_surface, (pygame.mouse.get_pos()[0] - controls_surface_pos[0], pygame.mouse.get_pos()[1] - controls_surface_pos[1]))

    display.blit(controls_surface, controls_surface_pos)

    # Update the display.
    pygame.display.update()
    pygame.time.Clock().tick(60)

pygame.quit()
