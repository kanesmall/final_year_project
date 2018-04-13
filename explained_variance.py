from sklearn.metrics import explained_variance_score
import pymysql

def queryDb(sqlQuery):
    db = pymysql.connect(host='localhost', user='root', password='6p8RK#LLy0&7hLo#', db='training_data', charset='utf8')

    cursor = db.cursor()
    cursor.execute(sqlQuery)
    cursor = cursor.fetchall()

    db.commit() # Save changes
    db.close() # Disconnect from the server

    return cursor

sql = "SELECT film_vote_average FROM films WHERE film_status = 'Released' and film_trailer_view_count IS NOT NULL and film_budget > 0;"
user_ratings_results = queryDb(sql)

user_ratings = []

for rating in user_ratings_results:
    user_ratings.append(rating[0] * 10)

sql = "SELECT film_prediction_rating FROM films WHERE film_status = 'Released' and film_trailer_view_count IS NOT NULL and film_budget > 0;"
predicted_ratings_results = queryDb(sql)

predicted_ratings = []

for rating in predicted_ratings_results:
    predicted_ratings.append(rating[0])

print explained_variance_score(user_ratings, predicted_ratings)