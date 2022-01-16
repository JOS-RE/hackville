from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_file
from flask_login import login_required, current_user
from .models import Post, User, Comment, Like
from . import db
import os
from os import getenv
import openai
import json

views = Blueprint("views", __name__)

api_key = getenv('API_KEY')

openai.api_key = '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'


@views.route("/")
def index():
    return render_template("index.html", user=current_user)


@views.route("/home")
@login_required
def home():
    posts = Post.query.all()
    return render_template("home.html", user=current_user, posts=posts)


@views.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')

        if not text:
            flash('Post cannot be empty', category='error')
        else:
            post = Post(text=text, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('views.home'))

    return render_template('create_post.html', user=current_user)


@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist.", category='error')
    elif current_user.id != post.id:
        flash('You do not have permission to delete this post.', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')

    return redirect(url_for('views.home'))


@views.route("/posts/<username>")
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('views.home'))

    posts = user.posts
    return render_template("posts.html", user=current_user, posts=posts, username=username)


@views.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(
                text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')

    return redirect(url_for('views.home'))


@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('views.home'))


@views.route("/like-post/<post_id>", methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(
        author=current_user.id, post_id=post_id).first()

    if not post:
        return jsonify({'error': 'Post does not exist.'}, 400)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return jsonify({"likes": len(post.likes), "liked": current_user.id in map(lambda x: x.author, post.likes)})


# @views.route("/notes", methods=['GET', 'POST'])
# @login_required
# def notes():
#     if request.method == "POST":
#         text = request.form.get('text')

#         if not text:
#             flash('Note cannot be empty', category='error')
#         else:
#             post = Post(text=text, author=current_user.id)
#             db.session.add(post)
#             db.session.commit()
#             flash('Note created!', category='success')
#             return redirect(url_for('views.notes'))

    return render_template('notes.html', user=current_user)


@views.route("/notesbuddy", methods=['GET', 'POST'])
@login_required
def notesbuddy():
    if request.method == "POST":

        data = request.form['name']
        data1 = f'What are some key points I should know when studying about {data} ?'
        response = openai.Completion.create(
            engine="davinci-instruct-beta",
            prompt=data1,
            temperature=1,
            max_tokens=64,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        data = response.choices[0]['text']
        return render_template('notebuddy.html', user=current_user, data=data)
    else:
        return render_template('notebuddy.html', user=current_user)


@views.route("/grammer", methods=['GET', 'POST'])
@login_required
def grammer():
    if request.method == "POST":
        data = request.form['name']
        data1 = f'Original:{data}.\nStandard American English:'
        response = openai.Completion.create(
            engine="davinci",
            prompt=data1,
            temperature=0,
            max_tokens=60,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["\n"]
        )

        data = response.choices[0]['text']
        return render_template('grammer.html', user=current_user, data=data)
    else:
        return render_template('grammer.html', user=current_user)


@views.route("/essay", methods=['GET', 'POST'])
@login_required
def essay():
    if request.method == 'POST':
        data = request.form['name']
        response = openai.Completion.create(
            engine="davinci",
            prompt=f"Create an outline for an essay about {data}:\n\nI: Introduction",
            temperature=0.7,
            max_tokens=539,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        data = response.choices[0]['text']
        return render_template('essay.html', user=current_user, data=data)
    else:
        return render_template('essay.html', user=current_user)


@views.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user, email=current_user.email, name=current_user.username, college=current_user.college)

# routing to tools page is user is authenticated else redirect to login page


@views.route("/tools", methods=['GET', 'POST'])
@login_required
def tools():
        return render_template('tools.html', user=current_user)


@views.route("/interview", methods=['GET', 'POST'])
@login_required
def interview():
    if request.method == 'POST':
        data = request.form['name']
        response = openai.Completion.create(
        engine="davinci-instruct-beta",
        prompt=f"Create a list of questions for my interview with a {data}\n\n1.",
        temperature=0.8,
        max_tokens=64,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["\n\n"]
        )

        data = response.choices[0]['text']
        return render_template('interview.html', user=current_user, data=data)
    else:
        return render_template('interview.html', user=current_user)


@views.route('/summery', methods=['GET', 'POST'])
@login_required
def summery():
    if request.method == 'POST':
        data = request.form['name']

        response = openai.Completion.create(
        engine="davinci",
        prompt=f"My second grader asked me what this passage means:\n\"\"\"\n{data}\n\"\"\"\nI rephrased it for him, in plain language a second grader can understand:\n\"\"\"\n",
        temperature=0.5,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0.2,
        presence_penalty=0,
        stop=["\"\"\""]
        )
        data = response.choices[0]['text']
        return render_template('summery.html', user=current_user, data=data)
    else:
        return render_template('summery.html', user=current_user)

@views.route('/keyword',methods=['GET','POST'])
@login_required
def keyword():
    if request.method == 'POST':
        data = request.form['name']
        response = openai.Completion.create(
        engine="davinci",
        prompt=f"Text: {data}\n\nKeywords:",
        temperature=0.3,
        max_tokens=60,
        top_p=1,
        frequency_penalty=0.8,
        presence_penalty=0,
        stop=["\n"]
        )
        data = response.choices[0]['text']
        return render_template('keyword.html', user=current_user, data=data)
    else:
        return render_template('keyword.html', user=current_user)



