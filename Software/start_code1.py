 # -*- coding: utf-8 -*-
# DP8 – Dagplanning generator
# Auteur: Mike
# Datum: 2025-10-02

from pathlib import Path
import json  
import pprint
from datetime import date
import random
from database_wrapper import Database


# -------------------------------
# Parameters voor connectie met de database
# -------------------------------
db = Database(host="localhost", gebruiker="root", wachtwoord="200708s", database="attractiepark")

 
#input medewerker
personeelsl_id = input("voer het id van het personeelslid in:")

# -------------------------------
# Hulpfuncties    
db.connect()

select_query = f"SELECT * FROM personeelslid WHERE id = {personeelsl_id}"
personeelslid = db.execute_query(select_query)

# -------------------------------
# maximaal fysieke belasting berekenen
# -------------------------------if personeelslid[0]["verlaagde_fysieke_belasting"] > 0:

leeftijd = personeelslid[0]["leeftijd"]

if leeftijd > 0 and leeftijd <= 24:
        verlaagde_fysieke_belasting = 25
elif leeftijd > 25 and leeftijd <= 50:
        verlaagde_fysieke_belasting = 50
elif leeftijd > 50:
        verlaagde_fysieke_belasting = 20
else:
        verlaagde_fysieke_belasting = 0  # vang ongeldige waarde op

print("Verlaagde fysieke belasting:", verlaagde_fysieke_belasting)

db.close()



# Haal de eigenschappen op van een personeelslid
# altijd verbinding openen om query's uit te voeren
db.connect()

# pas deze query aan om het juiste personeelslid te selecteren




# altijd verbinding sluiten met de database als je klaar ben
pprint.pp(personeelslid) # print de resultaten van de query op een overzichtelijke manier
print(personeelslid[0]['naam'])
# voorbeeld van hoe je bij een eigenschap komt



# Haal alle onderhoudstaken op
# altijd verbinding openen om query's uit te voeren


# pas deze query aan en voeg queries toe om de juiste onderhoudstaken op te halen
select_query = (
    f"SELECT * FROM onderhoudstaak "
    f"WHERE beroepstype = '{personeelslid[0]['beroepstype']}' "
    f"AND bevoegdheid = '{personeelslid[0]['bevoegdheid']}' "
    f"AND afgerond = 0 "
    f"AND fysieke_belasting <= {verlaagde_fysieke_belasting}"
)




onderhoudstaken = db.execute_query(select_query)

# altijd verbinding sluiten met de database als je klaar bent
db.close()

#pprint.pp(onderhoudstaken) # print de resultaten van de query op een overzichtelijke manier



# verzamel alle benodigde gegevens in een dictionary
dagtakenlijst = {
    "personeelsgegevens" : {
        "naam": personeelslid[0]['naam'],  
        "leeftijd": personeelslid[0]['leeftijd'],
        "beroeptype": personeelslid[0]['beroepstype'],
        "bevoegdheid": personeelslid[0]['bevoegdheid'],
        "fysieke_belasting": personeelslid[0]['verlaagde_fysieke_belasting']
   
   
   
    },
    "weergegevens" : {
        # STAP 4: vul aan met weergegevens
    }, 
    "dagtaken": [] # STAP 2: hier komt een lijst met alle dagtaken
    ,
    "totale_duur": 0 # STAP 3: aanpassen naar daadwerkelijke totale duur
}

# uiteindelijk schrijven we de dictionary weg naar een JSON-bestand, die kan worden ingelezen door de acceptatieomgeving
with open('dagtakenlijst_personeelslid_x.json', 'w') as json_bestand_uitvoer:
    json.dump(dagtakenlijst, json_bestand_uitvoer, indent=4)



    
