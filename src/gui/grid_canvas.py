"""Grid canvas for visualizing the grid and chains."""

from typing import List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtWidgets import QWidget

from src.models.chain import Chain
from src.models.grid import Grid
from src.models.point import Point


class GridCanvas(QWidget):
    """Canvas widget for drawing the grid and chains."""

    def __init__(self) -> None:
        """Initialize the grid canvas."""
        super().__init__()
        self.setMinimumSize(400, 400)

        # Drawing properties
        self.base_point_radius = 8  # Base radius for small grids
        self.line_width = 3
        self.margin = 50

        # Colors
        self.background_color = Qt.GlobalColor.white
        self.grid_color = Qt.GlobalColor.lightGray
        self.unconnected_point_color = Qt.GlobalColor.blue
        self.connected_point_color = Qt.GlobalColor.red
        self.chain_color = Qt.GlobalColor.red

        # Data
        self.grid: Optional[Grid] = None
        self.chains: List[Chain] = []

    def update_grid(self, grid: Grid) -> None:
        """Update the grid to be displayed.

        Args:
            grid: The grid to display
        """
        self.grid = grid
        self.chains = []
        self.update()

    def update_chains(self, chains: List[Chain]) -> None:
        """Update the chains to be displayed.

        Args:
            chains: List of chains to display
        """
        self.chains = chains
        self.update()

    def clear_chains(self) -> None:
        """Clear all chain visualizations."""
        self.chains = []
        self.update()

    def paintEvent(self, event) -> None:
        """Handle paint events to draw the grid and chains.

        Args:
            event: The paint event
        """
        if not self.grid:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Clear background
        painter.fillRect(self.rect(), self.background_color)

        # Calculate grid layout
        self._calculate_layout()

        # Draw grid lines (optional, subtle)
        self._draw_grid_lines(painter)

        # Draw chains first (so they appear behind points)
        self._draw_chains(painter)

        # Draw points
        self._draw_points(painter)

    def _calculate_layout(self) -> None:
        """Calculate the layout parameters for drawing the grid."""
        if not self.grid:
            return

        # Available drawing area
        available_width = self.width() - 2 * self.margin
        available_height = self.height() - 2 * self.margin

        # Calculate spacing between points
        if self.grid.cols > 1:
            self.point_spacing_x = available_width / (self.grid.cols - 1)
        else:
            self.point_spacing_x = 0

        if self.grid.rows > 1:
            self.point_spacing_y = available_height / (self.grid.rows - 1)
        else:
            self.point_spacing_y = 0

        # Starting position (top-left of grid area)
        self.start_x = self.margin
        self.start_y = self.margin

        # Calculate dynamic point radius based on grid density
        self.point_radius = self._calculate_point_radius()

    def _calculate_point_radius(self) -> int:
        """Calculate the appropriate point radius based on grid dimensions.

        Returns:
            Optimal point radius for the current grid size
        """
        if not self.grid:
            return self.base_point_radius

        # Use the smaller spacing (either x or y) to determine radius
        min_spacing = min(self.point_spacing_x, self.point_spacing_y)
        
        # Point radius should be a fraction of the minimum spacing
        # to prevent overlap and ensure visual clarity
        optimal_radius = int(min_spacing * 0.15)  # 15% of minimum spacing
        
        # Clamp between reasonable bounds
        min_radius = 2  # Minimum viable radius for visibility
        max_radius = self.base_point_radius  # Don't exceed base radius
        
        return max(min_radius, min(optimal_radius, max_radius))

    def _draw_grid_lines(self, painter: QPainter) -> None:
        """Draw subtle grid lines.

        Args:
            painter: The painter to draw with
        """
        if not self.grid:
            return

        pen = QPen(self.grid_color, 1, Qt.PenStyle.DotLine)
        painter.setPen(pen)

        # Draw vertical lines
        for col in range(self.grid.cols):
            x = int(self.start_x + col * self.point_spacing_x)
            painter.drawLine(
                x,
                int(self.start_y),
                x,
                int(self.start_y + (self.grid.rows - 1) * self.point_spacing_y),
            )

        # Draw horizontal lines
        for row in range(self.grid.rows):
            y = int(self.start_y + row * self.point_spacing_y)
            painter.drawLine(
                int(self.start_x),
                y,
                int(self.start_x + (self.grid.cols - 1) * self.point_spacing_x),
                y,
            )

    def _draw_points(self, painter: QPainter) -> None:
        """Draw all points in the grid.

        Args:
            painter: The painter to draw with
        """
        if not self.grid:
            return

        for point in self.grid.get_all_points():
            self._draw_point(painter, point)

    def _draw_point(self, painter: QPainter, point: Point) -> None:
        """Draw a single point.

        Args:
            painter: The painter to draw with
            point: The point to draw
        """
        x, y = self._point_to_canvas_coords(point)

        # Choose color based on connection status
        if point.connected:
            color = self.connected_point_color
        else:
            color = self.unconnected_point_color

        # Draw point as filled circle
        painter.setPen(QPen(color, 2))
        painter.setBrush(color)
        painter.drawEllipse(
            x - self.point_radius,
            y - self.point_radius,
            2 * self.point_radius,
            2 * self.point_radius,
        )

    def _draw_chains(self, painter: QPainter) -> None:
        """Draw all chains.

        Args:
            painter: The painter to draw with
        """
        pen = QPen(self.chain_color, self.line_width)
        painter.setPen(pen)

        for chain in self.chains:
            self._draw_chain(painter, chain)

    def _draw_chain(self, painter: QPainter, chain: Chain) -> None:
        """Draw a single chain.

        Args:
            painter: The painter to draw with
            chain: The chain to draw
        """
        if len(chain.points) < 2:
            return

        # Draw lines between consecutive points in the chain
        for i in range(len(chain.points) - 1):
            point1 = chain.points[i]
            point2 = chain.points[i + 1]

            x1, y1 = self._point_to_canvas_coords(point1)
            x2, y2 = self._point_to_canvas_coords(point2)

            painter.drawLine(x1, y1, x2, y2)

    def _point_to_canvas_coords(self, point: Point) -> tuple[int, int]:
        """Convert grid point coordinates to canvas pixel coordinates.

        Args:
            point: The point to convert

        Returns:
            Tuple of (x, y) canvas coordinates
        """
        canvas_x = int(self.start_x + point.y * self.point_spacing_x)
        canvas_y = int(self.start_y + point.x * self.point_spacing_y)
        return canvas_x, canvas_y

    def sizeHint(self):
        """Provide size hint for the widget."""
        from PyQt6.QtCore import QSize

        return QSize(500, 500)
