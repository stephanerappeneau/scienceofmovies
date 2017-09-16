import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#chargement fichiers
dfa_full = pd.read_csv("AllMoviesDetailsCleaned.csv", sep=";", low_memory=False, parse_dates=["release_date"])
dfb_full = pd.read_csv("AllMoviesCastingRaw.csv", sep=";", low_memory=False)

#Fusion fichiers par ids communes
df_full = pd.merge(dfa_full, dfb_full, on='id')
#Création fichier avec les seules données pertinentes
df_rel = df_full[['id','director_name','release_date']].sort_values(by='director_name',ascending=True)

df_rel.fillna(pd.Timestamp('1800-01-01'))
df_rel['release_date2']=df_rel['release_date'].map(lambda x:x.year)
#On réindexe
df_rel2 = df_rel.reset_index(drop = True)

df = df_rel2
# valeurs retenues pour chaque réal: nombre de films, liste des années de sortie des films
dir_time = dict()
x = 0
# parcours de la liste de réals
while x < len(df):
    dir_name = df.loc[x, 'director_name']
    dir_time[dir_name] = {'movie_nb': 0, 'movie_nb_inclnodate': 0, 'dates': []}
    # les réals sont par ordre alphabétique, on parcourt la liste de films de chacun
    while df.loc[x, 'director_name'] == dir_name:
        dir_time[dir_name]['movie_nb_inclnodate'] += 1
        if df.loc[x, 'release_date2'] != 1800:
            dir_time[dir_name]['movie_nb'] += 1
            # on ajoute la date à la liste si elle n'y est pas déjà
            if df.loc[x, 'release_date2'] not in dir_time[dir_name]['dates']:
                dir_time[dir_name]['dates'].append(df.loc[x, 'release_date2'])

        x += 1
        if x == len(df):
            break

# CALCUL DE LA MOYENNE
for key in dir_time:
    # temps entre films: valeur de 2 ans par défaut
    if dir_time[key]['movie_nb'] == 1:
        min_date = min(dir_time[key]['dates'])
        max_date = max(dir_time[key]['dates'])
        avg = 2
    else:
        # gestion du cas particulier quand il y a N films tous defaultés en 1800 (dir_time[key]['movie_nb']=0)
        if dir_time[key]['movie_nb'] == 0:
            # valeur par défaut de 2 ans pour le premier film
            min_date = min(dir_time[key]['dates'])
            max_date = max(dir_time[key]['dates'])
            avg = round((max_date - min_date + 2) / dir_time[key]['movie_nb_inclnodate'], 1)
        else:
            avg = 2
            min_date = 1800
            max_date = 1800

    # piste d'audit
    dir_time[key]['min_date'] = min_date
    dir_time[key]['max_date'] = max_date
    dir_time[key]['avg'] = avg
