import pygame
import random

from src.constants import CONTROLLER

class Controls:
    def __init__(self):
        self.controllers = []
        self.init_controllers()
        self.rumble_end_time = 0
        self.last_aim_direction = (1, 0)

    def init_controllers(self):
        try:
            print(f"Found {pygame.joystick.get_count()} controller(s)")
            for i in range(pygame.joystick.get_count()):
                controller = pygame.joystick.Joystick(i)
                controller.init()

                for j in range(controller.get_numbuttons()):
                    state = controller.get_button(j)
                
                self.controllers.append(controller)
        except Exception as e:
            print(f"Controller initialization error: {e}")
            
    def get_button(self, action):
        if not self.controllers:
            return False
            
        try:
            controller = self.controllers[0]
            button_name = CONTROLLER['ACTIONS'].get(action)
            if not button_name:
                return False
                
            button_id = CONTROLLER['BUTTONS'].get(button_name)
            if button_id is None:
                return False
                
            if CONTROLLER['DEBUG'] and controller.get_button(button_id):
                # print(f"Button pressed: {button_name} (ID: {button_id})")
                pass
                
            return controller.get_button(button_id)
        except Exception as e:
            print(f"Button error: {e}")
            return False
            
    def is_shooting(self):
        # Check mouse first
        if pygame.mouse.get_pressed()[0]:  # Left click
            return True
        
        # Check keyboard (optional, if you want a keyboard shoot button)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:  # or whatever key you prefer
            return True
        
        # Check controller
        return self.get_button('SHOOT')
        
    def is_sprinting(self):
        # Check keyboard
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LSHIFT]:
            return True
        
        # Check controller
        return self.get_button('SPRINT')
        
    def get_movement_vector(self):
        # Check keyboard first
        keys = pygame.key.get_pressed()
        x = 0
        y = 0
        
        if keys[pygame.K_a]:
            x -= 1
        if keys[pygame.K_d]:
            x += 1
        if keys[pygame.K_w]:
            y -= 1
        if keys[pygame.K_s]:
            y += 1
        
        # Normalize diagonal movement
        if x != 0 and y != 0:
            x *= 0.707  # 1/√2
            y *= 0.707
        
        # If keyboard keys are pressed, return that vector
        if x != 0 or y != 0:
            return (x, y)
        
        # Otherwise check controller
        if not self.controllers:
            return (0, 0)
        
        try:
            controller = self.controllers[0]
            x = controller.get_axis(0)  # Left stick X
            y = controller.get_axis(1)  # Left stick Y
            
            # Apply deadzone
            if abs(x) < CONTROLLER['INPUT']['STICK_DEADZONE']:
                x = 0
            if abs(y) < CONTROLLER['INPUT']['STICK_DEADZONE']:
                y = 0
                
            return (x, y)
        except Exception as e:
            print(f"Movement error: {e}")
            return (0, 0)

    def get_aim_vector(self):
        # Check for mouse first
        mouse_pos = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0]:  # Left click
            self.last_aim_direction = (mouse_pos[0], mouse_pos[1])
            return (mouse_pos[0], mouse_pos[1], False)  # False = not using controller
        
        # Check controller
        if not self.controllers:
            return (self.last_aim_direction[0], self.last_aim_direction[1], False)
        
        try:
            controller = self.controllers[0]
            x = controller.get_axis(2)  # Right stick X
            y = controller.get_axis(3)  # Right stick Y
            
            # Apply deadzone
            if abs(x) < CONTROLLER['INPUT']['STICK_DEADZONE']:
                x = 0
            if abs(y) < CONTROLLER['INPUT']['STICK_DEADZONE']:
                y = 0
            
            # If we have any input, update the last direction
            if x != 0 or y != 0:
                # Normalize the vector
                length = (x*x + y*y) ** 0.5
                if length > 0:
                    x /= length
                    y /= length
                self.last_aim_direction = (x, y)
            
            # Return last known direction if no current input
            if x == 0 and y == 0:
                return (self.last_aim_direction[0], self.last_aim_direction[1], True)
                
            return (x, y, True)  # True = using controller
        except Exception as e:
            print(f"Aim error: {e}")
            return (self.last_aim_direction[0], self.last_aim_direction[1], False)

    def start_rumble(self):
        try:
            if self.controllers:
                controller = self.controllers[0]
                if hasattr(controller, 'rumble'):
                    rumble_low = random.uniform(
                        CONTROLLER['RUMBLE']['LOW_FREQ_MIN'],
                        CONTROLLER['RUMBLE']['LOW_FREQ_MAX']
                    )
                    controller.rumble(
                        rumble_low,
                        CONTROLLER['RUMBLE']['HIGH_FREQ'],
                        CONTROLLER['RUMBLE']['DURATION']
                    )
                    self.rumble_end_time = pygame.time.get_ticks() + CONTROLLER['RUMBLE']['DURATION']
        except Exception as e:
            print(f"Rumble error: {e}")
            self.rumble_end_time = 0

    def update_rumble(self):
        if self.rumble_end_time and pygame.time.get_ticks() > self.rumble_end_time:
            if self.controllers:
                try:
                    self.controllers[0].stop_rumble()
                except pygame.error:
                    pass
            self.rumble_end_time = 0