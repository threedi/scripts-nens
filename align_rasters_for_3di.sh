#----------------------------INFO-------------------------------------------------
# extent_aanpassen.sh
# Script voor het aanpassen van een raster zodat het raster dezelfde vorm en extent heeft als een ander raster
# handig als je 3Di berekeningen doet en je rasters nog niet overeen komen. Maak een backup van je bestanden voor je dit script probeert.
# Stan van den Bosch, Nelen & Schuurmans, juni 2016

#INPUT:
#- Raster met juiste extent (extentraster)
#- Raster met foute extent/en of vorm (inputraster)
#- Aannamewaarde voor wanneer inputraster geen waarde heeft
#OUTPUT:
#- Inputraster, maar dan met dezelfde extent en vorm als het extentraster. Op de plekken waar inputraster geen waardes had zijn 
#AANNAME:
#- Inputraster en extentraster hebben dezelfde projectie

# AANROEPEN
# sh extent_aanpassen.sh [extentraster] [inputraster] [aannamewaarde] [outputraster]
# bijvoorbeeld aanroepen als volgt: C:\Users\stan.vandenbosch\Documents\Q0156\algemeen_script>extent_aanpassen.sh dem.tif interceptie.tif 1 interceptie_nieuw.tif

# Als je meerdere keren wil runnen, kun je de eerste en opvolgende keren bepaalde commandos uitcommentarieren om het script te versnellen
# deze commando's zijn aangegeven met "BATCH 1" (1e en opvolgende keer runnen uitcommentarieren) en "BATCH 2" (2e en opvolgende keren runnen uitcommentarieren)


# Script voor het aanpassen van een raster zodat het raster dezelfde vorm en extent heeft als een ander raster
# handig als je 3Di berekeningen doet en je rasters nog niet overeen komen.
# input:
# - Raster met juiste extent (extentraster)
# - Raster met foute extent/en of vorm (inputraster)
# - Aannamewaarde voor wanneer inputraster geen waarde heeft
# output:
# - Inputraster, maar dan met dezelfde extent en vorm als het extentraster. Op de plekken waar inputraster geen waardes had zijn 
# aanname:
# - Inputraster en extentraster hebben dezelfde projectie
# 
# --- Snelle instructies voor gevorderden ---
# 
# Werkt alleen met Windows/OSGeo4W, niet op Linux/via Putty
# extent_aanpassen.sh [extentraster] [inputraster] [aannamewaarde] [outputraster]
# 
# De argumenten zijn:
# [extentraster]   output krijgt deze extent en vorm
# [inputraster]    het raster dat aangepast wordt
# [aannamewaarde]  aannamewaarde indien raster geen waarde heeft
# [outputraster]   outputraster
# 
# --- Uitgebreidere instructies ---
# 
# Voorbereiding:
# 1. Zet al je input in één map
# 2. Zet het script in dezelfde map
# 3. Start het OSGeo4W command prompt (zwart schermpje met witte letters)
# 4. navigeer met 'cd' naar de map waar je input en het script staat
# 5. Pas het volgende voorbeeldcommando aan naar jouw voorbeeld (zie onder voor inputs) 'sh extent_aanpassen.sh extentraster.tif inputraster.tif 3.59 outputraster.tif'
# 6. Voer het aangepaste commando uit
# 7. Python zal tijdens de berekeningen 3 maal vastlopen. Je krijgt dan een venster met 'python.exe has stopped working'. Kies telkens 'Close the program'
# 8. Je output staat in dezelfde map als je input en het script


#----------------------------SCRIPT--------------------------------------------------
echo "extentraster  :" $1 # input; output get this extent and shape
echo "inputraster   :" $2 # input; the raster to adjust
echo "aannamewaarde :" $3 # assumption value when the raster doesnt have a value
echo "outputraster  :" $4 # output raster
echo "
AANNAME: PROJECTIES VAN JE RASTERS ZIJN GELIJK
"

echo "---
ENENRASTER MAKEN (RASTER MET OVERAL 1 WAAR WAARDE NODIG IS)
---" # BATCH 2
gdal_calc.py --co="COMPRESS=DEFLATE" --NoDataValue -9999 -A $1 --outfile "enenraster_ongec.tif" --calc="1" # BATCH 2

echo "---
VULRASTER MAKEN (RASTER MET AANNAMEWAARDE DIE INGEVULD WORDT ALS INPUTRASTER GEEN WAARDE HEEFT
---"
gdal_calc.py --co="COMPRESS=DEFLATE" --NoDataValue -9999 -A $1 --outfile "vulraster_ongec.tif" --calc="$3"

echo "---
INPUTRASTER IN VULRASTER VOEGEN
---"
gdalwarp $2 "vulraster_ongec.tif"   

echo "---
VERMENIGVULDIGEN MET ENENRASTER (ALLEEN BENODIGDE WAARDES OVERHOUDEN)
---"
gdal_calc.py --co="COMPRESS=DEFLATE" --NoDataValue -9999 -A "enenraster_ongec.tif" -B "vulraster_ongec.tif" --outfile "outputraster_ongec.tif" --calc="A*B"

echo "rm enenraster_ongec.tif" # BATCH 1
rm enenraster_ongec.tif # BATCH 1
echo "rm vulraster_ongec.tif"
rm vulraster_ongec.tif

echo "---
COMPRIMEREN
---"
gdal_translate -co COMPRESS=DEFLATE "outputraster_ongec.tif" $4

echo "rm outputraster_ongec.tif"
rm "outputraster_ongec.tif"

echo "
Script uitgevoerd.
Script gemaakt door Stan van den Bosch, Nelen & Schuurmans, juni 2016"