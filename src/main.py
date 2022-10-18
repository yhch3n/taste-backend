from flask import Flask, jsonify, request, abort
from db.database import db_session, init_db
from db.models import User
from schemas import UserSchema, UserResponseSchema
from http import HTTPStatus


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

if __name__ == '__main__':
    app.run(debug=True)
