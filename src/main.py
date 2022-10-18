from flask import Flask, jsonify, request, abort
from db.database import db_session, init_db
from db.models import User, Rating
from schemas import UserSchema, UserResponseSchema, RatingSchema, RatingResponseSchema, RatingPrefSchema, RatingPrefResponseSchema
from http import HTTPStatus
import sqlalchemy
import json, random


init_db()
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route("/")
def show_all():
    return jsonify(UserResponseSchema(many=True).dump(User.query.all()))

@app.route('/users', methods = ['GET', 'POST'])
def users():
    if request.method == 'POST':
        try:
            user_req = UserSchema().load(request.get_json())
            try:
                if user_req['username'] is None or user_req['username'] == '' or \
                   user_req['password'] is None or user_req['password'] == '':
                   return jsonify(HTTPStatus.BAD_REQUEST.phrase), HTTPStatus.BAD_REQUEST
            except KeyError:
                return jsonify(HTTPStatus.UNPROCESSABLE_ENTITY.phrase), HTTPStatus.UNPROCESSABLE_ENTITY

            user = User(user_req['username'], user_req['password'])

            if 'country' in user_req and user_req['country'] is not None or user_req['country'] != '':
                user.country = user_req['country']
            if 'tastePref' in user_req and user_req['tastePref'] is not None or user_req['tastePref'] != '':
                if 'salty' in user_req['tastePref']: user.taste_salty = user_req['tastePref']['salty']
                if 'spicy' in user_req['tastePref']: user.taste_spicy = user_req['tastePref']['spicy']
                if 'sour' in user_req['tastePref']: user.taste_sour = user_req['tastePref']['sour']
                if 'sweet' in user_req['tastePref']: user.taste_sweet = user_req['tastePref']['sweet']

            db_session.add(user)
            db_session.commit()
            return jsonify(UserResponseSchema().dump(user)), HTTPStatus.CREATED
        except Exception as e:
            abort(400, e)
    return jsonify(UserResponseSchema(many=True).dump(User.query.all())), HTTPStatus.OK

@app.route('/ratings', methods = ['GET', 'POST'])
def ratings():
    if request.method == 'POST':
        try:
            rating_req = RatingSchema().load(request.get_json())
            try:
                if rating_req['userId'] is None or rating_req['userId'] == '' or \
                   rating_req['googlePlaceId'] is None or rating_req['googlePlaceId'] == '' or \
                   rating_req['rating'] is None or rating_req['rating'] == '':
                   return jsonify(HTTPStatus.BAD_REQUEST.phrase), HTTPStatus.BAD_REQUEST
            except KeyError:
                return jsonify(HTTPStatus.UNPROCESSABLE_ENTITY.phrase), HTTPStatus.UNPROCESSABLE_ENTITY

            rating = Rating(int(rating_req['userId']), rating_req['googlePlaceId'], float(rating_req['rating']))
            db_session.add(rating)
            db_session.commit()
            return jsonify(RatingResponseSchema().dump(rating)), HTTPStatus.CREATED
        except Exception as e:
            abort(400, e)
    return jsonify(RatingResponseSchema(many=True).dump(Rating.query.all())), HTTPStatus.OK

@app.route('/ratings/pref', methods = ['POST'])
def ratings_pref():
    try:
        req = RatingPrefSchema().load(request.get_json())
        try:
            if req['googlePlaceIds'] is None or req['googlePlaceIds'] == '':
                return jsonify(HTTPStatus.BAD_REQUEST.phrase), HTTPStatus.BAD_REQUEST
        except KeyError:
            return jsonify(HTTPStatus.UNPROCESSABLE_ENTITY.phrase), HTTPStatus.UNPROCESSABLE_ENTITY

        google_place_ids = req['googlePlaceIds']
        filter_taste_pref = ''
        filter_country = ''
        if 'tastePref' in req and req['tastePref'] is not None and req['tastePref'] != '':
            filter_taste_pref = f"( users.taste_salty >= {req['tastePref']['salty']} \
                AND users.taste_spicy >= {req['tastePref']['spicy']} \
                AND users.taste_sour >= {req['tastePref']['sour']} \
                AND users.taste_sweet >= {req['tastePref']['sweet']} ) "

        if 'country' in req and req['country'] is not None and req['country'] != '':
            filter_country = f"( users.country = '{req['country']}' )"

        filter = ''
        if filter_taste_pref != '' and filter_country != '':
            filter = 'AND (' + filter_taste_pref + 'OR' + filter_country + ')'
        elif filter_taste_pref != '':
            filter = 'AND ' + filter_taste_pref
        elif filter_country != '':
            filter = 'AND ' + filter_country

        raw_sql = 'SELECT ratings.google_place_id, AVG(ratings.rating) AS rating, MAX(users.country) AS country,\
            ROUND(SUM(users.taste_salty), 0) AS salty, ROUND(SUM(users.taste_spicy), 0) AS spicy,\
            ROUND(SUM(users.taste_sour), 0) AS sour, ROUND(SUM(users.taste_sweet), 0) AS sweet \
            FROM ratings LEFT JOIN users ON ratings.user_id = users.id\
            WHERE ratings.google_place_id IN :values ' + filter + \
            'GROUP BY ratings.google_place_id'

        query = sqlalchemy.text(raw_sql).bindparams(values=tuple(google_place_ids))
        result = db_session.execute(query).mappings().all()
        if not result:
            result = dummy_ratings(req)
            return json.dumps(result, indent=2), HTTPStatus.OK

        return jsonify(RatingPrefResponseSchema(many=True).dump(result)), HTTPStatus.OK
    except Exception as e:
        abort(400, e)

def dummy_ratings(req):
  result = []
  google_place_ids = req['googlePlaceIds']
  for google_place_id in google_place_ids:
    d = {
        "googlePlaceId": google_place_id,
        "rating": str(random.randrange(1.0, 5.0)),
        "country": req['country'],
        "tastePref": {
            "salty": req['tastePref']['salty'],
            "spicy": req['tastePref']['spicy'],
            "sour": req['tastePref']['sour'],
            "sweet": req['tastePref']['sweet']
        }
    }
    result.append(d)

  return result

if __name__ == '__main__':
    app.run(debug=True)
