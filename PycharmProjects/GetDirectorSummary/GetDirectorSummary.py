import requests
from bs4 import BeautifulSoup

# Récupération de la page exacte wikipedia à partir du nom de l'auteur non normalisé
director = "eric rohmer"
director  = director.replace(" ","+")
mysearchURL = "https://en.wikipedia.org/w/index.php?search="+director
mysummaryURL = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&redirects=true&exintro&explaintext&titles="
http = requests.get(mysearchURL)
#On vire les 30 premiers caractères pour trouver le nom normalisé de l'auteur
exactURL = mysummaryURL + http.url[30:]
#Récupération du résumé
fullresults= requests.get(exactURL).text
summaryindex = fullresults.find("extract")
summary =fullresults[summaryindex+10:-5]

print(summary)





# soup = BeautifulSoup(r.data, "lxml")

