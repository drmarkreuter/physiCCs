import pygame
import pygame.midi
import math
import random
from midi_physics_base import MIDIPhysicsBase

class ParticleModule(MIDIPhysicsBase):
    """
    Particle Module: Two particles bouncing around generating MIDI CC data
    from their X and Y positions.
    """
    
    def __init__(self):
        super().__init__("Particle")
        
        # Simulation area
        self.sim_x = 50
        self.sim_y = 130
        self.sim_width = 400
        self.sim_height = 400
        
        # Particles
        self.red_particle = {
            "x": random.randint(50, self.sim_width - 50),
            "y": random.randint(50, self.sim_height - 50),
            "vx": random.uniform(-3, 3),
            "vy": random.uniform(-3, 3),
            "radius": 15,
            "color": (255, 100, 100),
            "cc_x": 74,  # Default CC for red X
            "cc_y": 75   # Default CC for red Y
        }
        
        self.green_particle = {
            "x": random.randint(50, self.sim_width - 50),
            "y": random.randint(50, self.sim_height - 50),
            "vx": random.uniform(-3, 3),
            "vy": random.uniform(-3, 3),
            "radius": 15,
            "color": (100, 255, 100),
            "cc_x": 76,  # Default CC for green X
            "cc_y": 77   # Default CC for green Y
        }
        
        # Temperature control (affects particle speed)
        self.temperature = 0.5  # 0 = cold/slow, 1 = hot/fast
        self.base_speed = 2.0
        self.max_speed_multiplier = 3.0
        
        # UI elements
        self.temp_slider_x = 500
        self.temp_slider_y = 150
        self.temp_slider_height = 200
        self.temp_slider_width = 30
        self.dragging_temperature = False
        self.mouse_offset = 0
    
    def setup_cc_assignments(self):
        """Allow user to configure CC numbers for particle axes."""
        print("\nParticle CC Assignment")
        print("======================")
        
        # Red particle CCs
        print("\nRed Particle:")
        while True:
            try:
                current_cc = self.red_particle["cc_x"]
                cc_input = input(f"Red X-axis CC [default: {current_cc}]: ").strip()
                if not cc_input:
                    break
                cc_num = int(cc_input)
                if 0 <= cc_num <= 127:
                    self.red_particle["cc_x"] = cc_num
                    print(f"Red X assigned to CC {cc_num}")
                    break
                else:
                    print("CC number must be between 0 and 127!")
            except ValueError:
                print("Please enter a valid number!")
        
        while True:
            try:
                current_cc = self.red_particle["cc_y"]
                cc_input = input(f"Red Y-axis CC [default: {current_cc}]: ").strip()
                if not cc_input:
                    break
                cc_num = int(cc_input)
                if 0 <= cc_num <= 127:
                    self.red_particle["cc_y"] = cc_num
                    print(f"Red Y assigned to CC {cc_num}")
                    break
                else:
                    print("CC number must be between 0 and 127!")
            except ValueError:
                print("Please enter a valid number!")
        
        # Green particle CCs
        print("\nGreen Particle:")
        while True:
            try:
                current_cc = self.green_particle["cc_x"]
                cc_input = input(f"Green X-axis CC [default: {current_cc}]: ").strip()
                if not cc_input:
                    break
                cc_num = int(cc_input)
                if 0 <= cc_num <= 127:
                    self.green_particle["cc_x"] = cc_num
                    print(f"Green X assigned to CC {cc_num}")
                    break
                else:
                    print("CC number must be between 0 and 127!")
            except ValueError:
                print("Please enter a valid number!")
        
        while True:
            try:
                current_cc = self.green_particle["cc_y"]
                cc_input = input(f"Green Y-axis CC [default: {current_cc}]: ").strip()
                if not cc_input:
                    break
                cc_num = int(cc_input)
                if 0 <= cc_num <= 127:
                    self.green_particle["cc_y"] = cc_num
                    print(f"Green Y assigned to CC {cc_num}")
                    break
                else:
                    print("CC number must be between 0 and 127!")
            except ValueError:
                print("Please enter a valid number!")
    
    def get_speed_multiplier(self):
        """Calculate speed multiplier based on temperature."""
        return 1.0 + (self.temperature * (self.max_speed_multiplier - 1.0))
    
    def check_particle_collision(self, p1, p2):
        """Check if two particles are colliding."""
        dx = p1["x"] - p2["x"]
        dy = p1["y"] - p2["y"]
        distance = math.sqrt(dx * dx + dy * dy)
        return distance < (p1["radius"] + p2["radius"])
    
    def resolve_particle_collision(self, p1, p2):
        """Resolve collision between two particles."""
        # Calculate collision vector
        dx = p1["x"] - p2["x"]
        dy = p1["y"] - p2["y"]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            return  # Avoid division by zero
        
        # Normalize collision vector
        nx = dx / distance
        ny = dy / distance
        
        # Separate particles
        overlap = (p1["radius"] + p2["radius"]) - distance
        p1["x"] += nx * overlap * 0.5
        p1["y"] += ny * overlap * 0.5
        p2["x"] -= nx * overlap * 0.5
        p2["y"] -= ny * overlap * 0.5
        
        # Calculate relative velocity
        rvx = p1["vx"] - p2["vx"]
        rvy = p1["vy"] - p2["vy"]
        
        # Calculate relative velocity in collision normal direction
        speed = rvx * nx + rvy * ny
        
        # Only resolve if objects are approaching
        if speed > 0:
            return
        
        # Apply collision response (equal mass assumption)
        p1["vx"] -= speed * nx
        p1["vy"] -= speed * ny
        p2["vx"] += speed * nx
        p2["vy"] += speed * ny
    
    def update_particle(self, particle):
        """Update a single particle's position and handle boundary collisions."""
        speed_mult = self.get_speed_multiplier()
        
        # Update position
        particle["x"] += particle["vx"] * speed_mult
        particle["y"] += particle["vy"] * speed_mult
        
        # Boundary collisions
        if particle["x"] <= particle["radius"]:
            particle["x"] = particle["radius"]
            particle["vx"] = abs(particle["vx"])  # Bounce right
        elif particle["x"] >= self.sim_width - particle["radius"]:
            particle["x"] = self.sim_width - particle["radius"]
            particle["vx"] = -abs(particle["vx"])  # Bounce left
        
        if particle["y"] <= particle["radius"]:
            particle["y"] = particle["radius"]
            particle["vy"] = abs(particle["vy"])  # Bounce down
        elif particle["y"] >= self.sim_height - particle["radius"]:
            particle["y"] = self.sim_height - particle["radius"]
            particle["vy"] = -abs(particle["vy"])  # Bounce up
    
    def send_particle_midi(self, particle):
        """Send MIDI CC data based on particle position."""
        # Convert position to MIDI range (0-127)
        x_midi = int((particle["x"] / self.sim_width) * 127)
        y_midi = int((particle["y"] / self.sim_height) * 127)
        
        # Clamp to valid range
        x_midi = max(0, min(127, x_midi))
        y_midi = max(0, min(127, y_midi))
        
        # Send MIDI
        self.send_cc(particle["cc_x"], x_midi)
        self.send_cc(particle["cc_y"], y_midi)
    
    def update(self):
        """Update the particle simulation."""
        # Update both particles
        self.update_particle(self.red_particle)
        self.update_particle(self.green_particle)
        
        # Check for particle-particle collision
        if self.check_particle_collision(self.red_particle, self.green_particle):
            self.resolve_particle_collision(self.red_particle, self.green_particle)
        
        # Send MIDI data
        self.send_particle_midi(self.red_particle)
        self.send_particle_midi(self.green_particle)
    
    def handle_mouse_events(self, event):
        """Handle mouse interactions."""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check temperature slider
                temp_rect = pygame.Rect(
                    self.temp_slider_x, self.temp_slider_y,
                    self.temp_slider_width, self.temp_slider_height
                )
                
                if temp_rect.collidepoint(mouse_x, mouse_y):
                    self.dragging_temperature = True
                    handle_y = self.temp_slider_y + self.temp_slider_height - \
                              self.temperature * self.temp_slider_height
                    self.mouse_offset = mouse_y - handle_y
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging_temperature = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_temperature:
                # Update temperature
                relative_y = mouse_y - self.mouse_offset - self.temp_slider_y
                normalized = 1.0 - (relative_y / self.temp_slider_height)
                self.temperature = max(0, min(1, normalized))
    
    def draw_particle(self, particle):
        """Draw a single particle."""
        screen_x = int(self.sim_x + particle["x"])
        screen_y = int(self.sim_y + particle["y"])
        
        # Draw particle with glow effect
        pygame.draw.circle(self.screen, particle["color"], 
                         (screen_x, screen_y), particle["radius"])
        
        # Draw inner highlight
        highlight_color = tuple(min(255, c + 100) for c in particle["color"])
        pygame.draw.circle(self.screen, highlight_color,
                         (screen_x - 3, screen_y - 3), particle["radius"] // 3)
    
    def draw_simulation_area(self):
        """Draw the particle simulation boundary."""
        sim_rect = pygame.Rect(self.sim_x, self.sim_y, self.sim_width, self.sim_height)
        pygame.draw.rect(self.screen, self.WHITE, sim_rect, 2)
        
        # Draw grid for reference
        grid_spacing = 50
        for x in range(self.sim_x + grid_spacing, self.sim_x + self.sim_width, grid_spacing):
            pygame.draw.line(self.screen, (40, 40, 40), 
                           (x, self.sim_y), (x, self.sim_y + self.sim_height))
        for y in range(self.sim_y + grid_spacing, self.sim_y + self.sim_height, grid_spacing):
            pygame.draw.line(self.screen, (40, 40, 40),
                           (self.sim_x, y), (self.sim_x + self.sim_width, y))
    
    def draw_temperature_slider(self):
        """Draw the temperature control slider."""
        # Slider background
        slider_rect = pygame.Rect(
            self.temp_slider_x, self.temp_slider_y,
            self.temp_slider_width, self.temp_slider_height
        )
        pygame.draw.rect(self.screen, self.GRAY, slider_rect)
        pygame.draw.rect(self.screen, self.WHITE, slider_rect, 2)
        
        # Color gradient for temperature (blue = cold, red = hot)
        for i in range(self.temp_slider_height):
            intensity = i / self.temp_slider_height
            red = int(255 * intensity)
            blue = int(255 * (1 - intensity))
            color = (red, 0, blue)
            pygame.draw.line(self.screen, color,
                           (self.temp_slider_x + 2, self.temp_slider_y + i),
                           (self.temp_slider_x + self.temp_slider_width - 2, self.temp_slider_y + i))
        
        # Slider handle
        handle_height = 15
        handle_y = self.temp_slider_y + self.temp_slider_height - \
                   self.temperature * self.temp_slider_height - handle_height // 2
        handle_rect = pygame.Rect(
            self.temp_slider_x - 5, handle_y,
            self.temp_slider_width + 10, handle_height
        )
        pygame.draw.rect(self.screen, self.WHITE, handle_rect)
        pygame.draw.rect(self.screen, self.BLACK, handle_rect, 2)
        
        # Temperature labels
        self.draw_text("TEMP", self.temp_slider_x - 5, self.temp_slider_y - 30)
        temp_percent = f"{int(self.temperature * 100)}%"
        self.draw_text(temp_percent, self.temp_slider_x - 10, 
                      self.temp_slider_y + self.temp_slider_height + 10, 
                      self.WHITE, self.small_font)
        
        # Speed indicator
        speed_mult = self.get_speed_multiplier()
        self.draw_text(f"Speed: {speed_mult:.1f}x", self.temp_slider_x - 20,
                      self.temp_slider_y + self.temp_slider_height + 30,
                      self.GRAY, self.small_font)
    
    def draw_info_panel(self):
        """Draw particle information and CC assignments."""
        info_x = 560
        info_y = 170
        
        # Red particle info
        self.draw_text("RED PARTICLE", info_x, info_y, self.red_particle["color"])
        self.draw_text(f"X: CC{self.red_particle['cc_x']}", info_x, info_y + 25, 
                      self.WHITE, self.small_font)
        self.draw_text(f"Y: CC{self.red_particle['cc_y']}", info_x, info_y + 45,
                      self.WHITE, self.small_font)
        
        # Current red particle values
        x_val = int((self.red_particle["x"] / self.sim_width) * 127)
        y_val = int((self.red_particle["y"] / self.sim_height) * 127)
        self.draw_text(f"({x_val}, {y_val})", info_x, info_y + 65,
                      self.red_particle["color"], self.small_font)
        
        # Green particle info
        self.draw_text("GREEN PARTICLE", info_x, info_y + 90, self.green_particle["color"])
        self.draw_text(f"X: CC{self.green_particle['cc_x']}", info_x, info_y + 115,
                      self.WHITE, self.small_font)
        self.draw_text(f"Y: CC{self.green_particle['cc_y']}", info_x, info_y + 135,
                      self.WHITE, self.small_font)
        
        # Current green particle values
        x_val = int((self.green_particle["x"] / self.sim_width) * 127)
        y_val = int((self.green_particle["y"] / self.sim_height) * 127)
        self.draw_text(f"({x_val}, {y_val})", info_x, info_y + 155,
                      self.green_particle["color"], self.small_font)
    
    def draw(self):
        """Draw the particle module interface."""
        # Title
        self.draw_text("PARTICLE MODULE", 50, 50)
        
        # Instructions
        self.draw_text("Two particles bouncing and generating MIDI!", 50, 80, 
                      self.GRAY, self.small_font)
        self.draw_text("Adjust temperature to change particle speed", 50, 100,
                      self.GRAY, self.small_font)
        
        # Draw simulation elements
        self.draw_simulation_area()
        self.draw_particle(self.red_particle)
        self.draw_particle(self.green_particle)
        
        # Draw controls and info
        self.draw_temperature_slider()
        self.draw_info_panel()
    
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
    """Main function to run the Particle module."""
    particle = ParticleModule()
    
    print("MIDI Physics - Particle Module")
    print("==============================")
    print("Two particles bouncing around generating MIDI CC data!")
    print("- Red and Green particles move randomly and collide")
    print("- X and Y positions are converted to MIDI CC values")
    print("- Temperature control affects particle speed")
    
    # Setup MIDI
    if not particle.setup_midi_device():
        print("MIDI setup cancelled.")
        particle.cleanup()
        return
    
    # Setup CC assignments
    particle.setup_cc_assignments()
    
    if not particle.connect_midi():
        print("Failed to connect to MIDI device.")
        particle.cleanup()
        return
    
    print("\nControls:")
    print("- Mouse: Drag temperature slider")
    print("- ESC: Exit")
    print(f"- Red Particle: CC{particle.red_particle['cc_x']} (X), CC{particle.red_particle['cc_y']} (Y)")
    print(f"- Green Particle: CC{particle.green_particle['cc_x']} (X), CC{particle.green_particle['cc_y']} (Y)")
    
    # Run the module
    particle.run()
    particle.cleanup()

if __name__ == "__main__":
    main()