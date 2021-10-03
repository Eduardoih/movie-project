from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies_database.db'
db = SQLAlchemy(app)


class Form(FlaskForm):
    rating = StringField('Your Rating Out of 10 e.g. 7.5', validators=[DataRequired()])
    review = StringField('Your Review', validators=[DataRequired()])
    send = SubmitField('Done')


class FormAdd(FlaskForm):
    new_movie = StringField('Movie Title', validators=[DataRequired()])
    send = SubmitField('Add Movie')


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(280), unique=True)
    year = db.Column(db.Integer)
    description = db.Column(db.String(280))
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer, unique=True)
    review = db.Column(db.String(300))
    img_url = db.Column(db.String(300))


# db.create_all()
# db.session.commit()

# new_movie = Movie(
#     title="Alien",
#     year=1979,
#     description="After a space merchant vessel receives an unknown"
#                 "transmission as a distress call, one of the crew is attacked by"
#                 "a mysterious life form and they soon realize that its life cycle"
#                 "has merely begun.",
#     rating=8.3,
#     ranking=9,
#     review="Best horror movie ever.",
#     img_url="https://br.web.img3.acsta.net/c_310_420/pictures/15/05/14/21/14/504650.jpg"
# )
#
# db.session.add(new_movie)
# db.session.commit()


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=['POST', 'GET'])
def edit():
    form = Form()
    if form.validate_on_submit():
        movie_id = request.args.get('id')
        movie_selected = Movie.query.filter_by(id=movie_id).first()
        movie_selected.rating = form.rating.data
        movie_selected.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form=form)


@app.route("/delete")
def delete():
    movie_id = request.args.get('id')
    movie_selected = Movie.query.filter_by(id=movie_id).first()
    db.session.delete(movie_selected)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=['POST', 'GET'])
def add():
    form_add = FormAdd()
    if form_add.validate_on_submit():
        search_movie = form_add.new_movie.data
        print(search_movie)
        url = "https://api.themoviedb.org/3/search/movie"
        parameters = {'api_key': 'ba84aa04cbcf55237db9943a9597afd2',
                      'Language': 'en-US',
                      'query': search_movie}
        response = requests.get(url, params=parameters).json()['results']
        return render_template('select.html', results=response)
    return render_template('add.html', form=form_add)


@app.route("/select")
def select():
    return render_template('select.html')


@app.route("/add_movie")
def add_movie():
    movie_id = request.args.get('id')
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    parameters = {'api_key': 'ba84aa04cbcf55237db9943a9597afd2'}
    response = requests.get(url, params=parameters).json()
    title_movie = response['title']
    poster_url = f"https://image.tmdb.org/t/p/original/{response['poster_path']}"
    release_year = response['release_date'].split('-')[0]
    description = response['overview']
    new_entry = Movie(title=title_movie,
                      img_url=poster_url,
                      year=release_year,
                      description=description)
    db.session.add(new_entry)
    db.session.flush()
    db.session.commit()
    id_entry = new_entry.id
    print(id_entry)
    return redirect(url_for('edit', id=id_entry))


if __name__ == '__main__':
    app.run(debug=True)
