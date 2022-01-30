from email import message
from flask import Blueprint, request, jsonify, session
from app.models import User
from app.db import get_db
from sqlalchemy.exc import IntegrityError
import sys

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/users", methods=["POST"])
def signup():
    data = request.get_json()
    db = get_db()

    try:
        # create new user
        new_user = User(username=data["username"], email=data["email"], password=data["password"])

        # save to DB
        db.add(new_user)
        db.commit()
    except AssertionError:
        db.rollback()
        return jsonify(message="Signup failed due to a validation error"), 400
    except IntegrityError:
        db.rollback()
        return jsonify(message="Signup failed due to an internal server error"), 500
    except:
        print(sys.exc_info()[0])
        db.rollback()
        return jsonify(message="Signup failed due to an internal server error"), 500

    session.clear()
    session["user_id"] = new_user.id
    session["loggedIn"] = True
    return jsonify(id=new_user.id)


@bp.route("/users/logout", methods=["POST"])
def logout():
    # remove session variables
    session.clear()
    return "", 204


@bp.route("/users/login", methods=["POST"])
def login():
    data = request.get_json()
    db = get_db()

    try:
        user = db.query(User).filter(User.email == data["email"]).one()
    except:
        print(sys.exc_info()[0])
        return jsonify(message="Incorrect credentials"), 400

    if user.verify_password(data["password"]) == False:
        return jsonify(message="Incorrect credentials"), 400

    session.clear()
    session["user_id"] = user.id
    session["loggedIn"] = True

    return jsonify(id=user.id)
