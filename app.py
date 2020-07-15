#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from datetime import datetime

from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import Form
from sqlalchemy import func

import logging
from logging import Formatter, FileHandler

from forms import *
from utils import VenueViewData, ArtistViewData

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

Show = db.Table('Show',
                db.Column('id', db.Integer, primary_key=True),
                db.Column('venue_id', db.Integer, db.ForeignKey(
                    'Venue.id')),
                db.Column('artist_id', db.Integer, db.ForeignKey(
                    'Artist.id')),
                db.Column('start_time', db.DateTime)
                )


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    _genres = db.Column(db.String(120), default='')
    address = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String, nullable=True)
    image_link = db.Column(db.String(500))
    artists = db.relationship('Artist', secondary=Show,
                              backref=db.backref('venues', lazy=True))

    @property
    def genres(self):
        return [x for x in self._genres.split(',')]

    @genres.setter
    def genres(self, value):
        self._genres = ','.join(value)

    def __repr__(self):
        return f'<Venue Id: {self.id} , Name: {self.name} Genres: {self.genres}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    _genres = db.Column(db.String(120), default='')
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String, nullable=True)
    image_link = db.Column(db.String(500))

    @property
    def genres(self):
        return [x for x in self._genres.split(',')]

    @genres.setter
    def genres(self, value):
        self._genres = ','.join(value)

    def __repr__(self):
        return f'<Artist Id: {self.id} , Name: {self.name} Genres: {self.genres}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

    data = list()
    result_venues = Venue.query.with_entities(
        Venue.id, Venue.name, Venue.city, Venue.state).order_by(Venue.id).all()

    if(len(result_venues) > 0):
        result_venus_shows = list()
        distinct_city_state = list()

        for v in result_venues:
            if (v.city, v.state) not in distinct_city_state:
                distinct_city_state.append((v.city, v.state))

            shows_count = db.session.query(Show).filter(
                Show.c.venue_id == v.id, Show.c.start_time > datetime.now()).count()
            result_venus_shows.append({
                **v._asdict(),
                "num_upcoming_shows": shows_count,
            })

        for city, state in distinct_city_state:
            data.append({
                "city": city,
                "state": state,
                "venues": [v for v in result_venus_shows if v["city"] == city and v["state"] == state]
            })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    response = dict()
    search_term = request.form.get('search_term', '')

    if search_term:
        query_venue = Venue.query.filter(Venue.name.ilike(
            f'%{search_term}%')).with_entities(Venue.id, Venue.name)
        result_venues = query_venue.all()

        response["count"] = len(result_venues)
        response["data"] = list()

        if len(result_venues) > 0:

            for v in result_venues:
                shows_count = db.session.query(Show).filter(
                    Show.c.venue_id == v.id, Show.c.start_time > datetime.now()).count()
                response["data"].append({
                    **v._asdict(),
                    "num_upcoming_shows": shows_count
                })

    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue_data = Venue.query.get(venue_id)

    shows_data = db.session.query(Show).join(Artist).filter(Show.c.venue_id == venue_id).with_entities(
        Show.c.artist_id, Artist.name.label('artist_name'), Artist.image_link.label('artist_image_link'), func.to_char(Show.c.start_time, 'YYYY-MM-DD"T"HH24:MI:SS"Z"').label('start_time')).all()

    data = VenueViewData(venue_data, shows_data)
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        venue_form = VenueForm(obj=request.form.to_dict())
 
        if venue_form.validate_on_submit():
            new_venue = Venue()
            new_venue.name = venue_form.name.data
            new_venue.city = venue_form.city.data
            new_venue.state = venue_form.state.data
            new_venue.address = venue_form.address.data
            new_venue.phone = venue_form.phone.data
            new_venue.image_link = venue_form.image_link.data
            new_venue.genres = venue_form.genres.data
            new_venue.facebook_link = venue_form.facebook_link.data

            db.session.add(new_venue)
            db.session.commit()

            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
        else:
            return render_template('forms/new_venue.html', form=venue_form)

    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Venue ' +
              venue_form.name.data + ' could not be listed.')
        return render_template('pages/home.html')
    finally:
        db.session.close()

    return redirect(url_for('venues'))


@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
    venue_data = Venue.query.get(venue_id)
    return render_template('forms/delete_venue.html', venue_id=venue_data.id, venue_name=venue_data.name)


@app.route('/venues/<venue_id>/delete', methods=['POST'])
def delete_venue_submission(venue_id):
    try:
        venue_data = Venue.query.get(venue_id)

        # Assume Typical many to many relationship table with composite primary key consists from the two table forien keys
        # so when deleting it expects only one row
        # venue_data.artists.clear()

        delete_query = Show.delete().where(Show.c.venue_id == venue_id)
        db.session.execute(delete_query)
        db.session.delete(venue_data)

        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        return render_template('errors/500.html')
    finally:
        db.session.close()

    return redirect(url_for('venues'))


#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    data = list()
    query_artists = Artist.query.with_entities(
        Artist.id, Artist.name).order_by(Artist.id).all()
    if(len(query_artists) > 0):
        data = [a._asdict() for a in query_artists]

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    response = dict()
    search_term = request.form.get('search_term', '')
    if search_term:
        query_artist = Venue.query.filter(Artist.name.ilike(
            f'%{search_term}%')).with_entities(Artist.id, Artist.name)
        result_artists = query_artist.all()

        response["count"] = len(result_artists)
        response["data"] = list()

        if len(result_artists) > 0:

            for a in result_artists:
                shows_count = db.session.query(Show).filter(
                    Show.c.artist_id == a.id, Show.c.start_time > datetime.now()).count()
                response["data"].append({
                    **a._asdict(),
                    "num_upcoming_shows": shows_count
                })
    print(response)
    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

    artist_data = Artist.query.get(artist_id)

    shows_data = db.session.query(Show).join(Venue).filter(Show.c.artist_id == artist_id).with_entities(
        Show.c.venue_id, Venue.name.label('venue_name'), Venue.image_link.label('venue_image_link'), func.to_char(Show.c.start_time, 'YYYY-MM-DD"T"HH24:MI:SS"Z"').label('start_time')).all()

    data = ArtistViewData(artist_data, shows_data)
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist_data = Artist.query.get(artist_id)

    # generate form and populate data
    form = ArtistForm(obj=artist_data)

    return render_template('forms/edit_artist.html', form=form, artist_id=artist_data.id, artist_name=artist_data.name)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    try:
        artist_data = Artist.query.get(artist_id)
        artist_form_submitted = ArtistForm(obj=request.form.to_dict())

        if artist_form_submitted.validate_on_submit():
            artist_data.name = artist_form_submitted.name.data
            artist_data.city = artist_form_submitted.city.data
            artist_data.state = artist_form_submitted.state.data
            artist_data.phone = artist_form_submitted.phone.data
            artist_data.image_link = artist_form_submitted.image_link.data
            artist_data.genres = artist_form_submitted.genres.data
            artist_data.facebook_link = artist_form_submitted.facebook_link.data

            db.session.commit()
        else:
            return render_template('forms/edit_artist.html', form=artist_form_submitted, artist_id=artist_data.id, artist_name=artist_data.name)

    except:
        db.session.rollback()
        return render_template('errors/500.html')

    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue_data = Venue.query.get(venue_id)

    # generate form and populate data
    form = VenueForm(obj=venue_data)

    return render_template('forms/edit_venue.html', form=form, venue_id=venue_data.id, venue_name=venue_data.name)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
        venue_data = Venue.query.get(venue_id)
        venue_form_submitted = VenueForm(obj=request.form.to_dict())

        if venue_form_submitted.validate_on_submit():
            venue_data.name = venue_form_submitted.name.data
            venue_data.city = venue_form_submitted.city.data
            venue_data.state = venue_form_submitted.state.data
            venue_data.address = venue_form_submitted.address.data
            venue_data.phone = venue_form_submitted.phone.data
            venue_data.image_link = venue_form_submitted.image_link.data
            venue_data.genres = venue_form_submitted.genres.data
            venue_data.facebook_link = venue_form_submitted.facebook_link.data

            db.session.commit()
        else:
            return render_template('forms/edit_venue.html', form=venue_form_submitted, venue_id=venue_data.id, venue_name=venue_data.name)

    except:
        db.session.rollback()
        return render_template('errors/500.html')

    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    try:
        artist_form = ArtistForm(obj=request.form.to_dict())

        if artist_form.validate_on_submit():
            new_artist = Artist()
            new_artist.name = artist_form.name.data
            new_artist.city = artist_form.city.data
            new_artist.state = artist_form.state.data
            new_artist.phone = artist_form.phone.data
            new_artist.image_link = artist_form.image_link.data
            new_artist.genres = artist_form.genres.data
            new_artist.facebook_link = artist_form.facebook_link.data

            db.session.add(new_artist)
            db.session.commit()

            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
        else:
            return render_template('forms/new_artist.html', form=artist_form)

    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Artist ' +
              artist_form.name.data + ' could not be listed.')
        return render_template('pages/home.html')
    finally:
        db.session.close()

    return redirect(url_for('artists'))


@app.route('/artists/<artist_id>/delete', methods=['GET'])
def delete_artist(artist_id):
    artist_data = Artist.query.get(artist_id)
    return render_template('forms/delete_artist.html', artist_id=artist_data.id, artist_name=artist_data.name)


@app.route('/artists/<artist_id>/delete', methods=['POST'])
def delete_artist_submission(artist_id):
    try:
        artist_data = Artist.query.get(artist_id)
        # Assume Typical many to many relationship table (reflection table) with composite primary key consists from the two table forien keys
        # so when deleting it expects only one row
        # artist_data.venues.clear()

        delete_query = Show.delete().where(Show.c.artist_id == artist_id)
        db.session.execute(delete_query)
        db.session.delete(artist_data)

        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        return render_template('errors/500.html')
    finally:
        db.session.close()

    return redirect(url_for('artists'))

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    data = list()
    query_shows = db.session.query(Show).join(Venue).join(
        Artist).with_entities(Show.c.venue_id.label('venue_id'), Venue.name.label('venue_name'), Show.c.artist_id.label('artist_id'), Artist.name.label('artist_name'), Artist.image_link.label('artist_image_link'), func.to_char(Show.c.start_time, 'YYYY-MM-DD"T"HH24:MI:SS"Z"').label('start_time')).all()

    if(len(query_shows) > 0):
        data = [s._asdict() for s in query_shows]

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        form_data = request.form.to_dict()
        print('form_data: ', form_data)

        insert_show_query = Show.insert().values(
            artist_id=form_data["artist_id"], venue_id=form_data["venue_id"], start_time=form_data["start_time"])

        db.session.execute(insert_show_query)
        db.session.commit()

        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
        return render_template('pages/home.html')
    finally:
        db.session.close()

    return redirect(url_for('shows'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
