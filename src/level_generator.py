import pygame
import random
import threading
from queue import Queue
from typing import Dict, List, Set, Tuple

from src.constants import (
    WINDOW,
    LEVEL
)

class LevelGenerator:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.min_room_size = LEVEL['ROOM']['MIN_SIZE']
        self.wall_thickness = LEVEL['WALL']['THICKNESS']
        
        # Dictionary to store walls by chunk coordinates
        self.chunks: Dict[Tuple[int, int], List[pygame.Rect]] = {}
        self.chunk_size = (WINDOW['WIDTH'], WINDOW['HEIGHT'])
        
        # Generate spawn room at screen center
        spawn_chunk = (0, 0)
        self.chunks[spawn_chunk] = self.generate_spawn_room()
        
        # Threading setup
        self.generation_queue = Queue()
        self.processing_chunks: Set[Tuple[int, int]] = set()
        self.generation_thread = threading.Thread(target=self._generation_worker, daemon=True)
        self.generation_thread.start()
    
    def get_chunk_coords(self, x: float, y: float) -> Tuple[int, int]:
        """Convert world coordinates to chunk coordinates"""
        chunk_x = int(x // self.chunk_size[0])
        chunk_y = int(y // self.chunk_size[1])
        return (chunk_x, chunk_y)
    
    def update(self, camera_x: float, camera_y: float):
        """Check if new chunks need to be generated"""
        current_chunk = self.get_chunk_coords(camera_x, camera_y)
        
        # Check chunks in generation radius
        for dx in range(-LEVEL['CHUNK_GENERATION_RADIUS'], LEVEL['CHUNK_GENERATION_RADIUS'] + 1):
            for dy in range(-LEVEL['CHUNK_GENERATION_RADIUS'], LEVEL['CHUNK_GENERATION_RADIUS'] + 1):
                chunk_coords = (current_chunk[0] + dx, current_chunk[1] + dy)
                
                # Skip if chunk already exists or is being processed
                if chunk_coords in self.chunks or chunk_coords in self.processing_chunks:
                    continue
                    
                # Add new chunk to generation queue
                # print(f"Queueing new chunk {chunk_coords} for generation")
                self.processing_chunks.add(chunk_coords)
                self.generation_queue.put(chunk_coords)
    
    def _generation_worker(self):
        """Background worker that generates new chunks"""
        while True:
            try:
                chunk_coords = self.generation_queue.get()
                if chunk_coords is None:
                    break
                
                # Skip if chunk was already generated while in queue
                if chunk_coords in self.chunks:
                    self.processing_chunks.remove(chunk_coords)
                    self.generation_queue.task_done()
                    continue
                    
                # print(f"Worker starting generation of chunk {chunk_coords}")
                
                # Generate walls for this chunk
                chunk_x, chunk_y = chunk_coords
                chunk_walls = self._generate_chunk_walls(
                    chunk_x * self.chunk_size[0],
                    chunk_y * self.chunk_size[1]
                )
                
                # Store the generated walls
                self.chunks[chunk_coords] = chunk_walls
                self.processing_chunks.remove(chunk_coords)
                # print(f"Successfully generated chunk {chunk_coords}")
                
                self.generation_queue.task_done()
            except Exception as e:
                # print(f"Error generating chunk {chunk_coords}: {e}")
                # Make sure we remove from processing even if there's an error
                if chunk_coords in self.processing_chunks:
                    self.processing_chunks.remove(chunk_coords)
    
    def _generate_chunk_walls(self, base_x: int, base_y: int) -> List[pygame.Rect]:
        """Generate walls for a specific chunk"""
        walls = []
        
        def split_area(x: int, y: int, w: int, h: int, depth: int = 0):
            try:
                if depth > LEVEL['GENERATION']['MAX_DEPTH']:
                    return
                
                can_split_vertical = w >= self.min_room_size * 2 + self.wall_thickness
                can_split_horizontal = h >= self.min_room_size * 2 + self.wall_thickness
                
                if depth > 0 and random.random() < LEVEL['GENERATION']['SPLIT_CHANCE']:
                    return
                
                if not (can_split_vertical or can_split_horizontal):
                    return
                
                # Favor splitting along the longer dimension
                if can_split_vertical and can_split_horizontal:
                    split_vertical = w > h
                elif can_split_vertical:
                    split_vertical = True
                else:
                    split_vertical = False
                
                if split_vertical:
                    wall_x = x + w // 2
                    gap_height = LEVEL['WALL']['GAP_SIZE']
                    
                    # Add validation for random ranges
                    min_gap1 = y + gap_height
                    max_gap1 = y + (h // 2) - gap_height
                    min_gap2 = y + (h // 2)
                    max_gap2 = y + h - gap_height
                    
                    gap1_y = random.randint(min_gap1, max_gap1)
                    gap2_y = random.randint(min_gap2, max_gap2)
                    
                    # Create wall segments with validation
                    if gap1_y - y > 0:
                        walls.append(pygame.Rect(wall_x, y, self.wall_thickness, gap1_y - y))
                    if gap2_y - (gap1_y + gap_height) > 0:
                        walls.append(pygame.Rect(wall_x, gap1_y + gap_height, 
                                            self.wall_thickness, gap2_y - (gap1_y + gap_height)))
                    if (y + h) - (gap2_y + gap_height) > 0:
                        walls.append(pygame.Rect(wall_x, gap2_y + gap_height,
                                            self.wall_thickness, (y + h) - (gap2_y + gap_height)))
                    
                    # Recursive calls with validation
                    new_width = wall_x - x
                    if new_width > self.min_room_size:
                        split_area(x, y, new_width, h, depth + 1)
                    
                    new_x = wall_x + self.wall_thickness
                    new_width = w - (wall_x - x) - self.wall_thickness
                    if new_width > self.min_room_size:
                        split_area(new_x, y, new_width, h, depth + 1)
                    
                else:
                    wall_y = y + h // 2
                    gap_width = LEVEL['WALL']['GAP_SIZE']
                    
                    # Add validation for random ranges
                    min_gap1 = x + gap_width
                    max_gap1 = x + (w // 2) - gap_width
                    min_gap2 = x + (w // 2)
                    max_gap2 = x + w - gap_width
                    
                    gap1_x = random.randint(min_gap1, max_gap1)
                    gap2_x = random.randint(min_gap2, max_gap2)
                    
                    # Create wall segments with validation
                    if gap1_x - x > 0:
                        walls.append(pygame.Rect(x, wall_y, gap1_x - x, self.wall_thickness))
                    if gap2_x - (gap1_x + gap_width) > 0:
                        walls.append(pygame.Rect(gap1_x + gap_width, wall_y,
                                            gap2_x - (gap1_x + gap_width), self.wall_thickness))
                    if (x + w) - (gap2_x + gap_width) > 0:
                        walls.append(pygame.Rect(gap2_x + gap_width, wall_y,
                                            (x + w) - (gap2_x + gap_width), self.wall_thickness))
                    
                    # Recursive calls with validation
                    new_height = wall_y - y
                    if new_height > self.min_room_size:
                        split_area(x, y, w, new_height, depth + 1)
                    
                    new_y = wall_y + self.wall_thickness
                    new_height = h - (wall_y - y) - self.wall_thickness
                    if new_height > self.min_room_size:
                        split_area(x, new_y, w, new_height, depth + 1)
                    
            except Exception as e:
                print(f"Error in split_area: {e}")
                print(f"Parameters: x={x}, y={y}, w={w}, h={h}, depth={depth}")
        
        try:
            # Generate for this chunk
            split_area(base_x, base_y, self.chunk_size[0], self.chunk_size[1])
            return walls
        except Exception as e:
            print(f"Error in _generate_chunk_walls: {e}")
            return []
    
    def get_visible_walls(self, camera_x: float, camera_y: float) -> List[pygame.Rect]:
        """Get all walls that should be visible to the player"""
        visible_walls = []
        current_chunk = self.get_chunk_coords(camera_x, camera_y)
        
        # Check chunks in view range
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                chunk_coords = (current_chunk[0] + dx, current_chunk[1] + dy)
                if chunk_coords in self.chunks:
                    visible_walls.extend(self.chunks[chunk_coords])
        
        return visible_walls
    
    def generate_spawn_room(self) -> List[pygame.Rect]:
        walls = []
        room_size = LEVEL['ROOM']['SPAWN_SIZE']
        gap_size = LEVEL['WALL']['GAP_SIZE']
        wall_thickness = self.wall_thickness
        
        # Calculate room boundaries centered on screen center
        center_x = WINDOW['WIDTH'] // 2
        center_y = WINDOW['HEIGHT'] // 2
        
        left = center_x - room_size // 2
        right = center_x + room_size // 2
        top = center_y - room_size // 2
        bottom = center_y + room_size // 2
        
        # Create walls with gaps at cardinal directions
        # Top wall (with north gap)
        walls.extend([
            pygame.Rect(left, top, (room_size - gap_size) // 2, wall_thickness),  # Left segment
            pygame.Rect(right - (room_size - gap_size) // 2, top, (room_size - gap_size) // 2, wall_thickness)  # Right segment
        ])
        
        # Bottom wall (with south gap)
        walls.extend([
            pygame.Rect(left, bottom - wall_thickness, (room_size - gap_size) // 2, wall_thickness),  # Left segment
            pygame.Rect(right - (room_size - gap_size) // 2, bottom - wall_thickness, (room_size - gap_size) // 2, wall_thickness)  # Right segment
        ])
        
        # Left wall (with west gap)
        walls.extend([
            pygame.Rect(left, top, wall_thickness, (room_size - gap_size) // 2),  # Top segment
            pygame.Rect(left, bottom - (room_size - gap_size) // 2, wall_thickness, (room_size - gap_size) // 2)  # Bottom segment
        ])
        
        # Right wall (with east gap)
        walls.extend([
            pygame.Rect(right - wall_thickness, top, wall_thickness, (room_size - gap_size) // 2),  # Top segment
            pygame.Rect(right - wall_thickness, bottom - (room_size - gap_size) // 2, wall_thickness, (room_size - gap_size) // 2)  # Bottom segment
        ])
        
        return walls