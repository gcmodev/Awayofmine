import pygame
import sys
import os # We need this to read files from folders

# --- Player Class ---
# This class now features a dynamic animation system.
class Player:
    def __init__(self, x, y):
        # --- Animation Discovery System ---
        self.animation_path = 'art/player'
        self.animations = self.discover_animations(self.animation_path)
        
        # --- Player State ---
        self.action = 'breathing-idle'
        self.direction = 'south' # Default direction
        self.current_frame = 0
        self.animation_speed = 0.1 # How fast the animation plays. Adjust this value!
        
        # Set initial image. Error handling for missing animations.
        try:
            self.image = self.animations[self.action][self.direction][self.current_frame]
        except KeyError:
            print(f"ERROR: Default animation '{self.action}/{self.direction}' not found!")
            self.image = pygame.Surface((32, 32)); self.image.fill((255, 0, 255))

        # --- Position and Movement ---
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 4
        self.pos = pygame.math.Vector2(self.rect.center)

    def discover_animations(self, path):
        """ Scans the provided path and automatically loads all animation folders. """
        animations = {}
        try:
            for action_folder in os.listdir(path):
                action_path = os.path.join(path, action_folder)
                if os.path.isdir(action_path):
                    animations[action_folder] = {}
                    for direction_folder in os.listdir(action_path):
                        direction_path = os.path.join(action_path, direction_folder)
                        if os.path.isdir(direction_path):
                            frames = []
                            # Find all pngs, sort them by the number in their filename
                            try:
                                frame_files = sorted(
                                    [f for f in os.listdir(direction_path) if f.endswith('.png')],
                                    key=lambda f: int(f.split('_')[-1].split('.')[0])
                                )
                                for frame_file in frame_files:
                                    full_path = os.path.join(direction_path, frame_file)
                                    frames.append(pygame.image.load(full_path).convert_alpha())
                                
                                if frames: # Only add if frames were found
                                    animations[action_folder][direction_folder] = frames
                            except (ValueError, IndexError):
                                print(f"Warning: Could not sort frames in '{direction_path}'. Ensure they are named 'frame_000.png', etc.")

        except FileNotFoundError:
             print(f"ERROR: Player art path not found at '{path}'")
        return animations

    def update(self):
        """ Handles player input, movement, and animation state changes. """
        last_action = self.action
        last_direction = self.direction

        # --- Input and Direction Mapping ---
        keys = pygame.key.get_pressed()
        move_vector = pygame.math.Vector2(0, 0)
        
        if keys[pygame.K_w]:
            move_vector.y = -1
        if keys[pygame.K_s]:
            move_vector.y = 1
        if keys[pygame.K_a]:
            move_vector.x = -1
        if keys[pygame.K_d]:
            move_vector.x = 1

        # Determine direction string from move vector
        if move_vector.length_squared() > 0: # <-- CORRECTED THIS LINE
            self.action = 'walk' # Assuming you have a 'walk' folder
            move_vector.normalize_ip()

            if move_vector.y < -0.5:
                self.direction = 'north'
                if move_vector.x > 0.5: self.direction = 'north-east'
                elif move_vector.x < -0.5: self.direction = 'north-west'
            elif move_vector.y > 0.5:
                self.direction = 'south'
                if move_vector.x > 0.5: self.direction = 'south-east'
                elif move_vector.x < -0.5: self.direction = 'south-west'
            else:
                if move_vector.x > 0.5: self.direction = 'east'
                elif move_vector.x < -0.5: self.direction = 'west'
        else:
            self.action = 'breathing-idle'

        # --- Movement ---
        self.pos += move_vector * self.speed
        self.rect.center = self.pos

        # --- Animation ---
        # Reset frame index if state changed
        if self.action != last_action or self.direction != last_direction:
            self.current_frame = 0

        # Advance the frame
        self.current_frame += self.animation_speed
        
        # Check if the current animation exists before trying to play it
        if self.action in self.animations and self.direction in self.animations[self.action]:
            animation_frames = self.animations[self.action][self.direction]
            if self.current_frame >= len(animation_frames):
                self.current_frame = 0 # Loop the animation
            
            self.image = animation_frames[int(self.current_frame)]
        else:
            # If a specific animation is missing (e.g. 'walk/north-east'), do nothing
            # Or you could have a fallback here
            pass

# --- Game Class (No changes needed here) ---
class Game:
    def __init__(self):
        # --- Core Engine Initialization ---
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("A Way of Mine - Engine v0.4")
        self.clock = pygame.time.Clock()

        # --- Game Objects ---
        self.player = Player(400, 300)

        # --- World Objects for Camera Demo ---
        self.world_objects = []
        for i in range(20):
            dot_surface = pygame.Surface((8, 8))
            dot_surface.fill((0, 255, 0))
            dot_rect = dot_surface.get_rect(center=(i * 150, (i % 4) * 200))
            self.world_objects.append((dot_surface, dot_rect))
        
        self.camera_offset = pygame.math.Vector2(0, 0)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.player.update()
            
            self.camera_offset.x = self.player.rect.centerx - self.screen_width // 2
            self.camera_offset.y = self.player.rect.centery - self.screen_height // 2

            self.screen.fill((50, 50, 50))

            for dot_surf, dot_rect in self.world_objects:
                screen_pos = dot_rect.topleft - self.camera_offset
                self.screen.blit(dot_surf, screen_pos)

            player_screen_pos = self.player.rect.topleft - self.camera_offset
            self.screen.blit(self.player.image, player_screen_pos)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game()
    game.run()
