# Script de conversion d'une couche de type polyligne  en polygone
# Auteur: RIVIERE Romain
# Date: 26/08/2017

#Script ArcGIS 10.1
# Attention:  les polylignes ne doivent pas comporter d'arcs de cercle ni autres éléments exotiques - uniquement des traits droits classiques.

# ------------- Import des modules python  ----------------------
import arcpy, os

# ------------- Parametres de depart  ----------------------
polyligne = arcpy.GetParameterAsText(0)   # couche d'entité de type polyligne
output = arcpy.GetParameterAsText(1)  # Espace de travail en sortie

# ------------- Configuration environnement ARCPY ----------------------
arcpy.env.overwriteOutput = True

# Script

#listing des champs de la couche polyligne
listeChamps=[field for field in arcpy.Describe(polyligne).fields if field.name.upper() not in ("SHAPE_LENGTH","SHAPE_AREA", "SHAPE.LEN", "SHAPE.AREA")]  # tous les champs sauf ceux créés par ArCGIS
ChampGeometry=[field.type for field in listeChamps].index("Geometry") #Position champ géométrie
OIDField=[field.type for field in listeChamps].index("OID") #Position champ géométrieOID
Champs=[field.name for field in listeChamps]
Champs[ChampGeometry]="SHAPE@"
Champs[OIDField]="OID@"
nbChamps=len(Champs)


#Creation de la couche polygone et curseur d'insertion
polygone=arcpy.CreateFeatureclass_management (os.path.dirname(output), os.path.basename(output),"POLYGON", polyligne, "DISABLED", "DISABLED", polyligne)
curseurinsertion=arcpy.da.InsertCursor (polygone, Champs)

#Création du curseur de recherche au niveau de la couche polyligne
with arcpy.da.SearchCursor(polyligne,Champs) as curseurCherche:
	for row in curseurCherche:
		newrow=[el for el in row]
		line=row[ChampGeometry]
		array=arcpy.Array()
		for part in line:
			for pnt in part:
				if pnt:
					array.append(pnt)
		newrow[ChampGeometry]=arcpy.Polygon(array)
		try:
			curseurinsertion.insertRow(tuple(newrow))
		except Exception:
			e = sys.exc_info()[1]
			arcpy.AddWarning("Echec transformation polyligne ID: (Erreur: %s)"%(row[OIDField],e))
del curseurinsertion









