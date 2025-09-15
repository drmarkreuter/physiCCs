import pygame
import pygame.midi
import math
from midi_physics_base import MIDIPhysicsBase

class PendulumModule(MIDIPhysicsBase):
    """
    Pendulum Module: A swinging pendulum that generates MIDI data.
    Can output either pitch bend or MIDI CC data based on pendulum position.
    """
    
    def __init__(self):
        super().__init__("Pendulum")
        
        # Pendulum physics
        self.length = 200  # Pendulum length in pixels
        self.max_length = 300
        self.min_length = 100
        self.angle = math.pi / 4  # Starting angle (45 degrees)
        self.angular_velocity = 0
        self.gravity = 0.5  # Gravity strength
        self.damping = 0.999  # Energy loss factor
        
        # Pendulum position (pivot point)
        self.pivot_x = 400
        self.pivot_y = 150
        
        # Output mode
        self.output_modes = ["MIDI CC", "Pitch Bend"]
        self.current_mode = 0  # 0 = MIDI CC, 1 = Pitch Bend
        
        # MIDI CC settings (for CC mode)
        self.cc_number = 74  # Default CC
        self.cc_center = 64  # Center value for CC output
        
        # Visual settings
        self.bob_radius = 20
        self.trail_points = []
        self.max_trail_length = 50
        
        # UI controls
        self.length_slider_x = 550
        self.length_slider_y = 150
        self.length_slider_height = 200
        self.length_slider_width = 30
        
        self.mode_button_x = 550
        self.mode_button_y = 400
        self.mode_button_width = 120
        self.mode_button_height = 40
        
        # Mouse interaction
        self.dragging_length = False
        self.dragging_pendulum = False
        self.mouse_offset = 0
    
    def setup_pendulum_config(self):
        """Configure pendulum settings."""
        print("\nPendulum Configuration")
        print("======================")
        
        # Output mode selection
        print("\nOutput Modes:")
        for i, mode in enumerate(self.output_modes):
            print(f"{i + 1}. {mode}")
        
        while True:
            try:
                mode_input = input(f"Select mode (1-{len(self.output_modes)}) [default: 1]: ").strip()
                if not mode_input:
                    self.current_mode = 0
                    break
                
                mode_num = int(mode_input) - 1
                if 0 <= mode_num < len(self.output_modes):
                    self.current_mode = mode_num
                    print(f"Selected: {self.output_modes[self.current_mode]}")
                    break
                else:
                    print(f"Please enter 1-{len(self.output_modes)}!")
            except ValueError:
                print("Please enter a valid number!")
        
        # CC number setup (only for CC mode)
        if self.current_mode == 0:  # MIDI CC mode
            while True:
                try:
                    current_cc = self.cc_number
                    cc_input = input(f"MIDI CC number [default: {current_cc}]: ").strip()
                    if not cc_input:
                        break
                    
                    cc_num = int(cc_input)
                    if 0 <= cc_num <= 127:
                        self.cc_number = cc_num
                        print(f"CC {cc_num} selected")
                        break
                    else:
                        print("CC number must be between 0 and 127!")
                except ValueError:
                    print("Please enter a valid number!")
    
    def calculate_pendulum_position(self):
        """Calculate the current position of the pendulum bob."""
        x = self.pivot_x + self.length * math.sin(self.angle)
        y = self.pivot_y + self.length * math.cos(self.angle)
        return x, y
    
    def update_physics(self):
        """Update pendulum physics simulation."""
        # Simple pendulum equation: angular acceleration = -(g/L) * sin(θ)
        angular_acceleration = -(self.gravity / self.length) * math.sin(self.angle) * 0.1
        
        # Update angular velocity and position
        self.angular_velocity += angular_acceleration
        self.angular_velocity *= self.damping  # Apply damping
        self.angle += self.angular_velocity
        
        # Add trail point
        bob_x, bob_y = self.calculate_pendulum_position()
        self.trail_points.append((bob_x, bob_y))
        
        # Limit trail length
        if len(self.trail_points) > self.max_trail_length:
            self.trail_points.pop(0)
    
    def generate_midi_output(self):
        """Generate MIDI output based on pendulum position and mode."""
        bob_x, bob_y = self.calculate_pendulum_position()
        
        if self.current_mode == 0:  # MIDI CC mode
            # Convert X position to CC value centered around 64
            # Map from pendulum swing range to 0-127
            swing_range = self.length * 2  # Total swing width
            relative_x = bob_x - (self.pivot_x - self.length)
            normalized = relative_x / swing_range
            cc_value = int(normalized * 127)
            cc_value = max(0, min(127, cc_value))
            
            self.send_cc(self.cc_number, cc_value)
            
        elif self.current_mode == 1:  # Pitch Bend mode
            # Convert X position to pitch bend (-8192 to 8191)
            swing_range = self.length * 2
            relative_x = bob_x - self.pivot_x  # Center around pivot
            normalized = relative_x / self.length  # -1 to 1 range
            pitch_value = int(normalized * 8192)
            pitch_value = max(-8192, min(8191, pitch_value))
            
            self.send_pitch_bend(pitch_value)
    
    def update(self):
        """Update the pendulum simulation."""
        if not self.dragging_pendulum:
            self.update_physics()
        self.generate_midi_output()
    
    def handle_mouse_events(self, event):
        """Handle mouse interactions."""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check length slider
                length_rect = pygame.Rect(
                    self.length_slider_x, self.length_slider_y,
                    self.length_slider_width, self.length_slider_height
                )
                
                if length_rect.collidepoint(mouse_x, mouse_y):
                    self.dragging_length = True
                    # Calculate handle position
                    length_norm = (self.length - self.min_length) / (self.max_length - self.min_length)
                    handle_y = self.length_slider_y + self.length_slider_height - \
                              length_norm * self.length_slider_height
                    self.mouse_offset = mouse_y - handle_y
                
                # Check mode button
                mode_rect = pygame.Rect(
                    self.mode_button_x, self.mode_button_y,
                    self.mode_button_width, self.mode_button_height
                )
                
                if mode_rect.collidepoint(mouse_x, mouse_y):
                    # Toggle mode
                    self.current_mode = (self.current_mode + 1) % len(self.output_modes)
                
                # Check pendulum bob
                bob_x, bob_y = self.calculate_pendulum_position()
                bob_distance = math.sqrt((mouse_x - bob_x)**2 + (mouse_y - bob_y)**2)
                
                if bob_distance < self.bob_radius * 2:  # Slightly larger hit area
                    self.dragging_pendulum = True
                    self.angular_velocity = 0  # Stop motion when grabbed
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.dragging_pendulum:
                    # Calculate initial velocity based on mouse movement
                    # This gives the pendulum a natural "push" when released
                    self.dragging_pendulum = False
                
                self.dragging_length = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_length:
                # Update pendulum length
                relative_y = mouse_y - self.mouse_offset - self.length_slider_y
                normalized = 1.0 - (relative_y / self.length_slider_height)
                normalized = max(0, min(1, normalized))
                self.length = self.min_length + normalized * (self.max_length - self.min_length)
            
            elif self.dragging_pendulum:
                # Update pendulum angle based on mouse position
                dx = mouse_x - self.pivot_x
                dy = mouse_y - self.pivot_y
                
                if dy > 0:  # Only allow pendulum below pivot
                    self.angle = math.atan2(dx, dy)
                    # Clamp angle to reasonable range
                    max_angle = math.pi * 0.8  # About 144 degrees total swing
                    self.angle = max(-max_angle, min(max_angle, self.angle))
    
    def draw_pendulum(self):
        """Draw the pendulum."""
        bob_x, bob_y = self.calculate_pendulum_position()
        
        # Draw trail
        if len(self.trail_points) > 1:
            for i in range(len(self.trail_points) - 1):
                alpha = i / len(self.trail_points)
                color_intensity = int(100 * alpha)
                color = (color_intensity, color_intensity, color_intensity)
                if i < len(self.trail_points) - 1:
                    pygame.draw.line(self.screen, color, 
                                   self.trail_points[i], self.trail_points[i + 1], 2)
        
        # Draw pendulum rod
        pygame.draw.line(self.screen, self.WHITE, 
                        (self.pivot_x, self.pivot_y), (bob_x, bob_y), 3)
        
        # Draw pivot point
        pygame.draw.circle(self.screen, self.WHITE, 
                         (self.pivot_x, self.pivot_y), 8)
        pygame.draw.circle(self.screen, self.BLACK, 
                         (self.pivot_x, self.pivot_y), 8, 2)
        
        # Draw pendulum bob
        bob_color = self.BLUE if not self.dragging_pendulum else self.RED
        pygame.draw.circle(self.screen, bob_color, 
                         (int(bob_x), int(bob_y)), self.bob_radius)
        
        # Draw highlight on bob
        highlight_x = int(bob_x - 5)
        highlight_y = int(bob_y - 5)
        pygame.draw.circle(self.screen, self.WHITE, 
                         (highlight_x, highlight_y), 6)
    
    def draw_length_slider(self):
        """Draw the pendulum length control slider."""
        # Slider background
        slider_rect = pygame.Rect(
            self.length_slider_x, self.length_slider_y,
            self.length_slider_width, self.length_slider_height
        )
        pygame.draw.rect(self.screen, self.GRAY, slider_rect)
        pygame.draw.rect(self.screen, self.WHITE, slider_rect, 2)
        
        # Slider handle
        length_normalized = (self.length - self.min_length) / (self.max_length - self.min_length)
        handle_y = self.length_slider_y + self.length_slider_height - \
                   length_normalized * self.length_slider_height
        handle_rect = pygame.Rect(
            self.length_slider_x - 5, handle_y - 7,
            self.length_slider_width + 10, 15
        )
        pygame.draw.rect(self.screen, self.WHITE, handle_rect)
        pygame.draw.rect(self.screen, self.BLACK, handle_rect, 2)
        
        # Label
        self.draw_text("LENGTH", self.length_slider_x - 10, self.length_slider_y - 30)
        length_text = f"{int(self.length)}px"
        self.draw_text(length_text, self.length_slider_x - 15, 
                      self.length_slider_y + self.length_slider_height + 10,
                      self.WHITE, self.small_font)
    
    def draw_mode_button(self):
        """Draw the output mode toggle button."""
        button_rect = pygame.Rect(
            self.mode_button_x, self.mode_button_y,
            self.mode_button_width, self.mode_button_height
        )
        
        # Button background
        button_color = self.BLUE if self.current_mode == 0 else self.GREEN
        pygame.draw.rect(self.screen, button_color, button_rect)
        pygame.draw.rect(self.screen, self.WHITE, button_rect, 2)
        
        # Button text
        mode_text = self.output_modes[self.current_mode]
        text_surface = self.small_font.render(mode_text, True, self.WHITE)
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)
    
    def draw_output_info(self):
        """Draw current output information."""
        info_x = 50
        info_y = 500
        
        # Current mode
        mode_text = f"Mode: {self.output_modes[self.current_mode]}"
        self.draw_text(mode_text, info_x, info_y, self.WHITE, self.small_font)
        
        # Current output value
        bob_x, bob_y = self.calculate_pendulum_position()
        
        if self.current_mode == 0:  # MIDI CC
            swing_range = self.length * 2
            relative_x = bob_x - (self.pivot_x - self.length)
            normalized = relative_x / swing_range
            cc_value = int(normalized * 127)
            cc_value = max(0, min(127, cc_value))
            
            output_text = f"CC{self.cc_number}: {cc_value}"
            self.draw_text(output_text, info_x, info_y + 20, self.WHITE, self.small_font)
            
        elif self.current_mode == 1:  # Pitch Bend
            relative_x = bob_x - self.pivot_x
            normalized = relative_x / self.length
            pitch_value = int(normalized * 8192)
            pitch_value = max(-8192, min(8191, pitch_value))
            
            output_text = f"Pitch Bend: {pitch_value:+d}"
            self.draw_text(output_text, info_x, info_y + 20, self.WHITE, self.small_font)
        
        # Pendulum stats
        angle_degrees = math.degrees(self.angle)
        self.draw_text(f"Angle: {angle_degrees:.1f}°", info_x, info_y + 40, self.GRAY, self.small_font)
        self.draw_text(f"Length: {int(self.length)}px", info_x, info_y + 60, self.GRAY, self.small_font)
    
    def draw(self):
        """Draw the pendulum module interface."""
        # Title
        self.draw_text("PENDULUM MODULE", 50, 50)
        
        # Instructions
        self.draw_text("Drag the pendulum bob to set it swinging!", 50, 80, self.GRAY, self.small_font)
        self.draw_text("Adjust length for different swing speeds", 50, 100, self.GRAY, self.small_font)
        self.draw_text("Toggle between MIDI CC and Pitch Bend modes", 50, 120, self.GRAY, self.small_font)
        
        # Draw pendulum elements
        self.draw_pendulum()
        self.draw_length_slider()
        self.draw_mode_button()
        self.draw_output_info()
    
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
    """Main function to run the Pendulum module."""
    pendulum = PendulumModule()
    
    print("MIDI Physics - Pendulum Module")
    print("==============================")
    print("A swinging pendulum generating MIDI data!")
    print("- Drag the blue bob to start it swinging")
    print("- Longer pendulum = slower swing")
    print("- Choose between MIDI CC or Pitch Bend output")
    
    # Setup MIDI
    if not pendulum.setup_midi_device():
        print("MIDI setup cancelled.")
        pendulum.cleanup()
        return
    
    # Setup pendulum configuration
    pendulum.setup_pendulum_config()
    
    if not pendulum.connect_midi():
        print("Failed to connect to MIDI device.")
        pendulum.cleanup()
        return
    
    print("\nControls:")
    print("- Mouse: Drag pendulum bob to swing it")
    print("- Mouse: Drag length slider to change pendulum length")
    print("- Mouse: Click mode button to toggle CC/Pitch Bend")
    print("- ESC: Exit")
    
    if pendulum.current_mode == 0:
        print(f"- Output: MIDI CC {pendulum.cc_number}")
    else:
        print("- Output: Pitch Bend")
    
    # Run the module
    pendulum.run()
    pendulum.cleanup()

if __name__ == "__main__":
    main()