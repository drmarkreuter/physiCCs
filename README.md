# physiCCs - Physics-Based MIDI Controllers

Transform physics simulations into expressive musical controllers! physiCCs is a suite of three Python modules that use real physics principles to generate dynamic MIDI data for controlling synthesizers and DAWs.

## The Three Modules

### 🌍 Module 1: Gravity
Experience the pull of different worlds with three MIDI CC controllers that fall back to zero under adjustable gravity.

**How it works:** Drag the sliders up and watch them fall back down at different rates depending on the gravity setting. Zero gravity means controllers stay where you put them, while maximum gravity pulls them back to zero quickly.

**Gravity Settings:**
- **Zero G** - Controllers float in space
- **Moon** - Gentle drift back to zero  
- **Earth** - Natural gravity feel
- **Jupiter** - Strong pull back to baseline
- **Black Hole** - Instant snap back to zero

**Musical Applications:** Perfect for filter sweeps that naturally decay, envelope-like parameter control, or any effect where you want parameters to "fall" back to a resting state.

---

### ⚛️ Module 2: Particle
Watch two colorful particles bounce around a grid, converting their chaotic motion into musical data.

**How it works:** Red and green particles move randomly around a bounded area, bouncing off walls and each other. Their X and Y coordinates are continuously translated into MIDI CC values, creating evolving, unpredictable parameter changes.

**Features:**
- **Two Particles** - Red and green, each controlling separate X/Y MIDI channels
- **Realistic Collisions** - Particles bounce off boundaries and each other
- **Temperature Control** - Increase heat to make particles move faster (more collisions = more dynamic MIDI)
- **Visual Feedback** - Real-time display of MIDI values and particle positions

**Musical Applications:** Ideal for creating evolving soundscapes, spatial effects, randomized modulation, or adding organic movement to static sounds.

---

### 🔄 Module 3: Pendulum
A beautifully realistic swinging pendulum that generates smooth, musical motion.

**How it works:** Drag the pendulum bob to set it swinging. The pendulum follows authentic physics, with longer lengths creating slower swings. Choose between MIDI CC output (centered around value 64) or pitch bend data.

**Features:**
- **Authentic Physics** - Real pendulum motion with proper damping
- **Variable Length** - Longer pendulums swing slower, shorter ones swing faster
- **Dual Output Modes:**
  - **MIDI CC Mode** - Position converted to controller data (0-127)
  - **Pitch Bend Mode** - Position converted to pitch wheel data (±8192)
- **Interactive Control** - Drag the bob to start swinging, adjust length in real-time

**Musical Applications:** Excellent for organic vibrato, smooth filter sweeps, panning effects, or any parameter that benefits from natural, cyclical motion.

---

## Technical Foundation

All three modules share a common foundation:
- **Python + PyGame** - Reliable cross-platform graphics and MIDI
- **60 FPS Physics** - Smooth, responsive simulations
- **Flexible MIDI Routing** - Assign any MIDI device and channel
- **Custom CC Assignment** - Map controls to your specific synthesizer setup
- **Real-time Visual Feedback** - See exactly what MIDI data is being generated

## Getting Started

Each module can be run independently and configured for your specific MIDI setup. The physics simulations run in real-time at 60 FPS, providing smooth, musical control over your synthesizers.

Whether you want the controlled chaos of bouncing particles, the natural decay of gravity, or the hypnotic rhythm of a swinging pendulum, physiCCs turns physics into music.

## Installation

### Core Dependencies:

pygame>=2.0.0 - The main library we're using for graphics and MIDI
pygame-ce>=2.4.0 - Alternative community edition (either one works)

Optional Extensions:

pymunk and pybox2d - Physics libraries mentioned in your original spec (commented out since we're not using them yet, but easy to enable for future enhancements)

Development Tools:

pytest, black, flake8 - Common Python development tools (commented out, but easy to enable)

### bash
git clone https://github.com/yourusername/physiCCs.git

cd physiCCs

pip install -r requirements.txt

