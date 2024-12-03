import numpy as np
GripperHeight = 100 #altura garra

Depth = 12 #profundidad
GripperWidth = 30 #ancho garra
Theta = np.arctan2(GripperHeight, GripperWidth)
Phi = np.arctan2(GripperWidth, GripperHeight)
GripperHeightGift = 2
WallThickness = 2 #espesor pared


BarHeightThick = 2
BarHeightThin = 1
BarThinLength = 3

NBars = 8

NRowsTactile = 10
NColsTactile = 4

sangria_grilla = 0.5  # Margen desde los bordes en el eje Z (mm)
cantidad_grilla_vertical = 4  # Número deseado de líneas verticales

sangria_grilla_horizontal = 2 
cantidad_grilla_horizontal = 6  # Número deseado de líneas horizontales
radio_cilindro_grilla = 0.5  # Radio de los cilindros (mm)

borde = 1  # Separación en mm

base_extra = 10
abajo_base_extra = 8
