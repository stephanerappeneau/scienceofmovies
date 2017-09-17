# ----------------------------------------------------
# CREATION FROM SCRATCH (reprise tolérée) D'UN FICHIER QUI
# RECUPERE TOUS LES DETAILS D'UN FILM SUR TMDB
# This product uses the TMDb API but is not endorsed or certified by TMDb
# ----------------------------------------------------

import json
import requests
import csv
import datetime
import os

filename = "allmoviesdetails.csv"

#retrieve API KEY
api_key_file = "apikey.txt"
with open(api_key_file, "r") as filehandle:
    api_key =  next(csv.reader(filehandle))[0]

nbofreq = 0
request = "https://api.themoviedb.org/3/movie/latest?api_key="+api_key

# Si le fichier n'existe pas on le crée et initialise les headers
if not os.path.isfile(filename):
    with open(filename, "w") as filehandle:
        writer = csv.writer(filehandle, delimiter=';', lineterminator='\n')
        querystring = "https://api.themoviedb.org/3/movie/15?api_key=" + api_key
        req_details = requests.get(querystring)
        dic_details = json.loads(req_details.text)
        headers = list()
        for key in dic_details:
            headers.append(key)
        # on ajoute les headers nb companies, countries & languages
        headers.append("production_companies_number")
        headers.append("production_countries_number")
        headers.append("spoken_languages_number")
        writer.writerow(headers)
        print(str(datetime.datetime.now().time()) + " : headers")

# Sinon on l'ouvre (en lecture) pour trouver le dernier ID
with open(filename, "r", encoding='utf-8') as filehandle:
    reader=csv.reader(filehandle)
    for row in reader:
            try:
                rowlist = row[0].split(";")
                rowcount = rowlist[6]
            except:
                pass


# Puis on l'ouvre en écriture pour le remplir
with open(filename, "a", encoding='utf-8') as filehandle:

    # Récupération de l'index du dernier film dispo sur tmdb
    querystring = "https://api.themoviedb.org/3/movie/latest?api_key="+api_key
    req_details = requests.get(querystring)
    dic_details = json.loads(req_details.text)
    latest_tmdb_movie_index = dic_details["id"]
    rowcount=int(rowcount)
    # On récupère et stocke chaque film entre {nb de lignes déjà dans le fichier} et {latest movie}
    while rowcount < latest_tmdb_movie_index:
        writer = csv.writer(filehandle, delimiter=';', lineterminator='\n')
        querystring = "https://api.themoviedb.org/3/movie/" + str(rowcount) + "?api_key=" + api_key
        req_details = requests.get(querystring)
        dic_details = json.loads(req_details.text)
        print(str(datetime.datetime.now().time()) + " : fetching details for id " + str(rowcount))

        # on fabrique la liste "rateau" des détails du film
        # genres : on garde tout mais on concatène
        # production_companies : on ne garde que la 1ere + le nombre
        # production_countries : on ne garde que la 1ere + le nombre
        # spoken_languages : on ne garde que la 1ere + le nombre
        liste_details = list()

        production_companies_number = 0
        production_countries_number = 0
        spoken_languages_number = 0

        # Si la 1ere clé est status code = 34 alors pas de données => on écrit l'Id et on passe au suivant
        for key in dic_details:
            if key == "status_code":
                liste_details.append(rowcount)
                break
            elif key == "genres":
                genres = ""
                for genre_temp in dic_details[key]:
                    genres += genre_temp["name"] + "|"
                genres = genres[:-1]
                liste_details.append(genres)
            elif key == "production_companies":
                if len(dic_details[key]) > 0:
                    production_companies = dic_details[key][0]["name"]
                else:
                    production_companies = "none"
                liste_details.append(production_companies)
                production_companies_number = len(dic_details[key])
            elif key == "production_countries":
                if len(dic_details[key]) > 0:
                    production_countries = dic_details[key][0]["name"]
                else:
                    production_countries = "none"
                liste_details.append(production_countries)
                production_countries_number = len(dic_details[key])
            elif key == "spoken_languages":
                if len(dic_details[key]) > 0:
                    spoken_languages = dic_details[key][0]["name"]
                else:
                    spoken_languages = "none"
                liste_details.append(spoken_languages)
                spoken_languages_number = len(dic_details[key])
            else:
                liste_details.append(dic_details[key])

        liste_details.append(production_companies_number)
        liste_details.append(production_countries_number)
        liste_details.append(spoken_languages_number)

        writer.writerow(liste_details)

        try:
            print(str(datetime.datetime.now().time()) + " : " + dic_details["title"] + " (id=" + str(rowcount) + ")")
        except KeyError:
            print(str(datetime.datetime.now().time()) + " : Ghost id (id=" + str(rowcount) + ")")

        rowcount += 1
