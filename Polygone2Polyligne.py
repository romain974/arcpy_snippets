# Script de conversion d'une couche de type polygone en polyligne
# Auteur: RIVIERE Romain
# Date: 24/07/2013

#Script ArcGIS 10.1

# ------------- Import des modules python  ----------------------
import arcpy

# ------------- Parametres de depart  ----------------------
polygone = arcpy.GetParameterAsText(0)   # couche d'entité de type polygone
bdd = arcpy.GetParameterAsText(1)  # Espace de travail en sortie
nom = arcpy.GetParameterAsText(2)  # nom de la couche ligne en sortie

# ------------- Configuration environnement ARCPY ----------------------
arcpy.env.overwriteOutput = True

# Script

#listing des champs de la couche polygone
listeChamps=[field for field in arcpy.Describe(polygone).fields if field.name.upper() not in ("SHAPE_LENGTH","SHAPE_AREA")]  # tous les champs sauf ceux créés par ArCGIS
ChampGeometry=[field.type for field in listeChamps].index("Geometry") #Position champ géométrie
OIDField=[field.type for field in listeChamps].index("OID") #Position champ géométrieOID
Champs=[field.name for field in listeChamps]
Champs[ChampGeometry]="SHAPE@"
Champs[OIDField]="OID@"
nbChamps=len(Champs)


#Creation de la couche polylignes et curseur d'insertion
ligne=arcpy.CreateFeatureclass_management (bdd, nom,"POLYLINE", polygone, "DISABLED", "DISABLED", polygone)
curseurinsertion=arcpy.da.InsertCursor (ligne, Champs)

#Création du curseur de recherche au niveau de la couche polygone
curseurCherche=arcpy.da.SearchCursor(polygone,Champs)

for row in curseurCherche:
	newrow=[]
	for i in range(nbChamps):
		if i==ChampGeometry: 
			newrow.append( row[i].boundary())  # convertion polygone polyligne
		else:
			newrow.append(row[i])  # copie des autres champs
	curseurinsertion.insertRow(tuple(newrow))
	
del curseurCherche, curseurinsertion
	