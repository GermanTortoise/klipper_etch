import pygame
import sys
from typing import NamedTuple
import vector

"""
[keyboard_control]
framerate: 60
x_min: 10
x_max: 200
y_min: 10
y_max: 200
z_min(?): 0
z_max: 180
speed: 100
acceleration: 3000

can you read other config sections?
yes with config.getsection

mode where lines can't overlap already printed lines and instead are snapped to the edge of them
can only cross when not extruding
on new layer, can only extrude when on top of prev by at least a certain overhang %
"""

# copied from a gcode file
startup_command = """
; EXECUTABLE_BLOCK_START
M73 P0 R6
;TYPE:Custom
G90 ; use absolute coordinates
M83 ; extruder relative mode
M204 S5000 T5000
M104 S230 ; set extruder temp
M140 S50 ; set bed temp
G28 ; home all
M190 S50 ; wait for bed temp
G1 Z1.24
G1 X100 Y100 ; TODO: don't hardcode this
G1 Z.24
; TODO: finish
"""

class KeyboardControl:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')
        self.framerate = config.getint('framerate')
        self.x_min = config.getfloat('x_min')
        self.x_max = config.getfloat('x_max')
        self.y_min = config.getfloat('y_min')
        self.y_max = config.getfloat('y_max')
        self.z_min = config.getfloat('z_min')
        self.z_max = config.getfloat('z_max')
        self.speed = config.getfloat('speed')
        self.accel = config.getfloat('acceleration')
        self.x = (self.x_max - self.x_min) / 2
        self.y = (self.y_max - self.y_min) / 2
        self.z = 0.24 # TODO: don't hard code this
        self.gcode.register_command('ETCH_START', self.run, desc='start etching')
        self.gcode.register_command('ETCH_STOP', self.stop, desc='stop etching, can also stop by closing the window')
        
    def _increment_bounded(self, val: float, move: float, min: float, max: float) -> float:
        if val + move < min:
            return min
        if val + move > max:
            return max
        return val + move
    
    def _move_gcode(self) -> str:
        return f"G1 X{self.x:.3f} Y{self.y:.3f} E1.13607"
    
    def _move(self, keys: str) -> bool:
        v = vector.obj(x=0, y=0)
        for char in keys:
            match char:
                case 'w':
                    v.y += 1
                case 'a':
                    v.x -= 1
                case 's':
                    v.y -= 1
                case 'd':
                    v.x += 1
        if v.rho == 0:
            return False
        v = v.unit()
        v *= (self.speed / self.framerate)
        self.x = self._increment_bounded(self.x, v.x, self.x_min, self.x_max)
        self.y = self._increment_bounded(self.y, v.y, self.y_min, self.y_max)        
        return True
        
    def run(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.running = True
        # Create a small hidden window (required for pygame to work)
        self.screen = pygame.display.set_mode((100, 100))
        pygame.display.set_caption("Keyboard Control")
        while self.running:
            self.clock.tick(self.framerate)
            
            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            # Get pressed keys
            keys = pygame.key.get_pressed()
            keys_pressed = ""
            if keys[pygame.K_w]:
                keys_pressed += 'w'
            if keys[pygame.K_a]:
                keys_pressed += 'a'
            if keys[pygame.K_s]:
                keys_pressed += 's'
            if keys[pygame.K_d]:
                keys_pressed += 'd'
                
            if self._move(keys_pressed):
                print(self._move_gcode())
        
        pygame.quit()
        
    def stop(self):
        if self.running:
            pygame.quit()
            self.running = False
            
def load_config_prefix(config):
    return KeyboardControl(config)


class MockConfig:
    def __init__(self) -> None:
        self.values = {
            'framerate': 60,
            'x_min': 10,
            'x_max': 200,
            'y_min': 10,
            'y_max': 200,
            'z_min': 0,
            'z_max': 180,
            'speed': 100,
            'acceleration': 3000,
        }
    
    def getint(self, key: str) -> int:
        return int(self.values[key])
    
    def getfloat(self, key: str) -> float:
        return float(self.values[key])
    
    def get_printer(self):
        return MockPrinter()


class MockPrinter:
    def lookup_object(self, name: str):
        return MockGcode()


class MockGcode:
    def register_command(self, command: str, callback, desc: str = ''):
        pass
    
    
e = load_config_prefix(MockConfig()) 
e.run()



# class Position(NamedTuple):
#     x: float
#     y: float
#     z: float

# class PositionModel:
#     def __init__(self, x_min: float, x_max: float, y_min: float, y_max: float, z_min: float, z_max: float, speed: float, accel: float, x_i: float, y_i: float, z_i: float) -> None:
#         self.x_min = x_min
#         self.x_max = x_max
#         self.y_min = y_min
#         self.y_max = y_max
#         self.z_min = z_min
#         self.z_max = z_max
#         self.speed = speed
#         self.accel = accel
        
#         self.x = x_i
#         self.y = y_i
#         self.z = z_i
        
#     def move(self, keys):
#         pass
    
#     def get_pos(self) -> :
#         pass
