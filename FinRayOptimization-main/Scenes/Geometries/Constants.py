import numpy as np
GripperHeight = 100 #altura garra

Depth = 25 #profundidad
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

sangria_grilla = 1  # Margen desde los bordes en el eje Z (mm)
cantidad_grilla_vertical = 8  # Número deseado de líneas verticales
radio_cilindro_grilla = 1  # Radio de los cilindros (mm)