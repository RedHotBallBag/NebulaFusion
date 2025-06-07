from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt, QRect
import sys

def create_icon():
    # Create a 24x24 pixmap
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    # Create a painter
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Draw a star
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(255, 215, 0))  # Gold color
    
    # Draw a simple star
    points = [
        (12, 2), (15, 9), (23, 9), (16, 14), 
        (19, 21), (12, 17), (5, 21), (8, 14),
        (1, 9), (9, 9)
    ]
    
    # Draw the star
    painter.drawPolygon(*[points[0], points[1], points[2], points[3], points[4], 
                         points[5], points[6], points[7], points[8], points[9]])
    
    painter.end()
    return QIcon(pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon = create_icon()
    
    # Save the icon
    pixmap = icon.pixmap(24, 24)
    pixmap.save("icon.png")
    
    print("Icon created as icon.png")
