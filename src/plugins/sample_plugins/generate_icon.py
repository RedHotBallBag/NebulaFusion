#!/usr/bin/env python3
# Generate a simple star icon for the sample plugin

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPainter, QColor, QPixmap, QIcon
from PyQt6.QtCore import Qt, QPointF
import sys

def create_star_icon():
    # Create a 128x128 pixmap (will be scaled down for smaller sizes)
    size = 128
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    # Create a painter
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Draw a star
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(255, 215, 0))  # Gold color
    
    # Draw a simple star using drawPolygon
    points = []
    for i in range(5):
        # Outer point
        angle = i * 4 * 3.14159 / 5 - 3.14159 / 2  # Offset to start from top
        x = size // 2 + (size // 2 - 10) * 0.9 * math.cos(angle)
        y = size // 2 + (size // 2 - 10) * 0.9 * math.sin(angle)
        points.append(QPointF(x, y))
        
        # Inner point (for star shape)
        angle = (i + 0.5) * 4 * 3.14159 / 5 - 3.14159 / 2
        x = size // 2 + (size // 2 - 10) * 0.4 * math.cos(angle)
        y = size // 2 + (size // 2 - 10) * 0.4 * math.sin(angle)
        points.append(QPointF(x, y))
    
    # Draw the star
    if points:
        painter.drawPolygon(points)
    
    painter.end()
    return pixmap

if __name__ == "__main__":
    import math
    
    # Create the application
    app = QApplication(sys.argv)
    
    # Create the icon
    icon_pixmap = create_star_icon()
    
    # Save the icon in multiple sizes
    sizes = [16, 32, 48, 128]
    for size in sizes:
        scaled_pixmap = icon_pixmap.scaled(size, size, 
                                         Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation)
        scaled_pixmap.save(f"icon_{size}.png")
        print(f"Saved icon_{size}.png")
    
    # Also save as icon.png (default size 48x48)
    icon_pixmap.scaled(48, 48, 
                      Qt.AspectRatioMode.KeepAspectRatio,
                      Qt.TransformationMode.SmoothTransformation).save("icon.png")
    print("Saved icon.png")
    
    print("Icons generated successfully.")
