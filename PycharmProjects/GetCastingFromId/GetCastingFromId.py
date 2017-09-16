# ----------------------------------------------------
# RECUPERATION DE TOUT LES CREDITS D'UNE LISTE DE FILMS TMDB
# INPUT : fichier CSV avec une liste d'id tmdb
# OUTPUT : produit un fichier avec les crédits par id
# REPRISE TOLEREE
# ----------------------------------------------------

# 0. creation du fichier d'output s'il n'existe pas
# 1. calcul du dernier id récupéré (pour la reprise)

import json
import requests
import csv
import datetime
import os

# Ma clé d'authentification pour l'API tmdb & fichiers input/output
api_key = "04fe0efd7c6e8c505128686c70ae5825"
input_filename = "allmovies_cleaned ID Only.csv"
output_filename = "allmovies_casting.csv"

# ----------------------------------------------------
# Si le fichier n'existe pas on le crée et initialise les headers
# On garde 5 acteurs : nom + gender + nb d'acteurs
# Puis 1 directeur : nom + gender + nb de directeurs
# Puis 1 producteur + le nombre, 1 screenplayer, 1 editeur
if not os.path.isfile(output_filename):
    with open(output_filename, "w") as foutput:
        writer = csv.writer(foutput, delimiter=';', lineterminator='\n')
        headers = list()
        headers.append("id")
        for i in range(1, 6):
            headers.append("actor" + str(i) + "_name")
            headers.append("actor" + str(i) + "_gender")
        headers.append("actor_number")
        headers.append("director_name")
        headers.append("director_gender")
        headers.append("director_number")
        headers.append("producer_name")
        headers.append("producer_number")
        headers.append("screeplay_name")
        headers.append("editor_name")
        print("creating headers")
        writer.writerow(headers)

# ----------------------------------------------------
# On détecte le dernier Id qui a été renseigné
with open(output_filename, "r",  encoding='utf-8-sig') as foutput:
        reader = csv.reader(foutput)
        skip_label = True
        last_row_done = 0
        for row in reader:
            last_row_done += 1

# ----------------------------------------------------
# On parcourt le fichier d'input, on choppe le dernier Id et on requete l'API
with open(input_filename, "r",  encoding='utf-8-sig') as finput, open(output_filename, "a", encoding='utf-8') as foutput:
    reader = csv.reader(finput)
    writer = csv.writer(foutput, delimiter=';', lineterminator='\n')
    curseur_row_input = 0
    for row in reader:
        curseur_row_input += 1
        if curseur_row_input > last_row_done:
            last_row_done += 1
            id_movie = row[0]
            # ----------------------------------------------------
            # REQUETE & REMPLISSAGE DES CREDITS
            # ----------------------------------------------------

            # On fait la requete
            req_credits = requests.get("https://api.themoviedb.org/3/movie/" + id_movie +
                                       "/credits?api_key=" + api_key)
            dic_credits = json.loads(req_credits.text)
            nrow = dict()
            nrow["id"] = id_movie

            # Valeurs par défaut
            # REALISATEUR NOM, gender ET NOMBRE
            director_name = "none"
            director_gender = 1
            director_number = 0
            take_first_director = True

            # PRODUCER NOM & NOMBRE
            producer_name = "none"
            producer_number = 0
            take_first_producer = True

            # EDITOR & SCREENPLAY
            editor_name = "none"
            take_first_editor = True
            writer_name = "none"
            take_first_writer = True

            if dic_credits.get("crew", "nocrew") != "nocrew":

                for crewmember in dic_credits["crew"]:
                    if crewmember["job"] == "Director":
                        director_number += 1
                        if take_first_director:
                            director_name = crewmember.get("name", "none")
                            director_gender = crewmember.get("gender", 0)
                            take_first_director = False

                    elif crewmember["job"] == "Producer":
                        producer_number += 1
                        if take_first_producer:
                            producer_name = crewmember.get("name", "none")
                            take_first_producer = False

                    elif crewmember["job"] == "Editor" and take_first_editor:
                        editor_name = crewmember.get("name", "none")
                        take_first_editor = False

                    elif crewmember["job"] == "Screenplay" and take_first_writer:
                        writer_name = crewmember.get("name", "none")
                        take_first_writer = False

            # RECUPERATION DU TOP5 ACTEURS : nom, gender & décompte du nb d'acteurs
            # valeurs par défaut
            actor_number = 0
            for i in range(1, 6):
                nrow["actor" + str(i) + "_name"] = "none"
                nrow["actor" + str(i) + "_gender"] = 0
            # parcours des acteurs
            if dic_credits.get("cast", "nocast") != "nocast":
                for crewmember in dic_credits["cast"]:
                    actor_number += 1
                    if crewmember["order"] < 5:
                        nrow["actor" + str(crewmember["order"]+1) + "_name"] = crewmember.get("name", "none")
                        nrow["actor" + str(crewmember["order"]+1) + "_gender"] = crewmember.get("gender", 0)

            # On remplit le dictionnaire avec les valeurs récoltées
                        # On garde 5 acteurs : nom + gender + nb d'acteurs
                        # Puis 1 directeur : nom + gender + nb de directeurs
                        # Puis 1 producteur + le nombre, 1 screenplayer, 1 editeur
            nrow["actor_number"] = actor_number
            nrow["director_name"] = director_name
            nrow["director_gender"] = director_gender
            nrow["director_number"] = director_number
            nrow["producer_name"] = producer_name
            nrow["producer_number"] = producer_number
            nrow["writer_name"] = writer_name
            nrow["editor_name"] = editor_name

            # Ecriture du résultat
            if str(id_movie) != "id":
                print("[" + str(datetime.datetime.now().time()) + "] Requesting credits for id=" + str(id_movie))
                writer.writerow(list(nrow.values()))
