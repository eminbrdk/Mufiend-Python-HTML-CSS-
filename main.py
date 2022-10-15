from flask import Flask, render_template, redirect, url_for, flash, abort, request
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import RegisterForm, LoginForm, SearchMovieForm, CartForm, CommentForm
from sık_kullanıcaklar import TakeMovie
from functools import wraps
import ast
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


# Create DataBase
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# User Table
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=True)
    email = db.Column(db.String(250), nullable=True, unique=True)
    password = db.Column(db.String(250), nullable=True)

    carts = relationship("Cart", back_populates="author")

    followers = relationship("Follower", back_populates="followed")

    likes = relationship("Like", back_populates="liker")

    comments = relationship("Comment", back_populates="commenter")

    room_texts = relationship("RoomText", back_populates="author")


# Follower Table
class Follower(db.Model):
    __tablename__ = "followers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=True)
    follower_id = db.Column(db.Integer, nullable=True)

    followed_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    followed = relationship("User", back_populates="followers")


# Cart Table
class Cart(db.Model):
    __tablename__ = "carts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=True)
    year = db.Column(db.String(20), nullable=False)
    poster_url = db.Column(db.String(100), nullable=True)
    text = db.Column(db.String, nullable=True)

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="carts")

    likes = relationship("Like", back_populates="cart")

    comments = relationship("Comment", back_populates="cart")


# Like Table
class Like(db.Model):
    __tablename__ = "likes"
    id = db.Column(db.Integer, primary_key=True)

    cart_idd = db.Column(db.Integer, nullable=True)

    cart_id = db.Column(db.Integer, db.ForeignKey("carts.id"))
    cart = relationship("Cart", back_populates="likes")

    liker_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    liker = relationship("User", back_populates="likes")


# Comment Table
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=True)

    cart_id = db.Column(db.Integer, db.ForeignKey("carts.id"))
    cart = relationship("Cart", back_populates="comments")

    commenter_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    commenter = relationship("User", back_populates="comments")


# Room text Table
class RoomText(db.Model):
    __tablename__ = "rooms"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=True)
    movie_name = db.Column(db.String(150), nullable=True)
    movie_year = db.Column(db.Integer, nullable=True)

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="room_texts")


db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def get_register():
    form = RegisterForm()

    if form.validate_on_submit():
        if User.query.filter_by(name=form.username.data).first():
            flash("bu isim başka birisi tarafından kullanılıyor")
            return redirect(url_for("get_register"))
        elif User.query.filter_by(email=form.email.data).first():
            flash("bu email ile çoktan hesap açılmış. giriş yapmayı deneyin")
            return redirect(url_for("get_register"))
        else:
            hash_and_salted_password = generate_password_hash(
                password=form.password.data,
                method="pbkdf2:sha256",
                salt_length=8
            )
            new_user = User(
                name=form.username.data,
                email=form.email.data,
                password=hash_and_salted_password
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('get_page1'))

    return render_template("register.html", form=form, current_user=current_user)


@app.route("/login", methods=["GET", "POST"])
def get_login():
    form = LoginForm()
    if form.validate_on_submit():
        if not User.query.filter_by(email=form.email.data).first():
            flash("kayıtlı kişi yok")
            return redirect(url_for("get_login"))
        user = User.query.filter_by(email=form.email.data).first()
        if check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("get_page1"))
        else:
            flash("şifre yanlış")
            return redirect(url_for("get_login"))

    return render_template("login.html", form=form)


@app.route("/logout")
def get_logout():
    logout_user()
    return redirect(url_for("home"))


# kartların gösterileceği yer olacak ve kart ekleme butonu yapılacak
@app.route("/page1")
@login_required
def get_page1():
    malum_liste = []
    for like in current_user.likes:
        malum_liste.append(like.cart_idd)

    follows = Follower.query.filter_by(name=current_user.name).all()
    carts_list = []
    for cart in current_user.carts:
        carts_list.append(cart)
    for follow in follows:
        for cart in follow.followed.carts:
            carts_list.append(cart)
    cart_dict = {cart.id: cart for cart in carts_list}
    cart_dict = dict(sorted(cart_dict.items()))
    list = [cart for cart in cart_dict.values()]
    list.reverse()

    return render_template("page1.html", current_user=current_user, malum_liste=malum_liste, carts=list)


@app.route("/page2")
@login_required
def get_page2():
    all_carts = db.session.query(Cart).all()
    malum_liste = []
    for like in current_user.likes:
        malum_liste.append(like.cart_idd)
    return render_template("page2.html", current_user=current_user, all_carts=all_carts, malum_liste=malum_liste)


# kart ****************************************************************************************************************
@app.route("/create_cart", methods=["GET", "POST"])
@login_required
def create_cart():
    form = SearchMovieForm()
    movie_data = []

    if form.validate_on_submit():
        movie_data = TakeMovie().data_without_description(movie_name=form.movie_name.data)
        return render_template("create_cart.html", movie_data=movie_data, form=form)

    return render_template("create_cart.html", form=form, movie_data=movie_data)


@app.route("/create_cart_phase/<path:movie>", methods=["GET", "POST"])
@login_required
def create_cart3(movie):
    movie = ast.literal_eval(movie) # convert from string to dictionary
    form = CartForm()

    if form.validate_on_submit():
        new_cart = Cart(
            title=movie["title"],
            year=movie["year"],
            text=form.text.data,
            author=current_user,
            poster_url=movie["poster_url"]
        )
        db.session.add(new_cart)
        db.session.commit()
        return redirect(url_for("get_page1"))

    return render_template("create_cart3.html", form=form, movie=movie)


# Profile ************************************************************************************************************
@app.route("/profile")
@login_required
def get_profile():
    return redirect(url_for("get_someone_profile", name=current_user.name, id=current_user.id))


@app.route("/<name>/<int:id>")
@login_required
def get_someone_profile(name, id):
    someone = User.query.filter_by(id=id).first()
    follower_id_list = []
    for follower in someone.followers:
        follower_id_list.append(follower.follower_id)

    someone = User.query.filter_by(name=someone.name).first()
    follows = Follower.query.filter_by(name=someone.name).all()
    follows_list = []
    for follow in follows:
        follows_list.append(follow.followed.name)

    malum_liste = []
    for like in current_user.likes:
        malum_liste.append(like.cart_idd)

    return render_template("someone_profile.html", current_user=current_user, someone=someone, follower_id_list=follower_id_list, follows_list=follows_list, malum_liste=malum_liste)


# Follow *************************************************************************************************************
@app.route("/get_follow/<int:someone_id>")
@login_required
def get_follow(someone_id):
    someone = User.query.filter_by(id=someone_id).first()
    new_follower = Follower(
        follower_id=current_user.id,
        name=current_user.name,
        followed=someone
    )
    db.session.add(new_follower)
    db.session.commit()
    return redirect(url_for("get_someone_profile", name=someone.name, id=someone_id))


@app.route("/<someone_name>")
@login_required
def get_unfollow(someone_name):
    someone = User.query.filter_by(name=someone_name).first()
    targeted_row = None
    for row in Follower.query.filter_by(follower_id=current_user.id).all():
        if row.followed_id == someone.id:
            targeted_row = row
    db.session.delete(targeted_row)
    db.session.commit()
    return redirect(url_for("get_someone_profile", name=someone.name, id=someone.id))


@app.route("/<head>/<someone_name>")
@login_required
def follow_info(head, someone_name):
    someone = User.query.filter_by(name=someone_name).first()
    follows = Follower.query.filter_by(name=someone_name).all()
    follows_list = []
    for follow in follows:
        follows_list.append(follow.followed)
    return render_template("follow_info.html", head=head, someone=someone, follows_list=follows_list)


# Likes ***************************************************************************************************************
@app.route("/get_like/<int:cart_id>")
@login_required
def get_like(cart_id):
    cart = Cart.query.filter_by(id=cart_id).first()
    new_like = Like(
        cart_idd=cart.id,
        liker=current_user,
        cart=cart
    )
    db.session.add(new_like)
    db.session.commit()
    return redirect(request.referrer)


@app.route("/like_info/<int:cart_id>")
@login_required
def like_info(cart_id):
    cart = Cart.query.filter_by(id=cart_id).first()
    like_list = []
    for like in cart.likes:
        like_list.append(like)
    return render_template("like_info.html", like_list=like_list)


@app.route("/get_unlike/<int:cart_id>")
@login_required
def get_unlike(cart_id):
    cart = Cart.query.filter_by(id=cart_id).first()

    targeted_like = None
    for like in cart.likes:
        if like.liker == current_user:
            targeted_like = like
    db.session.delete(targeted_like)
    db.session.commit()

    return redirect(request.referrer)


# comments ********************************************************************************************************
@app.route("/make_comment/<int:cart_id>", methods=["GET", "POST"])
@login_required
def make_comment(cart_id):
    cart = Cart.query.filter_by(id=cart_id).first()
    form = CommentForm()

    if form.validate_on_submit():
        new_comment = Comment(
            text=form.text.data,
            cart=cart,
            commenter=current_user
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("show_comments", cart_id=cart.id))

    return render_template("make_comment.html", cart=cart, form=form)


@app.route("/comments/<int:cart_id>")
@login_required
def show_comments(cart_id):
    cart = Cart.query.filter_by(id=cart_id).first()
    return render_template("show_comments.html", cart=cart)


@app.route("/alkmsdakmsd/<int:comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    db.session.delete(comment)
    db.session.commit()
    return redirect(request.referrer)


# room **************************************************************************************************************
@app.route("/room", methods=["GET", "POST"])
@login_required
def get_room():
    form = SearchMovieForm()

    if form.validate_on_submit():
        movies_data = TakeMovie().data_without_description(form.movie_name.data)
        return render_template("room.html", form=form, movies_data=movies_data)

    return render_template("room.html", form=form)


@app.route("/movie_room/<path:movie>", methods=["GET", "POST"])
@login_required
def get_movie_room(movie):
    movie = ast.literal_eval(movie)  # convert from string to dictionary
    form = CommentForm()

    text_dict = {text.id: text for text in RoomText.query.filter_by(movie_name=movie["title"]).all()}
    dict(sorted(text_dict.items()))

    text_list = []
    for text in text_dict:
        text1 = text_dict[text]
        if int(text1.movie_year) == int(movie["year"]):
            text_list.append(text1)
    text_list.reverse()
    print(text_list)

    if form.validate_on_submit():
        new_room_text = RoomText(
            author=current_user,
            text=form.text.data,
            movie_name=movie["title"],
            movie_year=movie["year"]
        )
        db.session.add(new_room_text)
        db.session.commit()

        text_dict = {text.id: text for text in RoomText.query.filter_by(movie_name=movie["title"]).all()}
        dict(sorted(text_dict.items()))

        text_list = []
        for text in text_dict:
            text1 = text_dict[text]
            if int(text1.movie_year) == int(movie["year"]):
                text_list.append(text1)
        text_list.reverse()
        print(text_list)

        return render_template("movie_room.html", movie=movie, form=form, text_list=text_list)

    return render_template("movie_room.html", movie=movie, form=form, text_list=text_list)


@app.route("/delete_text/<int:text_id>/<path:movie>", methods=["GET", "POST"])
@login_required
def delete_room_text(text_id, movie):
    text = RoomText.query.filter_by(id=text_id).first()
    db.session.delete(text)
    db.session.commit()
    return redirect(url_for("get_movie_room", movie=movie))


# main page *********************************************************************************************************
@app.route("/index")
def get_index():
    return render_template("index.html")


# run ***************************************************************************************************************
if __name__ == "__main__":
    app.run(debug=True)
