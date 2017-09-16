import pandas as pd
import csv

# Chargement du fichier dans un dataframe
df = pd.read_csv("AllMoviesCastingRaw.csv", sep=";")

# Création d'une liste des 85929  réalisateurs uniques
# Parcours de mon dataframe initial,
# pour chaque ligne on popule un dictionnaire "clé=nom réalisateur ; valeur = dictionnaire (genre, nb films, fidelité)
# exemple pour herzog : ("klaus kinski" : 5, "claudia cardinale" : 1, ...)
# Inclure acteurs 1..X ;  producteur ;  éditeur ;  screenplayer avec divers coeff
# Proposition d'algo : fidélité = somme des occurences >1 / nb de films

df = df.sort_values(by="director_name", ascending=True)

# On parcourt la liste des credits
current_director = ""
compte = 0
all_directors = dict()
for x in range(0, len(df)):

    # Si on n'avait pas déja rencontré ce directeur on le crée & on initialise le genre (par défaut 2 = masculin)
    director_name = df.loc[x, "director_name"]
    if director_name not in all_directors:
        all_directors[director_name] = dict([("gender", 2), ("movies_nb", 0), ("fidelity", 0), ("collab", dict())])
        all_directors[director_name]["gender"] = df.loc[x, "director_gender"]
        if all_directors[director_name]["gender"] == 0:
            all_directors[director_name]["gender"] = 2

    # On met à jour le nb de films
    all_directors[director_name]["movies_nb"] += 1

    # Fonction qui incrémente le nb d'acteurs rencontrés par rapport à un dictionaire d'acteurs
    # On exclut les "none" et le réalisateur lui même (autocollab !)
    def incr_collab(director_root_name, name, collab_dict, coeff):
        if "none(" in name or name == "none" or director_root_name in name:
            return collab_dict
        if name not in collab_dict:
            collab_dict[name] = 0
        collab_dict[name] += coeff
        return collab_dict

    coeff_actor = 1
    coeff_editor = 1
    coeff_writer = 1
    coeff_producer = 1

    # On MAJ la fréquence de collab avec les acteurs
    for y in range(1, 6):
        collab_name = df.loc[x, "actor" + str(y) + "_name"]
        all_directors[director_name]["collab"] = incr_collab(director_name, collab_name,
                                                             all_directors[director_name]["collab"], coeff_actor)

    # On MAJ la fréquence de collab avec le producteur
    collab_name = df.loc[x, "producer_name"]+"(producer)"
    all_directors[director_name]["collab"] = incr_collab(director_name, collab_name,
                                                         all_directors[director_name]["collab"], coeff_producer)

    # On MAJ la fréquence de collab avec le monteur
    collab_name = df.loc[x, "editor_name"]+"(editor)"
    all_directors[director_name]["collab"] = incr_collab(director_name, collab_name,
                                                         all_directors[director_name]["collab"], coeff_editor)

    # On MAJ la fréquence de collab avec le screenwriter
    collab_name = df.loc[x, "screeplay_name"]+"(writer)"
    all_directors[director_name]["collab"] = incr_collab(director_name, collab_name,
                                                         all_directors[director_name]["collab"], coeff_writer)

    print(x)

# Une fois que tout ça c'est fait on calcule le coeff de fidelité : sum (freq>=2) / nb de films
# 1.99 pour être sur qu'on ne garde que les noms rencontrés au moins 2 fois
# et on écrit le résultat dans un fichier
with open("director_attr.csv", "w", encoding='utf-8') as filehandle:
    writer = csv.writer(filehandle, delimiter=';', lineterminator='\n')

    row = ["director_name", "gender", "movies_nb", "fidelity_rel", "fidelity_abs"]
    writer.writerow(row)
    for director_name in all_directors:
        if director_name != "none":
            for collab_freq in all_directors[director_name]["collab"]:
                if all_directors[director_name]["collab"][collab_freq] >= 2:
                    all_directors[director_name]["fidelity"] += all_directors[director_name]["collab"][collab_freq]

            fid_abs = all_directors[director_name]["fidelity"]
            fid_rel = round(fid_abs / all_directors[director_name]["movies_nb"], 1)

            row = [director_name, all_directors[director_name]["gender"], all_directors[director_name]["movies_nb"],
                   fid_rel, fid_abs]
            writer.writerow(row)

# log
with open('logfile.csv', 'w', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter=';', lineterminator='\n')
    writer.writerow(("director_name", "movies_nb", "fidelity_abs", "collab1_name", "collab1_freq"))
    for director_name in all_directors:
        if director_name != "none" and all_directors[director_name]["fidelity"] > 0:
            row = list()
            row.append(director_name)
            row.append(all_directors[director_name]["movies_nb"])
            row.append(all_directors[director_name]["fidelity"])
            # On trie les collaborateurs par apparition décroissante
            mdic = all_directors[director_name]["collab"]
            marray = sorted(mdic.items(), reverse=True, key=lambda i: i[1])
            mdic = dict(marray)
            for key in mdic:
                if mdic[key] >= 2:
                    row.append(key)
                    row.append(mdic[key])
            writer.writerow(row)
