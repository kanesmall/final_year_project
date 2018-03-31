from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor
from sklearn.decomposition import PCA
import pandas as pd
import numpy as np
import pymysql, math

def queryDb(sqlQuery):
    db = pymysql.connect(host='kanesmall.co.uk', user='kanesmal', password='wj5Gy%EE44#iK@j1', db='kanesmal_training_data', charset='utf8')

    cursor = db.cursor()
    cursor.execute(sqlQuery)
    cursor = cursor.fetchall()

    db.commit() # Save changes
    db.close() # Disconnect from the server

    return cursor

def queryDb_onehot(sqlQuery, params):
    db = pymysql.connect(host='kanesmall.co.uk', user='kanesmal', password='wj5Gy%EE44#iK@j1', db='kanesmal_training_data', charset='utf8')

    cursor = db.cursor()
    cursor.execute(sqlQuery, params)
    cursor = cursor.fetchall()

    db.commit() # Save changes
    db.close() # Disconnect from the server

    return cursor

def insertData(sqlQuery, params):
    db = pymysql.connect(host='kanesmall.co.uk', user='kanesmal', password='wj5Gy%EE44#iK@j1', db='kanesmal_training_data', charset='utf8')

    # Prepare a cursor object using the cursor() method
    cursor = db.cursor()

    # Execute an SQL query using the execute() method.
    results = cursor.execute(sqlQuery, params)

    db.commit() # Save changes
    db.close() # Disconnect from the server

    return results

# Training data
sqlQuery_training = "SELECT film_budget, film_runtime, film_trailer_view_count, film_trailer_like_count, film_trailer_dislike_count, film_vote_average FROM films WHERE film_status = 'Released';"
search_training = queryDb(sqlQuery_training)

df = pd.DataFrame(columns=['budget','runtime','trailer view count','trailer like count','trailer dislike count', 'user rating'])

for idx, item in enumerate(search_training):
    df.loc[idx] = item
    # print df # For testing purposes

sqlQuery_ids = "SELECT film_id FROM films WHERE film_status = 'Released';"
search_ids = queryDb(sqlQuery_ids)

genres = []

for id in search_ids:
    sql = "SELECT genres.genre_name FROM films INNER JOIN film_genres ON film_genres.film_id = films.film_id INNER JOIN genres ON film_genres.genre_id = genres.genre_id WHERE films.film_id = %s;"
    results = queryDb_onehot(sql, str(id[0]))
    tempList = []
    for result in results:
        tempList.append(str(result[0]))
    genres.append(tempList)

genredf = pd.Series(genres)

genredf_onehot = pd.get_dummies(genredf.apply(pd.Series).stack(), prefix='genre').sum(level=0)

df = df.join(genredf_onehot)

# Impute NULL values and set to -1
df = df.fillna(-1)

# features = ['budget','runtime','trailer view count','trailer like count','trailer dislike count', 'user rating']
# Separating out the features
x = df.drop('user rating', axis=1)
# Separating out the target
y = df.loc[:,['user rating']].values
# Standardizing the features
x = StandardScaler().fit_transform(x)

# Apply dimensionality reduction to reduce from multiple columns down to 2
pca = PCA(n_components=2)
principalComponents = pca.fit_transform(x)
principalDf = pd.DataFrame(data = principalComponents, columns = ['principal component 1', 'principal component 2'])

# Concatenate the target values back onto the final dataframe
finalDf = pd.concat([principalDf, df[['user rating']]], axis = 1)

# print finalDf # For testing purposes

regressor = DecisionTreeRegressor(max_depth=2)
regressor.fit(np.array([finalDf['principal component 1'].T, finalDf['principal component 2']]).T, finalDf['user rating'])

# Test data
sqlQuery_test = "SELECT film_budget, film_runtime, film_trailer_view_count, film_trailer_like_count, film_trailer_dislike_count FROM films LIMIT 10;"
search_test = queryDb(sqlQuery_test)

df2 = pd.DataFrame(columns=['budget','runtime','trailer view count','trailer like count','trailer dislike count'])

for idx, item in enumerate(search_test):
    df2.loc[idx] = item

# print df2 # For testing purposes

df2['budget'] = df2['budget'].astype(float)
df2['runtime'] = df2['runtime'].astype(float)

sqlQuery_ids2 = "SELECT film_id FROM films;"
search_ids2 = queryDb(sqlQuery_ids2)

genres2 = []

for id in search_ids2:
    sql = "SELECT genres.genre_name FROM films INNER JOIN film_genres ON film_genres.film_id = films.film_id INNER JOIN genres ON film_genres.genre_id = genres.genre_id WHERE films.film_id = %s;"
    results = queryDb_onehot(sql, str(id[0]))
    tempList = []
    for result in results:
        tempList.append(str(result[0]))
    genres2.append(tempList)

genredf2 = pd.Series(genres2)

genredf_onehot2 = pd.get_dummies(genredf2.apply(pd.Series).stack(), prefix='genre').sum(level=0)

df2 = df2.join(genredf_onehot2)

# Impute NULL values and set to -1
df2 = df2.fillna(-1)

# Separating out the features
x2 = df2.loc[:].values
# Standardizing the features
x2 = StandardScaler().fit_transform(x2)

# Apply dimensionality reduction to reduce from multiple columns down to 2
pca2 = PCA(n_components=2)
principalComponents2 = pca2.fit_transform(x2)

principalDf2 = pd.DataFrame(data = principalComponents2, columns = ['principal component 1', 'principal component 2'])

prediction_results = regressor.predict(principalDf2.values)

for idx, value in enumerate(prediction_results):
    sql = "UPDATE films SET film_prediction_rating = %s WHERE film_id = %s"
    insertData(sql, (int(math.ceil(value * 10)), search_ids2[idx]))