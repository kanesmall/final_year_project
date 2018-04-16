from sklearn.metrics import explained_variance_score
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import median_absolute_error
import pymysql

def queryDb(sqlQuery):
    db = pymysql.connect(host='localhost', user='root', password='6p8RK#LLy0&7hLo#', db='training_data', charset='utf8')

    cursor = db.cursor()
    cursor.execute(sqlQuery)
    cursor = cursor.fetchall()

    db.commit() # Save changes
    db.close() # Disconnect from the server

    return cursor

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

print "Explained variance: " + str(explained_variance_score(user_ratings, predicted_ratings))
print "Mean Absolute Error: " + str(mean_absolute_error(user_ratings, predicted_ratings))
print "Mean Squared Error: " + str(mean_squared_error(user_ratings, predicted_ratings))
print "Median Absolute Error: " + str(median_absolute_error(user_ratings, predicted_ratings))