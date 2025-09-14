# Grid Connection Game

A visual grid-based game where points are connected into chains following specific length and geometric constraints.

## Game Overview

This game creates an N×M grid of points and connects them into multiple separate chains/paths. The goal is to ensure every point in the grid is part of at least one chain, while respecting chain length limits and preventing chains from crossing each other geometrically.

## Core Mechanics

### Grid System
- **Grid Size**: Configurable N×M grid (e.g., 5×5, 8×6, etc.)
- **Points**: Each grid position contains a point that can be connected
- **Adjacency**: Points can connect to all 8 adjacent neighbors (horizontal, vertical, and diagonal)

### Connection Rules
- **Chain Length**: Each chain can have at most `length` connections (where chain_length = points_count - 1)
- **Direct Connections**: Each point can connect directly to at most 2 other points
- **Non-Crossing**: Chains cannot cross each other geometrically (configurable)
- **Coverage**: All points must be connected to some chain (no isolated points allowed)
- **Independence**: Chains are separate - they don't need to connect to each other
- **Linear Structure**: Chains are strictly linear paths with no branching

### Flexible Constraint System
The application features a modular constraint system that allows:
- **Enable/Disable Constraints**: Toggle different rules on/off
- **Non-Crossing Constraint**: Prevents geometric intersection of chain segments
- **Distance Constraints**: Optional minimum/maximum connection distances
- **Extensible Design**: Easy to add new constraint types

### Parameters
1. **N (Rows)**: Number of rows in the grid
2. **M (Columns)**: Number of columns in the grid  
3. **Length**: Maximum number of connections allowed in each chain (points = length + 1)
4. **Constraints**: Configurable rules that connections must follow

## Features

### Visual Interface
- **Grid Display**: Clear visualization of all points in the grid
- **Real-time Animation**: Watch chains being formed step-by-step
- **Smart Performance**: Automatic animation for large grids (>20×20), instant for small grids
- **Dynamic Sizing**: Dots automatically scale for optimal visibility on any grid size
- **Animation Speed Control**: Adjustable speed for the connection process
- **Uniform Coloring**: All chains displayed in the same color for consistency

### Interactive Controls
- **Dynamic Grid Sizing**: Change grid dimensions (N×M) on the fly
- **Length Parameter**: Adjust maximum chain length dynamically
- **Constraint Controls**: Enable/disable different connection constraints
- **Connect Button**: Start the automated connection algorithm (becomes "Stop Animation" during large grid processing)
- **Reset Functionality**: Clear all connections and start over

### Algorithm Visualization
- **Step-by-step Progress**: See each connection being made in real-time
- **Chain Formation**: Watch how the algorithm decides to start new chains vs extend existing ones
- **Coverage Tracking**: Visual feedback showing which points are connected
- **Performance Scaling**: Handles grids up to 50×50 without freezing the interface
- **Progress Indicators**: Real-time status showing "Building chains... X/Y points connected"

## Game Flow

1. **Setup Phase**
   - Configure grid size (N×M)
   - Set maximum chain length parameter
   - Grid displays all unconnected points

2. **Connection Phase** 
   - Click "Connect" button to start algorithm
   - Algorithm creates chains while respecting length constraints
   - Visual animation shows chains being formed
   - Process continues until all points are covered

3. **Completion**
   - All points are now part of some chain
   - Multiple separate chains may exist
   - Each chain respects the maximum length constraint

## Architecture Overview

### Technology Stack
- **Python 3.13**: Core programming language
- **PyQt6**: GUI framework for interactive interface
- **Modular Design**: Clean separation of concerns across layers

### Core Components
1. **Models** (`src/models/`): Data structures (Point, Grid, Chain)
2. **Algorithms** (`src/algorithms/`): Chain building logic
3. **Constraints** (`src/constraints/`): Flexible constraint validation system
4. **GUI** (`src/gui/`): User interface and visualization
5. **Tests** (`tests/`): Unit tests for all components

### Key Features
- **Constraint System**: Modular, extensible validation framework
- **Non-Crossing Detection**: Geometric intersection algorithms
- **Real-time Visualization**: PyQt6-based grid and chain display
- **Interactive Controls**: Dynamic parameter adjustment

## Example Scenarios

### Small Grid (3×3, Length=2)
```
● ● ●
● ● ●  →  Chain 1: A→B→C (length=2, 3 points)
● ● ●      Chain 2: D→E→F (length=2, 3 points)
            Chain 3: G→H→I (length=2, 3 points)
```

### Larger Grid (5×4, Length=3)
Multiple chains with ≤3 connections each (≤4 points per chain) covering all 20 points

### Performance Examples
- **Small grids (≤20×20)**: Instant chain building
- **Large grids (>20×20)**: Animated step-by-step building
- **Maximum tested**: 50×50 (2,500 points) with smooth animation

## Getting Started

### Prerequisites
- Python 3.12 or higher
- Virtual environment (recommended)

### Installation
```bash
# Clone or navigate to the project directory
cd grid_gen

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the application
python main.py
```

## Usage Guide

### Basic Controls
1. **Grid Size**: Adjust rows and columns using spinboxes (2-50 range supported)
2. **Max Connections**: Set maximum connections per chain
3. **Constraints**: Enable/disable non-crossing constraint
4. **Animation Speed**: Control visualization speed for animated building
5. **Connect**: Start the automatic chain building (shows "Stop Animation" for large grids)
6. **Reset**: Clear all connections and start over

### Understanding the Display
- **Blue Circles**: Unconnected points (size scales with grid dimensions)
- **Red Circles**: Connected points (size scales with grid dimensions)
- **Red Lines**: Chain connections between points
- **Statistics Panel**: Shows coverage progress and chain metrics
- **Status Bar**: Shows current operation ("Building chains... X/Y points connected")

## Success Criteria

- ✅ Every point is part of exactly one chain
- ✅ No chain exceeds the maximum connection count (length parameter)
- ✅ Each point has at most 2 direct connections (linear chains only)
- ✅ Chains use only valid 8-directional adjacency connections
- ✅ Configurable non-crossing constraint prevents geometric intersections
- ✅ Visual representation clearly shows all connections
- ✅ Modular constraint system allows easy extension

## Extensibility

### Adding New Constraints
The constraint system is designed for easy extension:

```python
from src.constraints.base import ConnectionConstraint

class CustomConstraint(ConnectionConstraint):
    def validate(self, grid, point1, point2):
        # Your validation logic here
        return True
    
    def get_description(self):
        return "description of your constraint"

# Add to grid's constraint manager
grid.constraint_manager.add_constraint(CustomConstraint())
```

### Architecture Benefits
- **Modular Design**: Easy to modify or extend individual components
- **Separation of Concerns**: Clear boundaries between data, logic, and presentation
- **Flexible Constraints**: Add/remove validation rules without changing core algorithms
- **Testable Code**: Each component can be tested independently