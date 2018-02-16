# ---------------------------------------------------------------------------
# Script permettant de créer des secteurs angulaires (cercle divisé en secteurs angulaires) selon un pas donné
# RIVIERE ROMAIN
# 18/05/2016
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy, os
from math import pi, cos, sin

geom = arcpy.GetParameterAsText(0) # point 
D = float(arcpy.GetParameterAsText(1).replace(",",".")) # D en km
Pas = float(arcpy.GetParameterAsText(2).replace(",",".")) # Pas angulaire en degrés
output =  arcpy.GetParameterAsText(3)


if arcpy.Exists(output):
	arcpy.Delete_management(output)


maille = 0.01 #maille angulaire calcul courbure cercle


#Pretraitement
D = D*1000 # km  -> m
Pas = pi * Pas / 180  # deg -> rad

#Initialisation traitement
SRS = arcpy.Describe(geom).spatialReference
resultat = []
Amax = pi * 360 / 180

for (X,Y) in [row for row in arcpy.da.SearchCursor(geom,["SHAPE@X","SHAPE@Y"])]:  #Recup XY utilisateur
	A = 0
	while A <= Amax:
		#Calcul des points formant le secteur angulaire
		points=[arcpy.Point(X,Y)] #liste initiale
		#Ajout points intermediaires
		A1 = A  #angle de depart
		A2 = A + Pas #angle de fin
		while A1 < A2:
			Xa = X + sin(A1)*D
			Ya = Y + cos(A1)*D
			A1+=maille
			points.append(arcpy.Point(Xa,Ya))
		#ajout dernier point
		Xa = X + sin(A2)*D
		Ya = Y + cos(A2)*D
		points.append(arcpy.Point(Xa,Ya))
		#Creation polygone
		Poly=arcpy.Polygon(arcpy.Array(points),SRS)
		#incremente angle
		A = A2
			#Ajout polygone au resultat
		resultat.append([Poly,A*180/pi-Pas*180/pi,A*180/pi,D])

#output geometry:
arcpy.CreateFeatureclass_management(os.path.dirname(output), os.path.basename(output), "POLYGON")
arcpy.AddField_management(output, "ANGLE_D", "SHORT")
arcpy.AddField_management(output, "ANGLE_F", "SHORT")
arcpy.AddField_management(output, "DISTANCE", "SHORT")
cursor = arcpy.da.InsertCursor(output, ("SHAPE@","ANGLE_D","ANGLE_F", "DISTANCE"))
for poly in resultat:
    cursor.insertRow(poly)
del cursor