from datetime import datetime


def VenueViewData(venue_data, shows_data):

    past_shows = [show._asdict() for show in shows_data if datetime.strptime(
        show.start_time, '%Y-%m-%dT%H:%M:%SZ') < datetime.now()]

    upcoming_shows = [show._asdict()
                      for show in shows_data if datetime.strptime(
        show.start_time, '%Y-%m-%dT%H:%M:%SZ') > datetime.now()]

    venue_view_data = {
        "id": venue_data.id,
        "name": venue_data.name,
        "genres": venue_data.genres,
        "address": venue_data.address,
        "city": venue_data.city,
        "state": venue_data.state,
        "phone": venue_data.phone,
        "seeking_talent": venue_data.seeking_talent,
        "image_link": venue_data.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    if venue_data.website:
        venue_view_data["website"] = venue_data.website
    if venue_data.facebook_link:
        venue_view_data["facebook_link"] = venue_data.facebook_link
    if venue_data.seeking_talent:
        venue_view_data["seeking_description"] = venue_data.seeking_description

    return(venue_view_data)


def ArtistViewData(artist_data, shows_data):

    past_shows = [show._asdict() for show in shows_data if datetime.strptime(
        show.start_time, '%Y-%m-%dT%H:%M:%SZ') < datetime.now()]

    upcoming_shows = [show._asdict()
                      for show in shows_data if datetime.strptime(
        show.start_time, '%Y-%m-%dT%H:%M:%SZ') > datetime.now()]

    artist_view_data = {
        "id": artist_data.id,
        "name": artist_data.name,
        "genres": artist_data.genres,
        "city": artist_data.city,
        "state": artist_data.state,
        "phone": artist_data.phone,
        "seeking_venue": artist_data.seeking_venue,
        "image_link": artist_data.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    if artist_data.website:
        artist_view_data["website"] = artist_data.website
    if artist_data.facebook_link:
        artist_view_data["facebook_link"] = artist_data.facebook_link
    if artist_data.seeking_venue:
        artist_view_data["seeking_description"] = artist_data.seeking_description

    return(artist_view_data)
