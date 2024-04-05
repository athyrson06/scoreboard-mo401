import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the display
screen_width = 640
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Hello, World!')

# Set up the colors
black = (0, 0, 0)
white = (255, 255, 255)

# Set up the font
font = pygame.font.Font(None, 74)
text = font.render('Hello, World!', True, white, black)

# Text position
text_rect = text.get_rect()
text_rect.center = (screen_width // 2, screen_height // 2)

# The game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the screen with black
    screen.fill(black)

    # Draw the text onto the screen
    screen.blit(text, text_rect)

    # Update the display
    pygame.display.flip()

# Clean up and quit
pygame.quit()
sys.exit()
