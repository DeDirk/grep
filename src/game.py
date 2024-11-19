import random
import math

import pygame
from pygame.locals import *

from src.constants import (
    COLORS,
    WINDOW,
    LEVEL,
    ITEMS,
    PLAYER,
    ENEMY
)
from src.camera import Camera
from src.entities.enemy import Enemy
from src.entities.player import Player
from src.entities.projectile import Projectile
from src.items.item import Item
from src.level_generator import LevelGenerator
from src.utils.collision import (
    handle_projectile_enemy_collision,
    handle_projectile_player_collision,
    handle_player_enemy_collision,
    handle_projectile_projectile_collision,
    handle_item_player_collision,
    handle_projectile_wall_collision
)
from src.effects.effect_manager import EffectManager
from src.settings import Settings

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW['WIDTH'], WINDOW['HEIGHT']))
        self.clock = pygame.time.Clock()
        self.running = True

        # Game objects
        self.player = Player(self)
        self.enemy = Enemy(self)
        self.projectiles = []
        self.items = []
        self.level_generator = LevelGenerator(WINDOW['WIDTH'], WINDOW['HEIGHT'])

        # Game settings
        self.settings = Settings()
        self.item_spawn_chance = ITEMS['SPAWN']['CHANCE']
        
        # Camera
        self.camera = Camera()

        # Add effect manager
        self.effect_manager = EffectManager()

    def update(self):
        """Main game update loop"""
        if not self.player.died:
            visible_walls = self.level_generator.get_visible_walls(self.camera.x, self.camera.y)
            
            self.player.move(visible_walls)
            new_projectiles = self.enemy.move(self.player.rect.center, visible_walls)
            if new_projectiles:
                self.projectiles.extend(new_projectiles)
            self.update_items()
            self.spawn_items()
            
            self.update_projectiles()
            
            # Check player-enemy collision
            handle_player_enemy_collision(self.player, self.enemy)
            
            self.camera.update(self.player.rect)
            self.level_generator.update(self.camera.x, self.camera.y)
            self.effect_manager.update()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(WINDOW['FPS'])

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            
            # Check for key press to toggle dark mode
            if event.type == KEYDOWN:
                if event.key == K_l:  # 'L' key is used to toggle dark mode
                    self.settings.toggle_dark_mode()
            
        # Check controller start button for dark mode toggle
        if self.player.controls.get_menu_press():  # Use new method
            self.settings.toggle_dark_mode()
        
        if self.player.controls.is_shooting():
            projectile = self.player.shoot((self.camera.x, self.camera.y))
            self.projectiles.append(projectile)
        #     if projectile.using_controller:
        #         self.player.controls.start_rumble()
        
        # self.player.controls.update_rumble()
        

    def update_projectiles(self):
        """Update all projectiles and handle collisions"""
        visible_walls = self.level_generator.get_visible_walls(self.camera.x, self.camera.y)
        
        # Update all projectiles
        i = 0
        while i < len(self.projectiles):
            projectile = self.projectiles[i]
            projectile.move()
            
            # Check collision with walls
            for wall in visible_walls:
                if handle_projectile_wall_collision(projectile, wall, self):
                    break
            
            # Check collision with other projectiles
            j = 0
            while j < len(self.projectiles):
                if i != j:  # Don't compare projectile with itself
                    other_projectile = self.projectiles[j]
                    if (not projectile.from_enemy and 
                        other_projectile.from_enemy and 
                        handle_projectile_projectile_collision(projectile, other_projectile)):
                        # Remove player projectile
                        if projectile in self.projectiles:
                            self.projectiles.remove(projectile)
                            i -= 1
                        # Shrink enemy projectile
                        other_projectile.radius *= other_projectile.shrink_rate
                        if other_projectile.radius <= other_projectile.min_size:
                            if other_projectile in self.projectiles:
                                self.projectiles.remove(other_projectile)
                                if j < i:
                                    i -= 1
                        else:
                            other_projectile.update_rect_size()
                        break
                j += 1
            
            # Skip remaining checks if projectile was removed
            if projectile not in self.projectiles:
                i += 1
                continue
            
            # Check collision with enemy (if player projectile)
            if not projectile.from_enemy:
                if handle_projectile_enemy_collision(projectile, self.enemy, self.effect_manager):
                    if projectile in self.projectiles:
                        self.projectiles.remove(projectile)
                    continue
            
            # Check collision with player (if enemy projectile)
            if projectile.from_enemy:
                should_remove = handle_projectile_player_collision(projectile, self.player)
                if should_remove and projectile in self.projectiles:
                    self.projectiles.remove(projectile)
                    continue
            
            # Remove if off screen
            if projectile.is_off_screen(self.camera):
                if projectile in self.projectiles:
                    self.projectiles.remove(projectile)
            i += 1

    def update_items(self):
        for item in self.items[:]:
            item.update()
            if handle_item_player_collision(item, self.player):
                item.apply_effect(self.player)
                self.items.remove(item)
            elif item.should_despawn(self.camera):
                self.items.remove(item)
                
    def spawn_items(self):
        if random.random() < self.item_spawn_chance:
            current_chunk = self.level_generator.get_chunk_coords(self.camera.x, self.camera.y)
            
            # Randomly select a chunk within the generation radius
            chunk_x = random.randint(
                current_chunk[0] - LEVEL['CHUNK_GENERATION_RADIUS'],
                current_chunk[0] + LEVEL['CHUNK_GENERATION_RADIUS']
            )
            chunk_y = random.randint(
                current_chunk[1] - LEVEL['CHUNK_GENERATION_RADIUS'],
                current_chunk[1] + LEVEL['CHUNK_GENERATION_RADIUS']
            )
            
            chunk_coords = (chunk_x, chunk_y)
            if chunk_coords not in self.level_generator.chunks:
                return
            
            chunk_world_x = chunk_x * WINDOW['WIDTH']
            chunk_world_y = chunk_y * WINDOW['HEIGHT']
            
            # Try to find a valid spawn position
            max_attempts = 10
            for _ in range(max_attempts):
                padding = 20
                random_pos = (
                    random.randint(int(chunk_world_x + padding), 
                                 int(chunk_world_x + WINDOW['WIDTH'] - padding)),
                    random.randint(int(chunk_world_y + padding), 
                                 int(chunk_world_y + WINDOW['HEIGHT'] - padding))
                )
                
                # Check if position is too close to other items
                too_close = False
                for item in self.items:
                    dx = random_pos[0] - item.rect.centerx
                    dy = random_pos[1] - item.rect.centery
                    distance = (dx * dx + dy * dy) ** 0.5
                    if distance < item.occupied_space:
                        too_close = True
                        break
                
                # Check if position collides with walls
                test_rect = pygame.Rect(
                    random_pos[0] - padding,
                    random_pos[1] - padding,
                    padding * 2,
                    padding * 2
                )
                wall_collision = False
                for wall in self.level_generator.chunks[chunk_coords]:
                    if wall.colliderect(test_rect):
                        wall_collision = True
                        break
                    
                if not too_close and not wall_collision:
                    self.items.append(Item(random_pos))
                    # print(f"Spawned stamina item at position {random_pos}")
                    break

    def render(self):
        self.screen.fill(COLORS['WHITE'])
        
        # Get only the visible walls
        visible_walls = self.level_generator.get_visible_walls(self.camera.x, self.camera.y)
        
        # Draw visible walls
        for wall in visible_walls:
            wall_rect = self.camera.apply(wall)
            pygame.draw.rect(self.screen, COLORS['BLACK'], wall_rect)
        
        # Apply camera offset to all game objects
        player_rect = self.camera.apply(self.player.rect)
        enemy_rect = self.camera.apply(self.enemy.rect)
        
        self.screen.blit(self.enemy.image, enemy_rect)
        self.screen.blit(self.player.image, player_rect)
        
        # Draw stamina bar
        self.player.draw_stamina_bar(self.screen, self.camera)
        # draw health bar
        self.player.draw_health_bar(self.screen, self.camera)
        
        for projectile in self.projectiles:
            proj_rect = self.camera.apply(projectile.rect)
            self.screen.blit(projectile.image, proj_rect)
            
        for item in self.items:
            item_rect = self.camera.apply(item.rect)
            self.screen.blit(item.image, item_rect)
            
        # Draw effects after game objects so they appear on top
        self.effect_manager.draw(self.screen, self.camera.x, self.camera.y)
        
        if self.player.died:
            self.render_game_over()
            
        pygame.display.update()
        
    def render_game_over(self):
        font = pygame.font.SysFont("Verdana", 60)
        game_over = font.render("you died fuckface", True, COLORS['RED'])
        self.screen.blit(game_over, (random.randint(27, 30), random.randint(247,250)))
        game_over_2 = font.render("!!!!!!!!!", True, COLORS['RED'])
        self.screen.blit(game_over_2, (random.randint(60, 70), random.randint(307,310)))
        game_over_3 = font.render("!!!!!!!!!", True, COLORS['RED'])
        self.screen.blit(game_over_3, (random.randint(60, 70), random.randint(197,200)))
        