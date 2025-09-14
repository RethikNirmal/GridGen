"""Main window for the Grid Connection Game."""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.algorithms.chain_builder import ChainBuilder
from src.gui.grid_canvas import GridCanvas
from src.models.grid import Grid


class MainWindow(QMainWindow):
    """Main application window for the Grid Connection Game."""

    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()
        self.setWindowTitle("Grid Connection Game")
        self.setGeometry(100, 100, 1000, 700)

        # Initialize game components
        self.grid = Grid(5, 5)
        self.chain_builder: ChainBuilder | None = None
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_step)

        # Setup UI
        self._setup_ui()
        self._setup_connections()

        # Initial canvas update
        self.canvas.update_grid(self.grid)

    def _setup_ui(self) -> None:
        """Set up the user interface components."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout (horizontal: controls on left, canvas on right)
        main_layout = QHBoxLayout(central_widget)

        # Controls panel
        controls_widget = self._create_controls_panel()
        main_layout.addWidget(controls_widget)

        # Grid canvas
        self.canvas = GridCanvas()
        main_layout.addWidget(self.canvas, 1)  # Give canvas more space

    def _create_controls_panel(self) -> QWidget:
        """Create the controls panel with parameter inputs and buttons.

        Returns:
            Widget containing all control elements
        """
        controls_widget = QWidget()
        controls_widget.setFixedWidth(250)
        layout = QVBoxLayout(controls_widget)

        # Grid dimensions section
        layout.addWidget(QLabel("Grid Dimensions:"))

        # Rows input
        rows_layout = QHBoxLayout()
        rows_layout.addWidget(QLabel("Rows:"))
        self.rows_spinbox = QSpinBox()
        self.rows_spinbox.setRange(2, 50)
        self.rows_spinbox.setValue(5)
        rows_layout.addWidget(self.rows_spinbox)
        layout.addLayout(rows_layout)

        # Columns input
        cols_layout = QHBoxLayout()
        cols_layout.addWidget(QLabel("Columns:"))
        self.cols_spinbox = QSpinBox()
        self.cols_spinbox.setRange(2, 50)
        self.cols_spinbox.setValue(5)
        cols_layout.addWidget(self.cols_spinbox)
        layout.addLayout(cols_layout)

        # Chain length section
        layout.addWidget(QLabel("Chain Settings:"))

        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel("Max Connections:"))
        self.length_spinbox = QSpinBox()
        self.length_spinbox.setRange(1, 50)
        self.length_spinbox.setValue(3)
        length_layout.addWidget(self.length_spinbox)
        layout.addLayout(length_layout)

        # Animation speed section
        layout.addWidget(QLabel("Animation:"))

        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed:"))
        self.speed_slider = QSlider()
        self.speed_slider.setOrientation(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(5)
        speed_layout.addWidget(self.speed_slider)
        layout.addLayout(speed_layout)

        # Constraint settings section
        layout.addWidget(QLabel("Constraints:"))

        self.non_crossing_checkbox = QCheckBox("Prevent chain crossing")
        self.non_crossing_checkbox.setChecked(True)  # Enabled by default
        layout.addWidget(self.non_crossing_checkbox)

        # Control buttons
        layout.addWidget(QLabel("Actions:"))

        self.connect_button = QPushButton("Connect Points")
        layout.addWidget(self.connect_button)

        self.reset_button = QPushButton("Reset Grid")
        layout.addWidget(self.reset_button)

        # Status section
        layout.addWidget(QLabel("Status:"))
        self.status_label = QLabel("Ready to connect...")
        layout.addWidget(self.status_label)

        # Statistics section
        layout.addWidget(QLabel("Statistics:"))
        self.stats_label = QLabel("0/25 points connected\n0 chains\n0 connections")
        layout.addWidget(self.stats_label)

        layout.addStretch()  # Push everything to the top
        return controls_widget

    def _setup_connections(self) -> None:
        """Connect UI signals to their respective handlers."""
        self.rows_spinbox.valueChanged.connect(self._on_grid_dimensions_changed)
        self.cols_spinbox.valueChanged.connect(self._on_grid_dimensions_changed)
        self.length_spinbox.valueChanged.connect(self._on_parameters_changed)
        self.speed_slider.valueChanged.connect(self._on_speed_changed)
        self.non_crossing_checkbox.toggled.connect(self._on_constraint_changed)
        self.connect_button.clicked.connect(self._on_connect_clicked)
        self.reset_button.clicked.connect(self._on_reset_clicked)

    def _on_grid_dimensions_changed(self) -> None:
        """Handle grid dimension changes."""
        rows = self.rows_spinbox.value()
        cols = self.cols_spinbox.value()

        self.grid = Grid(rows, cols)
        self.canvas.update_grid(self.grid)
        self._update_status("Grid resized")
        self._update_statistics()

    def _on_parameters_changed(self) -> None:
        """Handle parameter changes."""
        self._update_status("Parameters updated")

    def _on_speed_changed(self) -> None:
        """Handle animation speed changes."""
        speed = self.speed_slider.value()
        # Convert slider value (1-10) to timer interval (100-1000ms)
        interval = 1100 - (speed * 100)
        self.animation_timer.setInterval(interval)

    def _on_constraint_changed(self) -> None:
        """Handle constraint checkbox changes."""
        non_crossing_enabled = self.non_crossing_checkbox.isChecked()

        # Update the constraint in the grid
        if hasattr(self.grid, "constraint_manager"):
            if non_crossing_enabled:
                self.grid.constraint_manager.enable_constraint("Non-Crossing")
                self._update_status("Non-crossing constraint enabled")
            else:
                self.grid.constraint_manager.disable_constraint("Non-Crossing")
                self._update_status("Non-crossing constraint disabled")

    def _on_connect_clicked(self) -> None:
        """Handle connect button click to start chain building."""
        if self.animation_timer.isActive():
            self.animation_timer.stop()
            self._update_status("Animation stopped")
            return

        try:
            max_length = self.length_spinbox.value()
            self.chain_builder = ChainBuilder(self.grid, max_length)
            
            # Check grid size to decide between animated and immediate
            total_points = self.grid.rows * self.grid.cols
            if total_points > 400:  # 20x20 threshold
                # Start animated building for large grids
                self.chain_builder.start_animated_build()
                self._update_status("Building chains...")
                self.connect_button.setText("Stop Animation")
                self.animation_timer.start()
            else:
                # Build immediately for small grids
                chains = self.chain_builder.build_chains()
                self.canvas.update_chains(chains)
                self._update_status("All points connected!")
                self._update_statistics()

        except Exception as e:
            self._update_status(f"Error: {str(e)}")

    def _on_reset_clicked(self) -> None:
        """Handle reset button click to clear all connections."""
        self.animation_timer.stop()
        self.grid.reset_connections()
        self.canvas.clear_chains()
        self.connect_button.setText("Connect Points")
        self._update_status("Grid reset")
        self._update_statistics()

    def _animate_step(self) -> None:
        """Perform one step of the animation."""
        if not self.chain_builder:
            self.animation_timer.stop()
            return

        # Perform one step of chain building
        has_more_steps = self.chain_builder.build_step()
        
        # Update the canvas with current chains
        all_chains = self.chain_builder.chains.copy()
        if self.chain_builder.current_chain and self.chain_builder.current_chain.length > 0:
            all_chains.append(self.chain_builder.current_chain)
        
        self.canvas.update_chains(all_chains)
        self._update_statistics()
        
        # Check if animation is complete
        if not has_more_steps or self.chain_builder.is_animation_complete():
            self.animation_timer.stop()
            self.connect_button.setText("Connect Points")
            self._update_status("All points connected!")
        else:
            # Show progress
            connected_count = len(self.grid.get_connected_points())
            total_count = self.grid.total_points
            self._update_status(f"Building chains... {connected_count}/{total_count} points connected")

    def _update_status(self, message: str) -> None:
        """Update the status label.

        Args:
            message: Status message to display
        """
        self.status_label.setText(message)

    def _update_statistics(self) -> None:
        """Update the statistics display."""
        total_points = self.grid.total_points
        connected_points = len(self.grid.get_connected_points())
        chain_builder = getattr(self, "chain_builder", None)
        chain_count = len(chain_builder.chains if chain_builder else [])

        stats_text = f"{connected_points}/{total_points} points connected\n"
        stats_text += f"{chain_count} chains"

        if connected_points > 0:
            coverage = (connected_points / total_points) * 100
            stats_text += f"\n{coverage:.1f}% coverage"

        # Add chain length statistics
        if chain_builder and chain_builder.chains:
            total_connections = sum(
                chain.connection_count for chain in chain_builder.chains
            )
            avg_length = sum(
                chain.connection_count for chain in chain_builder.chains
            ) / len(chain_builder.chains)
            stats_text += f"\n{total_connections} total connections"
            stats_text += f"\nAvg chain length: {avg_length:.1f}"

        self.stats_label.setText(stats_text)
