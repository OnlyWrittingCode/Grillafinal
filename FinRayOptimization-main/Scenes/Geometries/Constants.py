import numpy as np
GripperHeight = 100 #altura garra

Depth = 10 #profundidad
GripperWidth = 30 #ancho garra
Theta = np.arctan2(GripperHeight, GripperWidth)
Phi = np.arctan2(GripperWidth, GripperHeight)
GripperHeightGift = 2
WallThickness = 3 #espesor pared


BarHeightThick = 2
BarHeightThin = 1
BarThinLength = 3

NBars = 9

NRowsTactile = 10
NColsTactile = 4

sangria_grilla = 0  # Margen desde los bordes en el eje Z (mm)
cantidad_grilla_vertical = 6  # Número deseado de líneas verticales

sangria_grilla_horizontal = 5 
cantidad_grilla_horizontal = 9  # Número deseado de líneas horizontales
radio_cilindro_grilla = 0.5  # Radio de los cilindros (mm)

borde = 1  # Separación en mm