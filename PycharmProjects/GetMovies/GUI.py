# ----------------------------------------------------
# COMPLETION A PARTIR D'UN FICHIER DE TITRES + AUTRES CARAC, QUI
# COMPLETE AVEC TOUS LES DETAILS + CASTING D'UN FILM SUR TMDB
# ----------------------------------------------------

from tkinter import messagebox
from tkinter import *
import json
import requests
import time
import csv
import datetime
import os


class MyFirstGUI:

    def __init__(self, master):
        self.master = master
        master.title("Get movie features")
        master.minsize(width=100, height=100)

        # Si on appuie sur entrée dans la boite on lance la recherche
        def key(event):
            if str(event.char) == "\r":
                self.getfeatures()
            if event.keycode == 27:
                root.quit()

        # Création des widgets & evenements
        self.frame = Frame(self.master, width=100, height=100)
        self.filename_entry = Entry(self.frame, width=80)
        self.filename_entry.insert(0, "movies.csv")
        self.filename_entry.bind("<Key>", key)
        self.resultat = Label(self.frame, text="Input file name, must be in same folder as exe, then press GO")
        self.getfeatures_button = Button(self.frame, text="GO", command=self.getfeatures)

        # Positionnement des widgets
        self.frame.pack()
        self.resultat.pack()
        self.filename_entry.pack()
        self.filename_entry.focus_set()
        self.getfeatures_button.pack()

    # Récupération des features des films dans le fichier saisi
    def getfeatures(self):

        logfilename = "log.txt"
        logfile = open(logfilename, "w", encoding='utf-8')
        logwrite = csv.writer(logfile)

        # si on atteint 40 requetes sur l'API tmdb on fait une pause de 10 sec pour éviter de se prendre des erreurs
        def throttle(prequest):
            prequest += 1
            if prequest > 39:
                printlog("40 requests reached. Pausing 10 sec")
                time.sleep(10)
                prequest = 0
            return prequest

        # On logge à la fois sur la console et dans un fichier
        def printlog(logstr):
            logstr = str(datetime.datetime.now().time()) + ":" + logstr + "\n"
            print(logstr)
            logfile.write(logstr)
            
        # Ma clé d'authentification pour l'API tmdb
        api_key = "04fe0efd7c6e8c505128686c70ae5825"

        # Création d'une liste de dictionnaires de ces films
        # Parcours de la liste, complétude via tmdb (throttling), si pas trouvé ou si pas le bon titre id_tmdb = 0
        # Stockage du fichier résultat et affichage du nombre de films trouvé / pas trouvés à chaque itération
        # Lecture du fichier qui comprend des attributs +  une colonne de titre
        # headernames = ("title","imdb_rating","viewing_date","personal_rating","children")
        filename = self.filename_entry.get()
        if not os.path.isfile(filename):
            messagebox.showinfo("File not found", "File not found, existing application")
            root.quit()
        filename_temp = "moviestemp.csv"

        with open(filename, encoding='utf-8-sig') as file, open(filename_temp, "w", encoding='utf-8') as filetemp:
            reader = csv.reader(file, delimiter=';', )
            writer = csv.writer(filetemp, delimiter=';', lineterminator='\n', quoting=csv.QUOTE_MINIMAL)

            movie_index = 0
            movie_total = len(open(filename).readlines())
            failed_lines = 0
            max_request = 0
            # On écrase les headers uniquement à partir de la première requete réussie
            # (au cas où on file un fichier sans toutes les colonnes en entrée)
            need_to_rewrite_header = False

            # Création de ma liste de films
            movies_list = list()

            # ----------------------------------------------
            # Lecture du fichier
            # Format attendu : CSV séparé par ";" d'excel, headers en premiere ligne
            # 1. je lis une ligne
            # 2. si id_tmdb = 0 ou pas de header "id_tmdb" je requete
            # 3. si la requete réussit, je complete les champs + j'écris la nouvelle ligne
            # 4. si id_tmdb >0 j'écris la ligne existante afin d'éviter de requeter pour rien
            # ----------------------------------------------
            firstrow = True
            for row in reader:
                movie_index += 1
                # Stockage des headers + on coupe les caractères spéciaux en début & fin de ligne
                if firstrow:
                    header_list = row
                    printlog("1/" + str(movie_total) + ".Skipping headers : " + str(row))
                    writer.writerow(header_list)
                    firstrow = False
                else:
                    movie_features = dict()
                    row_list = row

                    # On lit la ligne avec les valeurs du film
                    for col_index in range(len(row_list)):
                        movie_features[header_list[col_index]] = row_list[col_index]

                    # On ajoute la ligne dans ma liste de film
                    movies_list.append(movie_features)

                    # On teste s'il y a une clé tmdb_id et sinon on la rajoute
                    if not ("tmdb_id" in movie_features):
                        movie_features["tmdb_id"] = 0

                    # S'il y a déjà un identifiant tmdb_id, pas besoin d'aller chercher des infos du film
                    if int(movie_features["tmdb_id"]) > 0:
                        printlog(str(movie_index) + "/" + str(movie_total) + ". Line already filled, skipped.")
                        writer.writerow(row)
                        continue
                    else:
                        # --------------------------------------------
                        # Récupération des caractéristiques de chaque film avec tmdb=0 (overview, credits, détails)
                        # --------------------------------------------
                        # Get the movie result & convert in dictionary format
                        moviename = movie_features["title"]
                        max_request = throttle(max_request)
                        req_result = requests.get("https://api.themoviedb.org/3/search/movie?api_key=" + api_key +
                                                  "&query=" + moviename)
                        dic_result = json.loads(req_result.text)

                        # On ne continue que si on a trouvé au moins un résultat
                        if dic_result["total_results"] > 0:
                            printlog(str(movie_index) + "/" + str(movie_total) + ".Found " + str(
                                dic_result["total_results"]) + " results for " + moviename + ". Taking first one")

                            # On prend l'Id du premier sur la liste
                            movieid = str(dic_result["results"][0]["id"])

                            # Get the credits (for director(s), etc) for the movie
                            max_request = throttle(max_request)
                            req_credits = requests.get("https://api.themoviedb.org/3/movie/" + movieid +
                                                       "/credits?api_key=" + api_key)
                            dic_credits = json.loads(req_credits.text)

                            # Get the details (for budget, etc) for the movie
                            max_request = throttle(max_request)
                            req_details = requests.get(
                                "https://api.themoviedb.org/3/movie/" + movieid + "?api_key=" + api_key)
                            dic_details = json.loads(req_details.text)

                            # append a list of genres to result of movie
                            # lis_genres=list()
                            # for genreindex in dic_result["results"][0]["genre_ids"]:
                            #     lis_genres.append(dic_genres[genreindex])
                            # dic_result["results"][0]["genres"]=lis_genres

                            # Création d'un dictionnaire "rateau" pour une exploitation bigdata
                            # quand plusieurs genres ou plusieurs directeurs, on garde le premier et on renseigne le nb
                            movie_features["tmdb_id"] = movieid

                            # Récupération données générales
                            movie_features["original_language"] = dic_result["results"][0]["original_language"]
                            movie_features["vote_count"] = dic_result["results"][0]["vote_count"]
                            movie_features["vote_average"] = dic_result["results"][0]["vote_average"]
                            movie_features["release_date"] = dic_result["results"][0]["release_date"]
                            movie_features["original_title"] = dic_result["results"][0]["original_title"]

                            # Récupération données détaillées
                            movie_features["budget"] = dic_details["budget"]
                            movie_features["revenue"] = dic_details["revenue"]
                            movie_features["runtime"] = dic_details["runtime"]
                            movie_features["imdb_id"] = dic_details["imdb_id"]

                            if len(dic_details["production_countries"]) > 0:
                                movie_features["production_country"] = dic_details["production_countries"][0]["name"]
                                movie_features["production_countries_number"] = len(dic_details["production_countries"])
                            else:
                                movie_features["production_country"] = "none"
                                movie_features["production_countries_number"] = 0

                            if len(dic_details["production_companies"]) > 0:
                                movie_features["production_company"] = dic_details["production_companies"][0]["name"]
                                movie_features["production_companies_number"] = len(dic_details["production_companies"])
                            else:
                                movie_features["production_company"] = "none"
                                movie_features["production_companies_number"] = 0

                            if len(dic_details["genres"]) > 0:
                                movie_features["genre"] = dic_details["genres"][0]["name"]
                                movie_features["genre_number"] = len(dic_details["genres"])
                            else:
                                movie_features["genre"] = "none"
                                movie_features["genre_number"] = 0
                            # Récupération données credits : on prend le 1er réalisateur et on les compte
                            director_number = 0
                            movie_features["director"] = "none"
                            take_first_director = True
                            for crewmember in dic_credits["crew"]:
                                if crewmember["job"] == "Director":
                                    director_number += 1
                                    if take_first_director:
                                        movie_features["director"] = crewmember["name"]
                                        take_first_director = False
                            movie_features["director_number"] = director_number

                            # Récupération données credits : : on prend le 1er producteur et on les compte
                            producer_number = 0
                            movie_features["producer"] = "none"
                            take_first_producer = True
                            for crewmember in dic_credits["crew"]:
                                if crewmember["job"] == "Producer":
                                    producer_number += 1
                                    if take_first_producer:
                                        movie_features["producer"] = crewmember["name"]
                                        take_first_producer = False
                            movie_features["producer_number"] = producer_number

                            # Récupération données credits : nb d'acteurs
                            nbacteurs = len(dic_credits["cast"])
                            movie_features["actor_number"] = nbacteurs

                            # On convertit le dico en liste et on l'écrit dans le fichier
                            newline = list()
                            for key in movie_features:
                                newline.append(movie_features[key])
                            writer.writerow(newline)

                            # Dès lors qu'on modifie 1 ligne ALORS il faudra réécrire les headers à la fin
                            if not need_to_rewrite_header:
                                need_to_rewrite_header = True
                                newheader = list()
                                for key in movie_features:
                                    newheader.append(key)

                        else:
                            failed_lines += 1
                            printlog(str(movie_index) + "/" + str(movie_total) + ".Failed. "
                                                                                 "Found no results for " + moviename)
                            writer.writerow(row)

        file.close()
        filetemp.close()
        os.remove(filename)
        os.rename(filename_temp, filename)

        # On réécrit les headers si besoin
        if need_to_rewrite_header:
            with open(filename, encoding='utf-8-sig') as file, open(filename_temp, "w", encoding='utf-8') as filetemp:
                reader = csv.reader(file, delimiter=';')
                writer = csv.writer(filetemp, delimiter=';', lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
                firstrow = True
                # S'il y a déjà le même nombre de headers on skippe tout
                for row in reader:
                    if firstrow and len(row) != len(newheader):
                        writer.writerow(newheader)
                        printlog("Rewriting headers")
                        firstrow = False
                    else:
                        writer.writerow(row)
                        firstrow = False
            file.close()
            filetemp.close()
            os.remove(filename)
            os.rename(filename_temp, filename)

        # Décompte des lignes ratées
        printlog("Failed to find a movie for " + str(failed_lines) + " on " + str(movie_total))
        logfile.close()
        messagebox.showinfo("Exit", "Finished, check log.txt")

root = Tk()
my_gui = MyFirstGUI(root)
root.mainloop()
