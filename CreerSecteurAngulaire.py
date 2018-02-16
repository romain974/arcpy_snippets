# ---------------------------------------------------------------------------
# Script permettant de créer une géométrie à partir d'un point, d'une distance et de deux angles
# RIVIERE ROMAIN
# 24/02/2016
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy
from math import pi, cos, sin

geom = arcpy.GetParameterAsText(0)
D = float(arcpy.GetParameterAsText(1).replace(",",".")) # D en km
A1 = float(arcpy.GetParameterAsText(2).replace(",",".")) # A en degre
A2 =  float(arcpy.GetParameterAsText(3).replace(",",".")) # A en degre
output =  arcpy.GetParameterAsText(4)


if arcpy.Exists(output):
	arcpy.Delete_management(output)


maille = 0.01 #maille angle

if A1 > A2:
	A1, A2 = A2, A1

#Pretraitement
D = D*1000 # km  -> m
A1 = pi * A1 / 180  # deg -> rad
A2 = pi * A2 / 180  # deg -> rad

#Recup XY utilisateur
(X,Y) = [row for row in arcpy.da.SearchCursor(geom,["SHAPE@X","SHAPE@Y"])][0]

#Calcul des points formant le secteur angulaire
points=[arcpy.Point(X,Y)] #liste initiale
#Ajout points intermediaires
A = A1  #angle de depart
while A < A2:
	Xa = X + sin(A)*D
	Ya = Y + cos(A)*D
	A+=maille
	points.append(arcpy.Point(Xa,Ya))
#ajout dernier point
Xa = X + sin(A2)*D
Ya = Y + cos(A2)*D
points.append(arcpy.Point(Xa,Ya))


#Creation polygone
Poly=arcpy.Polygon(arcpy.Array(points),arcpy.SpatialReference(2154))

#output geometry:
arcpy.CopyFeatures_management(Poly, output)