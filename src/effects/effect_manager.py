import pygame
import math
import random
import traceback
from typing import List
from .particle import Particle
from src.constants import COLORS, EFFECTS

class EffectManager:
    def __init__(self):
        self.particles: List[Particle] = []
    
    def update(self):
        self.particles = [p for p in self.particles if p.update()]
    
    def draw(self, surface: pygame.Surface, camera_x: int = 0, camera_y: int = 0):
        for particle in self.particles[:]:
            try:
                if not isinstance(particle.color, (tuple, list)) or len(particle.color) not in (3, 4):
                    print(f"""Invalid particle detected:
                        Position: ({particle.x:.2f}, {particle.y:.2f})
                        Color: {particle.color}
                        Speed: {particle.speed}
                        Lifetime: {particle.lifetime}
                        Size: {particle.size}
                        Created by: {traceback.extract_stack()[-2][2]}""")
                    self.particles.remove(particle)
                    continue
                particle.draw(surface, camera_x, camera_y)
            except Exception as e:
                print(f"""Error drawing particle:
                    Error: {str(e)}
                    Position: ({particle.x:.2f}, {particle.y:.2f})
                    Color: {particle.color}
                    Speed: {particle.speed}
                    Lifetime: {particle.lifetime}
                    Size: {particle.size}
                    Created by: {traceback.extract_stack()[-2][2]}""")
                self.particles.remove(particle)
    
    def create_boost_effect(self, x: float, y: float, direction: float):
        opposite_direction = direction + math.pi
        spread = math.radians(EFFECTS['BOOST']['SPREAD'])
        
        for _ in range(EFFECTS['BOOST']['PARTICLE_COUNT']):
            angle = opposite_direction + random.uniform(-spread, spread)
            speed = random.uniform(*EFFECTS['BOOST']['SPEED'])
            lifetime = random.randint(*EFFECTS['BOOST']['LIFETIME'])
            
            particle = Particle(x, y, COLORS['GRAY'], speed, angle, lifetime, size=(random.uniform(0.5, 3)))
            self.particles.append(particle)
    
    def create_wall_hit_effect(self, x: float, y: float, wall_normal: float):
        num_particles = random.randint(*EFFECTS['WALL_HIT']['PARTICLE_COUNT'])
        spread = math.radians(EFFECTS['WALL_HIT']['SPREAD'])
        
        for _ in range(num_particles):
            angle = wall_normal + random.uniform(-spread, spread)
            speed = random.uniform(*EFFECTS['WALL_HIT']['SPEED'])
            lifetime = random.randint(*EFFECTS['WALL_HIT']['LIFETIME'])
            size = random.uniform(0.5, 1.5)
            
            particle = Particle(x, y, COLORS['DARKGREY'], speed, angle, lifetime, size)
            self.particles.append(particle)
    
    def create_phase_change_effect(self, x: float, y: float):
        num_particles = EFFECTS['PHASE_CHANGE']['PARTICLE_COUNT']
        spiral_tightness = 0.5
        base_speed = 3
        
        # Use RGB color without alpha - let Particle handle alpha
        particle_color = COLORS['RED']  # This should be (255, 0, 0)
        
        for i in range(num_particles):
            angle = i * (2 * math.pi / num_particles)
            distance = i * spiral_tightness
            
            start_x = x + math.cos(angle) * distance
            start_y = y + math.sin(angle) * distance
            
            # Outward particle
            particle = Particle(start_x, start_y, COLORS['PURPLE'], 
                              base_speed, angle, 
                              EFFECTS['PHASE_CHANGE']['LIFETIME'], size=5)
            self.particles.append(particle)
            
            # Inward particle (delayed)
            inward_particle = Particle(start_x, start_y, COLORS['PURPLE'],
                                     base_speed, angle + math.pi, 
                                     EFFECTS['PHASE_CHANGE']['LIFETIME'], size=8)
            # Add the delay to the lifetime
            inward_particle.lifetime = EFFECTS['PHASE_CHANGE']['LIFETIME']
            inward_particle.original_lifetime = inward_particle.lifetime + EFFECTS['PHASE_CHANGE']['INWARD_DELAY']
            self.particles.append(inward_particle)
    
    def create_movement_change_effect(self, x: float, y: float):
        num_particles = EFFECTS['MOVEMENT_CHANGE']['PARTICLE_COUNT']
        for i in range(num_particles):
            angle = i * (2 * math.pi / num_particles)
            
            particle = Particle(x, y, COLORS['RED'], 
                              EFFECTS['MOVEMENT_CHANGE']['SPEED'],
                              angle, EFFECTS['MOVEMENT_CHANGE']['LIFETIME'], size=4)
            self.particles.append(particle)
    