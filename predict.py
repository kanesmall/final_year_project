from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor
from sklearn.decomposition import PCA
from sklearn.externals import joblib
from sklearn.metrics import explained_variance_score
import pandas as pd
import numpy as np
import pymysql, math

def queryDb(sqlQuery):
    db = pymysql.connect(host='localhost', user='root', password='6p8RK#LLy0&7hLo#', db='training_data', charset='utf8')

    cursor = db.cursor()
    cursor.execute(sqlQuery)
    cursor = cursor.fetchall()

    db.commit() # Save changes
    db.close() # Disconnect from the server

    return cursor

def queryDb_onehot(sqlQuery, params):
    db = pymysql.connect(host='localhost', user='root', password='6p8RK#LLy0&7hLo#', db='training_data', charset='utf8')

    cursor = db.cursor()
    cursor.execute(sqlQuery, params)
    cursor = cursor.fetchall()

    db.commit() # Save changes
    db.close() # Disconnect from the server

    return cursor

def insertData(sqlQuery, params):
    db = pymysql.connect(host='localhost', user='root', password='6p8RK#LLy0&7hLo#', db='training_data', charset='utf8')

    # Prepare a cursor object using the cursor() method
    cursor = db.cursor()

    # Execute an SQL query using the execute() method.
    results = cursor.execute(sqlQuery, params)

    db.commit() # Save changes
    db.close() # Disconnect from the server

    return results

# Training data
# sqlQuery_training = "SELECT film_budget, film_runtime, film_trailer_view_count, film_trailer_like_count, film_trailer_dislike_count, film_vote_average FROM films WHERE film_status = 'Released';"
# search_training = queryDb(sqlQuery_training)
#
# df = pd.DataFrame(columns=['budget','runtime','trailer view count','trailer like count','trailer dislike count', 'user rating'])
#
# for idx, item in enumerate(search_training):
#     df.loc[idx] = item
#     # print df # For testing purposes

file_train = "training_set.csv"
df = pd.read_csv(file_train, names=['budget','runtime','trailer view count','trailer like count','trailer dislike count', 'user rating'], low_memory=False)

sqlQuery_genres = "SELECT genre_id, genre_name FROM genres;"
genresTable = queryDb(sqlQuery_genres)

genresDict = dict((x, str(y)) for x, y in genresTable)

sqlQuery_ids = "SELECT film_id FROM films WHERE film_status = 'Released';"
search_ids = queryDb(sqlQuery_ids)

genres = []

for id in search_ids:
    sql = "SELECT genre_id FROM film_genres WHERE film_id = %s;"
    results = queryDb_onehot(sql, str(id[0]))
    tempList = []
    for result in results:
        tempList.append(genresDict.get(result[0]))

    genres.append(tempList)

print "Training genres acquired."

genredf = pd.Series(genres)

genredf_onehot = pd.get_dummies(genredf.apply(pd.Series).stack(), prefix='genre').sum(level=0)

df = df.join(genredf_onehot)

# Impute NULL values and set to -1
df = df.fillna(-1)

print df.info(memory_usage='deep')

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

print "Regressor has been trained."

# Save model to a file
file = 'finalised_model.sav'
joblib.dump(regressor, file)

# Test data
# sqlQuery_test = "SELECT film_budget, film_runtime, film_trailer_view_count, film_trailer_like_count, film_trailer_dislike_count FROM films;"
# search_test = queryDb(sqlQuery_test)
#
# df2 = pd.DataFrame(columns=['budget','runtime','trailer view count','trailer like count','trailer dislike count'])
#
# for idx, item in enumerate(search_test):
#     df2.loc[idx] = item

file_test = "test_set.csv"
df2 = pd.read_csv(file_test, names=['budget','runtime','trailer view count','trailer like count','trailer dislike count'], low_memory=False)

sqlQuery_ids2 = "SELECT film_id FROM films;"
search_ids2 = queryDb(sqlQuery_ids2)

genres2 = []

for id in search_ids2:
    sql = "SELECT genre_id FROM film_genres WHERE film_id = %s;"
    results = queryDb_onehot(sql, str(id[0]))
    tempList = []
    for result in results:
        tempList.append(genresDict.get(result[0]))

    genres2.append(tempList)

print "Test genres acquired."

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

print "Predicted values added to database."

sql = "SELECT film_vote_average FROM films WHERE film_status = 'Released';"
user_ratings_results = queryDb(sql)

user_ratings = []

for rating in user_ratings_results:
    user_ratings.append(rating[0] * 10)

sql = "SELECT film_prediction_rating FROM films WHERE film_status = 'Released';"
predicted_ratings_results = queryDb(sql)

predicted_ratings = []

for rating in predicted_ratings_results:
    predicted_ratings.append(rating[0])

print explained_variance_score(user_ratings, predicted_ratings)