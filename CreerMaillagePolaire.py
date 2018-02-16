# ---------------------------------------------------------------------------
# Script permettant de créer des un maillage polaire (cercle divisé en secteurs angulaires) selon des pas d'angles et de distances données
# RIVIERE ROMAIN
# 27/09/2017
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy, os, numpy
from math import pi, cos, sin

geom = arcpy.GetParameterAsText(0) # point 
Dmax = float(arcpy.GetParameterAsText(1).replace(",","."))*1000
Pas_D = [float(el)*1000 for el in arcpy.GetParameterAsText(2).replace(",",".").split(";")] # Distances en m  (convertion km->m)
Pas_A = [pi*float(el)/180 for el in arcpy.GetParameterAsText(3).replace(",",".").split(";")] # Angles en rad (convertion ° -> rad)
output =  arcpy.GetParameterAsText(4)

#pre-traitement
maille = 0.01 #maille angulaire calcul courbure cercle
Amax = pi * 360 / 180
if len(Pas_D)==1: #pas métrique défini par l'utilisateur  -> generation de la liste des distances correspondantes
	Pas_D = numpy.arange(0,Dmax,Pas_D[0]).tolist()  # genere liste des distances à créer 
	Pas_D.append(Dmax) if Dmax not in Pas_D else None
if len(Pas_A)==1: #pas angulaire défini par l'utilisateur -> generation de la liste des angles correspondants
	Pas_A = numpy.arange(0,Amax,Pas_A[0]).tolist()  # genere liste des distances à créer
	Pas_A.append(Amax) if Amax not in Pas_A else None
Pas_D.sort()
Pas_A.sort()
#Initialisation traitement
SRS = arcpy.Describe(geom).spatialReference


#Creation secteurs angulaires
resultat = []
with arcpy.da.SearchCursor(geom,["SHAPE@X","SHAPE@Y"]) as cursor:
	for (X,Y) in [row for row in cursor]: #Recup XsYs utilisateur
		for id,angle in enumerate(Pas_A[:-1]):
			#Point 0
			points=[arcpy.Point(X,Y)]
			A1=Pas_A[id]
			A2=Pas_A[id+1]
			#Points intermediaires
			while A1 < A2:
				Xa = X + sin(A1)*Dmax
				Ya = Y + cos(A1)*Dmax
				A1+=maille
				points.append(arcpy.Point(Xa,Ya))
			#Point_final
			Xa = X + sin(A2)*Dmax
			Ya = Y + cos(A2)*Dmax
			points.append(arcpy.Point(Xa,Ya))
			#Creation polygone
			Poly=arcpy.Polygon(arcpy.Array(points),SRS)
			resultat.append([Poly,Pas_A[id]*180/pi,Pas_A[id+1]*180/pi]) #"SHAPE@","ANGLE_D","ANGLE_F"
secteurs_angles = arcpy.CreateUniqueName("sectangle","in_memory")
arcpy.CreateFeatureclass_management(os.path.dirname(secteurs_angles), os.path.basename(secteurs_angles), "POLYGON")
arcpy.AddField_management(secteurs_angles, "ANGLE_D", "SHORT")
arcpy.AddField_management(secteurs_angles, "ANGLE_F", "SHORT")
with arcpy.da.InsertCursor(secteurs_angles, ("SHAPE@","ANGLE_D","ANGLE_F")) as cursor:
	for poly in resultat:
		cursor.insertRow(poly)
		
#Creation cercles concentriques
secteurs_dist = arcpy.CreateUniqueName("sectdist","in_memory")
if 0 in Pas_D:
	del Pas_D[Pas_D.index(0)]  #supprime valeur 0
arcpy.MultipleRingBuffer_analysis(geom,secteurs_dist,Pas_D,"Meters","DIST_KM")

#Intersection des deux couches
arcpy.Intersect_analysis([secteurs_dist,secteurs_angles],output,"ALL")

#Suppression des champs inutiles
arcpy.DeleteField_management(output,[f.name for f in arcpy.ListFields(output) if not f.required and f.name not in ("ANGLE_D","ANGLE_F","DIST_KM")])