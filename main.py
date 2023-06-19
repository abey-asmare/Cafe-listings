from flask import Flask, render_template, request, url_for , redirect, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from forms import SearchForm, LoginForm, RegisterForm, EditListingForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin,LoginManager, login_required, login_user, current_user, logout_user
from functools import wraps
from sqlalchemy.types import Boolean, String
from random import choices

app = Flask(__name__)
app.config['SECRET_KEY'] = "thesecretkey234234234324"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
login_manager = LoginManager(app)
db = SQLAlchemy(app)


# cafe table
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(250), unique = True, nullable = False)
    seats = db.Column(db.String(250), nullable=False)
    location = db.Column(db.String(200), nullable = False)
    map_url = db.Column(db.String(500),  nullable = False)
    img_url = db.Column(db.String(500), nullable = False)
    has_sockets = db.Column(db.Boolean, nullable = False)
    has_toilet = db.Column(db.Boolean, nullable = False)
    has_wifi = db.Column(db.Boolean, nullable = False)
    can_take_calls = db.Column(db.Boolean, nullable = False)
    coffee_price = db.Column(db.String(250), nullable = True)
# user table
class Users(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(250), nullable = False)
    email= db.Column(db.String(250), unique = True, nullable = False)
    password= db.Column(db.String(50), nullable = False)
# create all database
with app.app_context():
    db.create_all()

# login manager
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)

def admin_only(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if current_user.id != 1:
             return abort(403)
        return f(*args, **kwargs)
    return decorated_func

# get cafe function
def get_cafes(query_by, keyword, cafes) -> list:
    find_cafe_id = []
    if query_by == "name":
            find_cafe= Cafe.query.filter_by(name = keyword).all()
            find_cafe_id = [cafe.id for cafe in find_cafe]
    if query_by == "seats":
            find_cafe_id = [cafe.id for cafe in cafes if keyword in cafe.seats]
    if query_by == "location":
            find_cafe= Cafe.query.filter_by(location = keyword.title()).all()
            find_cafe_id = [cafe.id for cafe in find_cafe]
    if query_by == "map_url":
            find_cafe_id = [cafe.id for cafe in cafes if keyword in cafe.map_url]
    if query_by == "coffee_price":
           find_cafe_id = [cafe.id for cafe in cafes if keyword in cafe.coffee_price]
    return find_cafe_id

# return favorite cafes
def fav_cafes() -> list:
    cafes = Cafe.query.all()
    return [cafe.id for cafe in cafes if cafe.has_toilet and cafe.has_toilet and cafe.has_sockets]



@app.route("/", methods = ["GET", "POST"])
def home():
    cafes = Cafe.query.all()
    form = SearchForm()
    if form.validate_on_submit():
        query_by = form.select.data
        keyword = form.query.data
        find_cafe_id = get_cafes(query_by, keyword, cafes)
        return redirect(url_for('cafe_listing', cafes = find_cafe_id))
    return render_template("index.html", cafes = cafes[:5], form = form)

@app.route("/cafe-listings")
def cafe_listing():
    cafes = None
    cafes_id = request.args.to_dict(flat = False)
    if cafes_id:
        cafes_id = request.args.to_dict(flat = False)['cafes']
        cafes = [Cafe.query.get(cafe_id) for cafe_id in cafes_id]
    else:
        flash("cafe doesn't exist")
        return redirect(url_for('home'))
    return render_template("listing.html", cafes  = cafes)

@app.route("/favorites")
def favorites():
    return redirect(url_for('cafe_listing', cafes = fav_cafes()))

@app.route("/random-cafes")
def random_cafes():
    cafes = Cafe.query.all()
    all_cafe_id = [ cafe.id for cafe in cafes]
    return redirect(url_for('cafe_listing', cafes = choices(all_cafe_id, k=10)))

@app.route("/all-cafes")
def all_cafes():
    return redirect(url_for('cafe_listing', cafes = [cafe.id for cafe in Cafe.query.all()]))

@app.route("/update", methods = ["GET", "POST"])
@login_required
@admin_only
def edit_listing():
    form = SearchForm()
    cafes = Cafe.query.all()
    if form.validate_on_submit():
        query_by = form.select.data
        keyword = form.query.data
        find_cafe_id = get_cafes(query_by, keyword, cafes)
        return redirect(url_for('cafe_listing', cafes = find_cafe_id))
    return render_template("edit.html", form = form)


@app.route("/register", methods = ["GET", 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        user = Users.query.filter_by(email = form.email.data).first()
        if user:
            flash("Account Registerd. Login Instead")
            return redirect(url_for('login'))

        new_user = Users(name = form.name.data,
                         email =email,
                         password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length = 8) )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("register.html", form = form )

@app.route("/login", methods = ["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = Users.query.filter_by(email = email).first()
        if user:
            if check_password_hash(user.password, password ):
                login_user(user)
                flash(f'Welcome back, {user.name}')
            else:
                flash('Invalid credentials')
                return redirect(url_for('login.html'))
        else:
            flash('Account Doesn\'t exist Register Instead')
            return redirect(url_for('register'))
        return redirect(url_for('home'))
    return render_template('login.html', form = form)


@app.route("/update_listing/<int:cafe_id>", methods = ["POST", "GET"])
@login_required
@admin_only
def update_listing(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    form = EditListingForm(
        name = cafe.name,
        location = cafe.location,
        img_url = cafe.img_url,
        map_url = cafe.map_url,
        coffee_price = cafe.coffee_price,
        has_sockets = cafe.has_sockets,
        has_toilet = cafe.has_toilet,
        has_wifi = cafe.has_wifi,
        can_take_calls = cafe.can_take_calls,
        seats = cafe.seats)
    # when you update the data don't use commas
    if form.validate_on_submit():
        cafe.name = form.name.data
        cafe.seats = form.seats.data
        cafe.location= form.location.data
        cafe.map_url = form.map_url.data
        cafe.img_url = form.img_url.data
        cafe.has_sockets = form.has_sockets.data
        cafe.can_take_calls = form.can_take_calls.data
        cafe.has_toilet = form.has_toilet.data
        cafe.has_wifi = form.has_wifi.data
        cafe.coffee_price = form.coffee_price.data
        db.session.commit()
        return redirect(url_for('cafe_listing'))
    return render_template('update.html', form = form)

@app.route("/add-listing", methods = ["POST", "GET"])
@login_required
@admin_only
def add_listing():
    form = EditListingForm()
    if form.validate_on_submit():
        cafe = Cafe(
        name = form.name.data,
        seats = form.seats.data,
        location= form.location.data,
        map_url = form.map_url.data,
        img_url = form.img_url.data,
        has_sockets = form.has_sockets.data,
        can_take_calls = form.can_take_calls.data,
        has_toilet = form.has_toilet.data,
        has_wifi = form.has_wifi.data,
        coffee_price = form.coffee_price.data
        )
        db.session.add(cafe)
        db.session.commit()
        return redirect(url_for('cafe_listing'))
    return render_template('update.html', form = form)

@app.route("/delete/<int:cafe_id>")
@login_required
@admin_only
def delete_listing(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    db.session.delete(cafe)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
if __name__ == "__main__":
    app.run(debug=True)