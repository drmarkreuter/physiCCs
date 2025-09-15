import pygame
import pygame.midi
import math
from midi_physics_base import MIDIPhysicsBase

class GravityModule(MIDIPhysicsBase):
    """
    Gravity Module: Three MIDI CC controllers that fall back to zero under gravity.
    Gravity strength determines how quickly they return to zero.
    """
    
    def __init__(self):
        super().__init__("Gravity")
        
        # CC Controllers
        self.controllers = [
            {"cc": 74, "value": 64, "velocity": 0, "name": "Controller 1"},
            {"cc": 75, "value": 64, "velocity": 0, "name": "Controller 2"},
            {"cc": 76, "value": 64, "velocity": 0, "name": "Controller 3"}
        ]
        
        # Gravity settings
        self.gravity_strength = 0.5  # 0 = no gravity, 1 = maximum gravity
        self.gravity_labels = {
            0.0: "Zero G",
            0.2: "Moon",
            0.5: "Earth", 
            0.8: "Jupiter",
            1.0: "Black Hole"
        }
        
        # UI state
        self.dragging_controller = None
        self.dragging_gravity = False
        self.mouse_offset = 0
        
        # Visual parameters
        self.controller_width = 80
        self.controller_height = 300
        self.controller_spacing = 150
        self.controller_start_x = 100
        self.controller_y = 200
        
        self.gravity_slider_x = 600
        self.gravity_slider_y = 150
        self.gravity_slider_height = 200
        self.gravity_slider_width = 30
    
    def setup_cc_assignments(self):
        """Allow user to configure CC numbers for each controller."""
        print("\nCC Controller Assignment")
        print("========================")
        
        for i, controller in enumerate(self.controllers):
            while True:
                try:
                    current_cc = controller["cc"]
                    cc_input = input(f"Controller {i+1} CC number [default: {current_cc}]: ").strip()
                    
                    if not cc_input:  # Use default
                        break
                    
                    cc_num = int(cc_input)
                    if 0 <= cc_num <= 127:
                        controller["cc"] = cc_num
                        print(f"Controller {i+1} assigned to CC {cc_num}")
                        break
                    else:
                        print("CC number must be between 0 and 127!")
                except ValueError:
                    print("Please enter a valid number!")
    
    def get_gravity_force(self):
        """Calculate gravity force based on current setting."""
        if self.gravity_strength == 0:
            return 0
        # Exponential scaling for more dramatic effect at higher settings
        return self.gravity_strength * self.gravity_strength * 0.8
    
    def get_closest_gravity_label(self):
        """Get the closest gravity label for current setting."""
        closest_key = min(self.gravity_labels.keys(), 
                         key=lambda x: abs(x - self.gravity_strength))
        return self.gravity_labels[closest_key]
    
    def update(self):
        """Update physics simulation."""
        gravity_force = self.get_gravity_force()
        
        for controller in self.controllers:
            # Apply gravity - pull towards center (64)
            center = 64
            distance_from_center = controller["value"] - center
            
            if abs(distance_from_center) > 0.1:  # Small deadzone to prevent jitter
                # Gravity pulls towards center
                gravity_acceleration = -distance_from_center * gravity_force * 0.1
                controller["velocity"] += gravity_acceleration
                
                # Apply some damping to prevent oscillation
                controller["velocity"] *= 0.98
                
                # Update position
                controller["value"] += controller["velocity"]
                
                # Clamp to valid MIDI range
                controller["value"] = max(0, min(127, controller["value"]))
                
                # Send MIDI
                self.send_cc(controller["cc"], controller["value"])
            else:
                # Close enough to center, snap and stop
                if gravity_force > 0:
                    controller["value"] = center
                    controller["velocity"] = 0
    
    def handle_mouse_events(self, event):
        """Handle mouse interactions with sliders."""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check controller sliders
                for i, controller in enumerate(self.controllers):
                    slider_x = self.controller_start_x + i * self.controller_spacing
                    slider_rect = pygame.Rect(
                        slider_x, self.controller_y,
                        self.controller_width, self.controller_height
                    )
                    
                    if slider_rect.collidepoint(mouse_x, mouse_y):
                        self.dragging_controller = i
                        # Calculate mouse offset from slider handle
                        handle_y = self.controller_y + self.controller_height - \
                                  (controller["value"] / 127) * self.controller_height
                        self.mouse_offset = mouse_y - handle_y
                        break
                
                # Check gravity slider
                gravity_rect = pygame.Rect(
                    self.gravity_slider_x, self.gravity_slider_y,
                    self.gravity_slider_width, self.gravity_slider_height
                )
                
                if gravity_rect.collidepoint(mouse_x, mouse_y):
                    self.dragging_gravity = True
                    handle_y = self.gravity_slider_y + self.gravity_slider_height - \
                              self.gravity_strength * self.gravity_slider_height
                    self.mouse_offset = mouse_y - handle_y
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                self.dragging_controller = None
                self.dragging_gravity = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_controller is not None:
                # Update controller value based on mouse position
                controller = self.controllers[self.dragging_controller]
                relative_y = mouse_y - self.mouse_offset - self.controller_y
                # Invert Y (top = high value)
                normalized = 1.0 - (relative_y / self.controller_height)
                normalized = max(0, min(1, normalized))
                controller["value"] = normalized * 127
                controller["velocity"] = 0  # Stop any gravity motion while dragging
                
                # Send MIDI immediately
                self.send_cc(controller["cc"], controller["value"])
            
            elif self.dragging_gravity:
                # Update gravity value
                relative_y = mouse_y - self.mouse_offset - self.gravity_slider_y
                normalized = 1.0 - (relative_y / self.gravity_slider_height)
                self.gravity_strength = max(0, min(1, normalized))
    
    def draw_controller_slider(self, x, y, value, name):
        """Draw a single controller slider."""
        # Slider background
        slider_rect = pygame.Rect(x, y, self.controller_width, self.controller_height)
        pygame.draw.rect(self.screen, self.GRAY, slider_rect)
        pygame.draw.rect(self.screen, self.WHITE, slider_rect, 2)
        
        # Slider handle
        handle_height = 20
        handle_y = y + self.controller_height - (value / 127) * self.controller_height - handle_height // 2
        handle_rect = pygame.Rect(x, handle_y, self.controller_width, handle_height)
        pygame.draw.rect(self.screen, self.BLUE, handle_rect)
        
        # Value text
        value_text = f"{int(value)}"
        self.draw_text(value_text, x + 5, handle_y - 25, self.WHITE, self.small_font)
        
        # Name label
        self.draw_text(name, x, y + self.controller_height + 10, self.WHITE, self.small_font)
        
        # CC number
        cc_text = f"CC{self.controllers[0]['cc'] if name == 'Controller 1' else self.controllers[1]['cc'] if name == 'Controller 2' else self.controllers[2]['cc']}"
        self.draw_text(cc_text, x, y + self.controller_height + 30, self.GRAY, self.small_font)
    
    def draw_gravity_slider(self):
        """Draw the gravity control slider."""
        # Slider background
        slider_rect = pygame.Rect(
            self.gravity_slider_x, self.gravity_slider_y,
            self.gravity_slider_width, self.gravity_slider_height
        )
        pygame.draw.rect(self.screen, self.GRAY, slider_rect)
        pygame.draw.rect(self.screen, self.WHITE, slider_rect, 2)
        
        # Color gradient for gravity (red = high gravity)
        for i in range(self.gravity_slider_height):
            intensity = i / self.gravity_slider_height
            color = (int(255 * intensity), int(100 * (1 - intensity)), 0)
            pygame.draw.line(self.screen, color,
                           (self.gravity_slider_x + 2, self.gravity_slider_y + i),
                           (self.gravity_slider_x + self.gravity_slider_width - 2, self.gravity_slider_y + i))
        
        # Slider handle
        handle_height = 15
        handle_y = self.gravity_slider_y + self.gravity_slider_height - \
                   self.gravity_strength * self.gravity_slider_height - handle_height // 2
        handle_rect = pygame.Rect(
            self.gravity_slider_x - 5, handle_y,
            self.gravity_slider_width + 10, handle_height
        )
        pygame.draw.rect(self.screen, self.WHITE, handle_rect)
        pygame.draw.rect(self.screen, self.BLACK, handle_rect, 2)
        
        # Gravity label
        self.draw_text("GRAVITY", self.gravity_slider_x - 20, self.gravity_slider_y - 30)
        
        # Current gravity setting
        gravity_label = self.get_closest_gravity_label()
        gravity_percent = f"{int(self.gravity_strength * 100)}%"
        self.draw_text(gravity_label, self.gravity_slider_x - 30, self.gravity_slider_y + self.gravity_slider_height + 20)
        self.draw_text(gravity_percent, self.gravity_slider_x - 10, self.gravity_slider_y + self.gravity_slider_height + 40, self.GRAY, self.small_font)
    
    def draw(self):
        """Draw the gravity module interface."""
        # Title
        self.draw_text("GRAVITY MODULE", 50, 50)
        
        # Instructions
        self.draw_text("Drag sliders up, watch them fall back down!", 50, 80, self.GRAY, self.small_font)
        self.draw_text("Adjust gravity to change fall speed", 50, 100, self.GRAY, self.small_font)
        
        # Draw controllers
        for i, controller in enumerate(self.controllers):
            x = self.controller_start_x + i * self.controller_spacing
            self.draw_controller_slider(x, self.controller_y, controller["value"], controller["name"])
        
        # Draw gravity slider
        self.draw_gravity_slider()
        
        # Current gravity force indicator
        force = self.get_gravity_force()
        if force > 0:
            self.draw_text(f"Force: {force:.2f}", self.gravity_slider_x - 20, self.gravity_slider_y + self.gravity_slider_height + 60, self.WHITE, self.small_font)
    
    def run(self):
        """Main run loop with mouse event handling."""
        self.running = True
        
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if not self.handle_base_events(event):
                    self.running = False
                    break
                
                # Handle mouse events
                self.handle_mouse_events(event)
            
            if not self.running:
                break
            
            # Clear screen
            self.screen.fill(self.BLACK)
            
            # Update physics
            self.update()
            
            # Draw everything
            self.draw()
            self.draw_connection_status()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)

def main():
    """Main function to run the Gravity module."""
    gravity = GravityModule()
    
    print("MIDI Physics - Gravity Module")
    print("=============================")
    print("Three CC controllers that fall back to zero under gravity!")
    print("- Drag the blue sliders up and watch them fall back to zero")
    print("- Adjust the gravity slider (right side) to control fall speed")
    print("- Zero G = no gravity, Black Hole = maximum gravity")
    
    # Setup MIDI
    if not gravity.setup_midi_device():
        print("MIDI setup cancelled.")
        gravity.cleanup()
        return
    
    # Setup CC assignments
    gravity.setup_cc_assignments()
    
    if not gravity.connect_midi():
        print("Failed to connect to MIDI device.")
        gravity.cleanup()
        return
    
    print("\nControls:")
    print("- Mouse: Drag sliders")
    print("- ESC: Exit")
    cc_list = ", ".join([f"CC{c['cc']}" for c in gravity.controllers])
    print(f"- Sending: {cc_list}")
    
    # Run the module
    gravity.run()
    gravity.cleanup()

if __name__ == "__main__":
    main()