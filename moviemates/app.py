from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import numpy as np
import pandas as pd
from collections import Counter
import math
import yaml

movies_csv =  pd.read_csv("movies.csv")

movie_genres = movies_csv[["genres"]]

movie_g = movies_csv[["title", "genres"]].set_index("title")


#flask stuff ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
#Initialize database
#database stuff ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from flask_mysqldb import MySQL

db = yaml.safe_load(open('config.yaml'))

app.config["MYSQL_HOST"] = db["host"]
app.config["MYSQL_USER"] = db["user"]
app.config["MYSQL_PASSWORD"] = db["password"]
app.config["MYSQL_DB"] = db["db_name"]

mysql = MySQL(app)
#~~~~~~~~~~~~~~~~~~~~~~~~~

#routes
from user import routes

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/users')
def users():
	return render_template('users.html')


from flask import session


@app.route('/clearme')
def clearme():
	session.clear()
	return "session cleared!"

@app.route('/movies', methods = ['POST', 'GET'])
def movies():

	print("hackathon")
	print(session)

	if "movie_likes" not in session:
		session["movie_likes"] = {}

	movie_likes = session["movie_likes"]

	print("movie_likes", movie_likes)


	if request.method == "POST":

		user = request.form['handle']
		movie = request.form['name']

		session["user"] = user

		if movies_csv["title"].isin([movie]).any():
			if user in movie_likes:
				movie_likes[user].append(movie)
			else:
				movie_likes[user] = [movie]

		session["movie_likes"] = movie_likes
		
		return redirect('/movies')
		#new_movie_liked = MovieLikes(name=user_movie)

		#Push to databse
		#try:
		#	db.session.add(new_movie_liked)
		#	db.session.commit()
		#	return redirect('/movies')
		#except:
	#		return "There was an error adding the movie."
		
	else:# GET 

		user_movie_genre_list = []
		other_user_movie_genre_list = []

		user_likes = []
		user = ""
		if "user" in session:
			user = session["user"]
			user_likes = [m for m in movie_likes[user]]


		m_genre_specifics = []
		om_genre_specifics = []

		#masterlist of all other user's compatability scores
		master_list = {}



		user_movies = movie_likes.get(user, [])
		for user_movie in user_movies:
			user_movie_genre_list.append(movie_g.loc[user_movie]["genres"])	
			

		for umg in user_movie_genre_list:
			genres = umg.split("|")
			for genre in genres:
				m_genre_specifics.append(genre)	

		for other_user in movie_likes.keys(): #checks for all users in "database", about to compare them all to our user
			other_user_temp = other_user
			if user != other_user: #checks if current user in session is one of the users in the "database"
				
				other_user_movies = movie_likes.get(other_user)

				for other_user_movie in other_user_movies:
					other_user_movie_genre_list.append(movie_g.loc[other_user_movie]["genres"])


				for umg in other_user_movie_genre_list:
					genres = umg.split("|")
					for genre in genres:  
						om_genre_specifics.append(genre)

				def counter_cosine_similarity(c1, c2):
				    terms = set(c1).union(c2)
				    dotprod = sum(c1.get(k, 0) * c2.get(k, 0) for k in terms)
				    magA = math.sqrt(sum(c1.get(k, 0)**2 for k in terms))
				    magB = math.sqrt(sum(c2.get(k, 0)**2 for k in terms))
				    return dotprod / (magA * magB)

				counter_user = Counter(m_genre_specifics)
				counter_other_user = Counter(om_genre_specifics)

				percent_similarity = round((counter_cosine_similarity(counter_user, counter_other_user) *100))

				master_list[other_user] = percent_similarity

		c = Counter(master_list)

		most_common = c.most_common(3)  # returns top 3 pairs

		similar_keys = [key for key, val in most_common]




		#movie_likes = MovieLikes.query.order_by(MovieLikes.date_created)
		
		return render_template('movies.html', 
			#movies=[movie_titles.iloc[i][0] for i in range(len(movie_titles))], 
			movies=[],
			movie_likes=user_likes, user=user, similar_keys=similar_keys, master_list=master_list)

if __name__ == "__main__":
    # Quick test configuration. Please use proper Flask configuration options
    # in production settings, and use a separate file or environment variables
    # to manage the secret key!
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    app.debug = True
    app.run()
    # hmmm...
