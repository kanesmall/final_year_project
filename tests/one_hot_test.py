from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor
from sklearn.decomposition import PCA
import pandas as pd
import numpy as np
import pymysql

def queryDb_onehot(sqlQuery, params):
    db = pymysql.connect(host='kanesmall.co.uk', user='kanesmal', password='wj5Gy%EE44#iK@j1', db='kanesmal_training_data', charset='utf8')

    cursor = db.cursor()
    cursor.execute(sqlQuery, params)
    cursor = cursor.fetchall()

    db.commit() # Save changes
    db.close() # Disconnect from the server

    return cursor

ids = [5,6,8,11,12,13,14,15,16,17,18,20,21]

genres = []

for id in ids:
    sql = "SELECT genres.genre_name FROM films INNER JOIN film_genres ON film_genres.film_id = films.film_id INNER JOIN genres ON film_genres.genre_id = genres.genre_id WHERE films.film_id = %s;"
    results = queryDb_onehot(sql, id)
    tempList = []
    for result in results:
        tempList.append(str(result[0]))
    genres.append(tempList)

genredf = pd.Series(genres)

genredf_onehot = pd.get_dummies(genredf.apply(pd.Series).stack(), prefix='genre').sum(level=0)