from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor
from sklearn.decomposition import PCA
import pandas as pd
import numpy as np
import pymysql

file = "E:\\training_data.csv"

# load dataset into Pandas DataFrame
df = pd.read_csv(file, names=['budget','runtime','trailer view count','trailer like count','trailer dislike count', 'user rating'])

print df # For testing

def queryDb_onehot(sqlQuery, params):
    db = pymysql.connect(host='kanesmall.co.uk', user='kanesmal', password='wj5Gy%EE44#iK@j1', db='kanesmal_training_data', charset='utf8')

    cursor = db.cursor()
    cursor.execute(sqlQuery, params)
    cursor = cursor.fetchall()

    db.commit() # Save changes
    db.close() # Disconnect from the server

    return cursor

ids = [5,6,8,11,12,13,14,15,16,17,18]

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

df = df.join(genredf_onehot)

print df

# features = ['budget','runtime','trailer view count','trailer like count','trailer dislike count', 'user rating']
# Separating out the features
x = df.drop('user rating', axis=1)
# Separating out the target
y = df.loc[:,['user rating']].values
# Standardizing the features
x = StandardScaler().fit_transform(x)

# Apply dimensionality reduction to reduce from 5 columns down to 2
pca = PCA(n_components=2)
principalComponents = pca.fit_transform(x)
principalDf = pd.DataFrame(data = principalComponents, columns = ['principal component 1', 'principal component 2'])

#print principalDf.values # For testing

# Concatenate the target values back onto the final dataframe
finalDf = pd.concat([principalDf, df[['user rating']]], axis = 1)

# print finalDf # For testing

regressor = DecisionTreeRegressor(max_depth=2)
regressor.fit(np.array([finalDf['principal component 1'].T, finalDf['principal component 2']]).T, finalDf['user rating'])

print regressor.predict([[-0.923461, -1.114969]])

# Accuracy / precision / recall --> Google these