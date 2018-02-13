import csv
import progressbar
import pymysql
import requests
import sys
import time
import traceback
import pprint

# Initialise the progressbar
bar = progressbar.ProgressBar()

def getLatestFilmID():
    url = "https://api.themoviedb.org/3/movie/latest?api_key=634014fb344524ac652cddca6c0b6442&language=en-GB"
    response = requests.get(url)
    data = response.json()

    latest_film_id = data['id']

    return latest_film_id

def insertData(sqlQuery, params):
    # Open a database connection
    # MacBook db
    # db = pymysql.connect(host='localhost', user='root', password='maclogin', db='training_data', charset='utf8')

    # Debian VM db
    # db = pymysql.connect(host='192.168.0.27', user='root', password='linuxlogin', db='training_data', charset='utf8')

    # Raspberry Pi db
    # db = pymysql.connect(host='192.168.0.30', user='root', password='linuxlogin', db='training_data', charset='utf8')

    # Web Hosting db
    db = pymysql.connect(host='kanesmall.co.uk', user='kanesmal', password='wj5Gy%EE44#iK@j1', db='kanesmal_training_data', charset='utf8')

    # Prepare a cursor object using the cursor() method
    cursor = db.cursor()

    # Execute an SQL query using the execute() method.
    results = cursor.execute(sqlQuery, params)

    # Save changes
    db.commit()

    # Disconnect from the server
    db.close()

    return results

def selectData(sqlQuery):
    # Open a database connection
    # MacBook db
    # db = pymysql.connect(host='localhost', user='root', password='maclogin', db='training_data', charset='utf8')

    # Debian VM db
    # db = pymysql.connect(host='192.168.0.27', user='root', password='linuxlogin', db='training_data', charset='utf8')

    # Raspberry Pi db
    # db = pymysql.connect(host='192.168.0.30', user='root', password='linuxlogin', db='training_data', charset='utf8')

    # Web Hosting db
    db = pymysql.connect(host='kanesmall.co.uk', user='kanesmal', password='wj5Gy%EE44#iK@j1', db='kanesmal_training_data', charset='utf8')

    # Prepare a cursor object using the cursor() method
    cursor = db.cursor()

    # Execute an SQL query using the execute() method.
    cursor.execute(sqlQuery)

    results = [item[0] for item in cursor.fetchall()]

    # Save changes
    db.commit()

    # Disconnect from the server
    db.close()

    return results

def insertGenres():
    url = "https://api.themoviedb.org/3/genre/movie/list?api_key=634014fb344524ac652cddca6c0b6442&language=en-GB"
    response = requests.get(url)
    data = response.json()

    # For testing that the JSON/headers have been received from the API request
    # pprint(data)

    for i in data['genres']:
        sql = "INSERT INTO genres (genre_id, genre_name) VALUES (%s, %s)"
        insertData(sql, (i['id'], i['name']))

def getTrailerViewCount(id):
    url = "https://api.themoviedb.org/3/movie/" + str(id) + "/videos?api_key=634014fb344524ac652cddca6c0b6442&language=en-GB"
    response = requests.get(url)
    data = response.json()

    if(response.status_code == 200):
        if(data['results']):
            vidKey = data['results'][0]['key']

            if(vidKey != None):
                YouTubeURL = "https://www.googleapis.com/youtube/v3/videos?part=statistics&id=" + vidKey + "&key=AIzaSyDXpN4wLEHRewdoAeoigdoBO3l-NkerRMU"
                YouTubeResponse = requests.get(YouTubeURL, verify=False)
                vidData = YouTubeResponse.json()

                if('items' in vidData):
                    if(vidData['items']):
                        vidURL = "https://www.youtube.com/watch?v=" + vidKey

                        if('viewCount' in vidData['items'][0]['statistics']):
                            viewCount = vidData['items'][0]['statistics']['viewCount']
                        else:
                            viewCount = None

                        if('likeCount' and 'dislikeCount' in vidData['items'][0]['statistics']):
                            likeCount = vidData['items'][0]['statistics']['likeCount']
                            dislikeCount = vidData['items'][0]['statistics']['dislikeCount']
                        else:
                            likeCount = None
                            dislikeCount = None

                    else:
                        vidURL = None
                        viewCount = None
                        likeCount = None
                        dislikeCount = None
                else:
                    vidURL = None
                    viewCount = None
                    likeCount = None
                    dislikeCount = None
            else:
                vidURL = None
                viewCount = None
                likeCount = None
                dislikeCount = None

        else:
            vidURL = None
            viewCount = None
            likeCount = None
            dislikeCount = None

    return vidURL, viewCount, likeCount, dislikeCount

def matchGenres(film_id, genre_ids, genre_names):
    for i, genre_id in enumerate(genre_ids):
        sql = "SELECT genre_id FROM genres WHERE genre_id = %s"
        results = insertData(sql, genre_id)

        if(results == 0):
            sql = "INSERT INTO genres (genre_id, genre_name) VALUES (%s, %s)"
            insertData(sql, (genre_id, genre_names[i]))

            sql = "INSERT INTO film_genres (film_id, genre_id) VALUES (%s, %s)"
            insertData(sql, (film_id, genre_id))
        else:
            sql = "INSERT INTO film_genres (film_id, genre_id) VALUES (%s, %s)"
            insertData(sql, (film_id, genre_id))

def matchProdComps(film_id, data):
    # Loop through JSON data and store production_company_id and production_company_name
    # Check if production_company_id, production_company_name are present in the production_companies table
    for prod_comp in data['production_companies']:
        prod_comp_id = prod_comp['id']
        prod_comp_name = prod_comp['name']

        sql = "SELECT production_company_id FROM production_companies WHERE production_company_id = %s"
        results = insertData(sql, prod_comp_id)

        if(results == 0):
            sql = "INSERT INTO production_companies (production_company_id, production_company_name) VALUES (%s, %s)"
            insertData(sql, (prod_comp_id, prod_comp_name))

            sql = "INSERT INTO film_production_companies (film_id, production_company_id) VALUES (%s, %s)"
            insertData(sql, (film_id, prod_comp_id))
        else:
            sql = "INSERT INTO film_production_companies (film_id, production_company_id) VALUES (%s, %s)"
            insertData(sql, (film_id, prod_comp_id))

def matchActors(film_id):
    url = "https://api.themoviedb.org/3/movie/" + str(film_id) + "/credits?api_key=634014fb344524ac652cddca6c0b6442"
    response = requests.get(url)
    data = response.json()

    # Loop through JSON data and store actor_id, actor_name and actor_character
    # Check if actor_id, actor_name are present in the actors table
    # Take only the top 10 actors listed
    for actor in data['cast'][:10]:
        actor_id = actor['id']
        actor_name = actor['name']
        actor_character = actor['character']

        imgURLDomain = "https://image.tmdb.org/t/p/w640"
        # Check that the JSON object is not null to prevent a str + nonetype error
        if(actor['profile_path']):
            actor_pic_url = imgURLDomain + actor['profile_path']
        else:
            actor_pic_url = None

        sql = "SELECT actor_id FROM actors WHERE actor_id = %s"
        results = insertData(sql, actor_id)

        if(results == 0):
            sql = "INSERT INTO actors (actor_id, actor_name, actor_pic_url) VALUES (%s, %s, %s)"
            insertData(sql, (actor_id, actor_name, actor_pic_url))

            sql = "INSERT INTO film_actors (film_id, actor_id, actor_character) VALUES (%s, %s, %s)"
            insertData(sql, (film_id, actor_id, actor_character))
        else:
            sql = "INSERT INTO film_actors (film_id, actor_id, actor_character) VALUES (%s, %s, %s)"
            insertData(sql, (film_id, actor_id, actor_character))

def matchDirectors(film_id):
    url = "https://api.themoviedb.org/3/movie/" + str(film_id) + "/credits?api_key=634014fb344524ac652cddca6c0b6442"
    response = requests.get(url)
    data = response.json()

    # Loop through JSON data and store director_id, director_name
    # Check if director_id, director_name are present in the directors table
    # Take only the top 10 directors listed
    for director in data['crew']:
        if(director['job'] == "Director"):
            director_id = director['id']
            director_name = director['name']

            imgURLDomain = "https://image.tmdb.org/t/p/w640"
            # Check that the JSON object is not null to prevent a str + nonetype error
            if(director['profile_path']):
                director_pic_url = imgURLDomain + director['profile_path']
            else:
                director_pic_url = None

            sql = "SELECT director_id FROM directors WHERE director_id = %s"
            results = insertData(sql, director_id)

            if(results == 0):
                sql = "INSERT INTO directors (director_id, director_name, director_pic_url) VALUES (%s, %s, %s)"
                insertData(sql, (director_id, director_name, director_pic_url))

                sql = "INSERT INTO film_directors (film_id, director_id) VALUES (%s, %s)"
                insertData(sql, (film_id, director_id))
            else:
                sql = "INSERT INTO film_directors (film_id, director_id) VALUES (%s, %s)"
                insertData(sql, (film_id, director_id))

def checkIfPresent(data):
    if(data):
        return data
    else:
        return None

def insertFilms():
    # Store the latest film id in a variable
    latest_film_id = getLatestFilmID()

    # Specify the progressbar range
    bar(range(46166, latest_film_id+1))

    # Open CSV file for writing
    errors_csv = open('execution_errors.csv', 'wb')
    wrtr = csv.writer(errors_csv, delimiter=',')

    i = 1
    while i <= latest_film_id:
        try:
            url = "https://api.themoviedb.org/3/movie/" + str(i) + "?api_key=634014fb344524ac652cddca6c0b6442&language=en-GB"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
            response = requests.get(url, headers=headers)
            data = response.json()

            # For testing that the JSON/headers have been received from the API request
            # pprint(data)
            # print response.status_code
            # print response.headers['X-RateLimit-Remaining'] + "\n"

            if(response.headers['X-RateLimit-Remaining'] != 0 and response.status_code == 200 and data['adult'] == False and data['original_language'] == "en"):
                film_id = data['id']
                film_title = data['title']
                film_tagline = checkIfPresent(data['tagline'])
                film_overview = checkIfPresent(data['overview'])

                imgURLDomain = "https://image.tmdb.org/t/p/w640"
                # Check that the JSON object is not null to prevent a str + nonetype error
                if(data['poster_path']):
                    film_poster_url = imgURLDomain + data['poster_path']
                else:
                    film_poster_url = None

                film_release_date = checkIfPresent(data['release_date'])
                film_budget = data['budget']
                film_revenue = data['revenue']
                film_runtime = checkIfPresent(data['runtime'])
                film_status = checkIfPresent(data['status'])
                film_vote_average = data['vote_average']
                film_vote_count = data['vote_count']

                film_trailer_url, film_trailer_view_count, film_trailer_like_count, film_trailer_dislike_count = getTrailerViewCount(i)

                # Insert into films table
                sql = "INSERT INTO films (film_id, film_title, film_tagline, film_overview, film_poster_url, film_release_date, film_budget, film_revenue, film_runtime, film_status, film_vote_average, film_vote_count, film_trailer_url, film_trailer_view_count, film_trailer_like_count, film_trailer_dislike_count) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                insertData(sql,(film_id, film_title, film_tagline, film_overview, film_poster_url, film_release_date, film_budget, film_revenue, film_runtime, film_status, film_vote_average, film_vote_count, film_trailer_url, film_trailer_view_count, film_trailer_like_count, film_trailer_dislike_count))

                genre_ids = []
                genre_names = []
                for genre in data['genres']:
                    genre_ids.append(genre['id'])
                    genre_names.append(genre['name'])
                matchGenres(film_id, genre_ids, genre_names)

                matchProdComps(film_id, data)

                matchActors(film_id)

                matchDirectors(film_id)

            elif(response.status_code == 429):
                time.sleep(response.headers['Retry-After']) # Sleep for regmaining time in order to reset API request rate limit
                # print "Reached sleep case"

                # Decrement the iterator to loop through the id that has been skipped
                i -= 1

            # Increment the iterator
            i += 1

            # Update the progress bar iteration
            bar.update(i)

        except Exception:
            # Print to csv, id and message (write to file as the program executes)
            # Flush the write object
            wrtr.writerow([i, traceback.format_exc()])
            errors_csv.flush()
            pass

    errors_csv.close()

def main():
    # Disable the SSL warnings for older Python versions
    requests.packages.urllib3.disable_warnings()

    # insertGenres()

    # insertFilms()

    sql = "SELECT film_id FROM films;"

    listOfFilmIDs = selectData(sql)

    # Open CSV file for writing
    errors_csv = open('execution_errors.csv', 'wb')
    wrtr = csv.writer(errors_csv, delimiter=',')

    # Find the index of the film_id that the code was killed on
    print listOfFilmIDs.index(428252)

    # Slice the list to return all values from the index position of the last film_id recorded +1
    for i in listOfFilmIDs[196963+1:]:
        try:
            matchActors(i)
            matchDirectors(i)
            print i

        except Exception:
            # Print to csv, id and message (write to file as the program executes)
            # Flush the write object
            wrtr.writerow([i, traceback.format_exc()])
            errors_csv.flush()
            pass

    errors_csv.close()

if __name__ == "__main__":
    main()