from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField
from wtforms.validators import DataRequired, AnyOf, URL, Length, Regexp, Optional
from enums import Genre, State


class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default=datetime.today()
    )


class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired(message="Name is Required.")]
    )
    city = StringField(
        'city', validators=[DataRequired(message="City is Required.")]
    )
    state = SelectField(
        'state', validators=[DataRequired(message="State is Required.")],
        choices=[(s.value, s.name) for s in State]
    )
    address = StringField(
        'address', validators=[DataRequired(message="Address is Required.")]
    )
    phone = StringField(
        'phone', validators=[Regexp('^[0-9]{3}-[0-9]{3}-[0-9]{4}$', message="Follow the pattern shown in placeholder")]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=[(g.value, g.name) for g in Genre]
    )
    image_link = StringField(
        'image_link', validators=[URL(message="Link provided is not valid."), Optional()]
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL(message="Link provided is not valid."), Optional()]
    )


class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired(message="Name is Required.")]
    )
    city = StringField(
        'city', validators=[DataRequired(message="City is Required.")]
    )
    state = SelectField(
        'state', validators=[DataRequired(message="State is Required.")],
        choices=[(s.value, s.name) for s in State]
    )
    phone = StringField(
        'phone', validators=[Regexp('^[0-9]{3}-[0-9]{3}-[0-9]{4}$', message="Follow the pattern shown in placeholder")]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=[(g.value, g.name) for g in Genre]
    )
    image_link = StringField(
        'image_link', validators=[URL(message="Link provided is not valid."), Optional()]
    )

    facebook_link = StringField(
        'facebook_link', validators=[URL(message="Link provided is not valid."), Optional()]
    )
