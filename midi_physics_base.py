import pygame
import pygame.midi
import time
import sys
from abc import ABC, abstractmethod

class MIDIPhysicsBase(ABC):
    """
    Base class for all MIDI Physics modules.
    Provides common MIDI functionality and UI boilerplate.
    """
    
    def __init__(self, module_name="Physics Controller"):
        self.module_name = module_name
        self.midi_out = None
        self.midi_device_id = None
        self.midi_channel = 1  # Default to channel 1 (0-indexed, so this is MIDI channel 2)
        self.running = False
        
        # Initialize pygame and MIDI
        pygame.init()
        pygame.midi.init()
        
        # Create a simple display window
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption(f"MIDI Physics - {self.module_name}")
        self.clock = pygame.time.Clock()
        
        # Colors for UI
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (128, 128, 128)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        
        # Font for text
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
    def get_midi_devices(self):
        """Get list of available MIDI output devices."""
        devices = []
        for i in range(pygame.midi.get_count()):
            info = pygame.midi.get_device_info(i)
            # info returns (interf, name, input, output, opened)
            if info[3]:  # if it's an output device
                devices.append((i, info[1].decode()))
        return devices
    
    def setup_midi_device(self):
        """Interactive setup for MIDI device selection."""
        devices = self.get_midi_devices()
        
        if not devices:
            print("No MIDI output devices found!")
            return False
        
        print("\nAvailable MIDI Output Devices:")
        for i, (device_id, name) in enumerate(devices):
            print(f"{i + 1}. {name} (ID: {device_id})")
        
        while True:
            try:
                choice = input(f"\nSelect device (1-{len(devices)}) or 'q' to quit: ").strip()
                if choice.lower() == 'q':
                    return False
                
                device_index = int(choice) - 1
                if 0 <= device_index < len(devices):
                    self.midi_device_id, device_name = devices[device_index]
                    print(f"Selected: {device_name}")
                    break
                else:
                    print("Invalid selection!")
            except ValueError:
                print("Please enter a number!")
        
        # Set MIDI channel
        while True:
            try:
                channel = input(f"Enter MIDI channel (1-16) [default: {self.midi_channel + 1}]: ").strip()
                if not channel:
                    break
                
                channel_num = int(channel)
                if 1 <= channel_num <= 16:
                    self.midi_channel = channel_num - 1  # Convert to 0-indexed
                    break
                else:
                    print("MIDI channel must be between 1 and 16!")
            except ValueError:
                print("Please enter a number!")
        
        return True
    
    def connect_midi(self):
        """Connect to the selected MIDI device."""
        if self.midi_device_id is None:
            print("No MIDI device selected!")
            return False
        
        try:
            self.midi_out = pygame.midi.Output(self.midi_device_id)
            print(f"Connected to MIDI device {self.midi_device_id} on channel {self.midi_channel + 1}")
            return True
        except pygame.midi.MidiException as e:
            print(f"Failed to connect to MIDI device: {e}")
            return False
    
    def send_cc(self, cc_number, value):
        """Send a MIDI CC message."""
        if self.midi_out and 0 <= cc_number <= 127 and 0 <= value <= 127:
            # MIDI CC message: status byte (176 + channel), CC number, value
            self.midi_out.write_short(0xB0 | self.midi_channel, cc_number, int(value))
    
    def send_pitch_bend(self, value):
        """Send pitch bend data. Value should be -8192 to 8191."""
        if self.midi_out:
            # Convert to 14-bit value (0-16383, with 8192 as center)
            pitch_value = max(0, min(16383, value + 8192))
            lsb = pitch_value & 0x7F
            msb = (pitch_value >> 7) & 0x7F
            self.midi_out.write_short(0xE0 | self.midi_channel, lsb, msb)
    
    def draw_text(self, text, x, y, color=None, font=None):
        """Helper method to draw text on screen."""
        if color is None:
            color = self.WHITE
        if font is None:
            font = self.font
        
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))
    
    def draw_connection_status(self):
        """Draw MIDI connection status on screen."""
        status_text = "MIDI: "
        if self.midi_out:
            status_text += f"Connected (Device {self.midi_device_id}, Ch {self.midi_channel + 1})"
            color = self.GREEN
        else:
            status_text += "Not Connected"
            color = self.RED
        
        self.draw_text(status_text, 10, 10, color, self.small_font)
    
    def handle_base_events(self, event):
        """Handle common events (like quit)."""
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
        return True
    
    @abstractmethod
    def update(self):
        """Update the physics simulation. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def draw(self):
        """Draw the module-specific graphics. Must be implemented by subclasses."""
        pass
    
    def run(self):
        """Main run loop."""
        self.running = True
        
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if not self.handle_base_events(event):
                    self.running = False
                    break
            
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
            self.clock.tick(60)  # 60 FPS
    
    def cleanup(self):
        """Clean up resources."""
        if self.midi_out:
            self.midi_out.close()
        pygame.midi.quit()
        pygame.quit()

def test_midi_connection():
    """Test function to verify MIDI setup works."""
    
    class TestModule(MIDIPhysicsBase):
        def __init__(self):
            super().__init__("MIDI Test")
            self.test_cc = 74  # Filter cutoff on many synths
            self.test_value = 0
            self.direction = 1
        
        def update(self):
            # Slowly sweep a CC value up and down
            self.test_value += self.direction * 0.5
            if self.test_value >= 127:
                self.test_value = 127
                self.direction = -1
            elif self.test_value <= 0:
                self.test_value = 0
                self.direction = 1
            
            # Send the CC
            self.send_cc(self.test_cc, self.test_value)
        
        def draw(self):
            # Draw test info
            self.draw_text("MIDI Connection Test", 50, 100)
            self.draw_text(f"Sending CC {self.test_cc}: {int(self.test_value)}", 50, 150)
            self.draw_text("You should hear filter cutoff sweeping", 50, 200)
            self.draw_text("Press ESC to exit", 50, 300, self.GRAY)
    
    test = TestModule()
    
    print("MIDI Physics Controller - Connection Test")
    print("========================================")
    
    # Setup MIDI
    if not test.setup_midi_device():
        print("MIDI setup cancelled.")
        test.cleanup()
        return
    
    if not test.connect_midi():
        print("Failed to connect to MIDI device.")
        test.cleanup()
        return
    
    print("\nStarting test... You should hear a filter sweep.")
    print("Close the window or press ESC to exit.")
    
    # Run the test
    test.run()
    test.cleanup()

if __name__ == "__main__":
    test_midi_connection()
    