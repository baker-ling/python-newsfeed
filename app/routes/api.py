import sys
from flask import Blueprint, request, jsonify, session
from app.models import User, Post, Comment, Vote
from app.db import get_db
from sqlalchemy.exc import IntegrityError

from app.utils.auth import login_required

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


@bp.route("/comments", methods=["POST"])
@login_required
def comment():
    data = request.get_json()
    db = get_db()
    try:
        # create a new comment
        new_comment = Comment(
            comment_text=data["comment_text"], post_id=data["post_id"], user_id=session.get("user_id")
        )
        db.add(new_comment)
        db.commit()
    except:
        print(sys.exc_info()[0])
        db.rollback()
        return jsonify(message="Comment failed"), 500

    return jsonify(id=new_comment.id)


@bp.route("/posts/upvote", methods=["PUT"])
@login_required
def upvote():
    data = request.get_json()
    db = get_db()
    try:
        # createa new vote with incoming id and session id
        new_vote = Vote(post_id=data["post_id"], user_id=session.get("user_id"))
        db.add(new_vote)
        db.commit()
    except:
        print(sys.exc_info[0])
        db.rollback()
        return jsonify(message="Upvote failed"), 500
    return "", 204


@bp.route("/posts", methods=["POST"])
@login_required
def create():
    data = request.get_json()
    db = get_db()
    try:
        # create a post
        new_post = Post(title=data["title"], post_url=data["post_url"], user_id=session.get("user_id"))
        db.add(new_post)
        db.commit()
    except:
        print(sys.exc_info[0])
        db.rollback()
        return jsonify(message="Post failed"), 500
    return jsonify(id=new_post.id)


@bp.route("/posts/<id>", methods=["PUT"])
@login_required
def update(id):
    data = request.get_json()
    db = get_db()
    try:
        # retrieve post and update title property
        post = db.query(Post).filter(Post.id == id).one()
        post.title = data["title"]
        db.commit()
    except:
        print(sys.exc_info()[0])
        db.rollback()
        return jsonify(message="Post not found"), 404

    return "", 204


@bp.route("posts/<id>", methods=["DELETE"])
@login_required
def delete(id):
    db = get_db()
    try:
        # delete post from db
        db.delete(db.query(Post).filter(Post.id == id).one())
        db.commit()
    except:
        print(sys.exc_info()[0])
        db.rollback()
        return jsonify(message="Post not found"), 404
    return "", 204
