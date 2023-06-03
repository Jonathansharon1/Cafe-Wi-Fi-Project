import random
from flask import Flask, jsonify, render_template, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SearchField, SubmitField, StringField, BooleanField, IntegerField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)


##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


    def to_dict(self):
        #Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            #Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


class SearchForm(FlaskForm):
    location = SearchField("", render_kw={"placeholder": "Let's find cafes..."})
    submit = SubmitField("Search")


class KeyInput(FlaskForm):
    password = StringField("Enter your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class AddCafe(FlaskForm):
    name = StringField("Cafe Name", validators=[DataRequired()])
    map_url = StringField("Map Url", validators=[DataRequired()])
    img_url = StringField("Image Url", validators=[DataRequired()])
    #location = request.form.get("loc"),
    has_sockets = BooleanField('The Cafe has sockets?')
    has_toilet = BooleanField('The Cafe has toilet?')
    has_wifi = BooleanField('The Cafe has Wi-Fi?')
    can_take_calls = BooleanField('The cafe can take calls?')
    seats = IntegerField("How many seats is in the Cafe?")
    coffee_price = IntegerField("How much costs coffe?")
    submit = SubmitField("Add The Cafe")


@app.route("/", methods=['GET', 'POST'])
def home():
    form = SearchForm()
    if form.validate_on_submit():
        loc = form.location.data
        print(loc)
        return search_by_location(search_input=loc)
    return render_template("index.html", form=form)


@app.route("/random", methods=['GET'])
def get_random_cafe():
    all_cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(all_cafes)
    return jsonify(cafe={
        "id": random_cafe.id,
        "name": random_cafe.name,
        "map_url": random_cafe.map_url,
        "img_url": random_cafe.img_url,
        "location": random_cafe.location,
        "seats": random_cafe.seats,
        "has_toilet": random_cafe.has_toilet,
        "has_wifi": random_cafe.has_wifi,
        "has_sockets": random_cafe.has_sockets,
        "can_take_calls": random_cafe.can_take_calls,
        "coffee_price": random_cafe.coffee_price,
    })


@app.route('/all')
def get_all_cafes():
    all_cafes = db.session.query(Cafe).all()
    all_cafes2 = [cafe.to_dict() for cafe in all_cafes]
    return jsonify(cafe=all_cafes2)


@app.route('/search', methods=['GET', 'POST'])
def search_by_location(search_input):
    loc_cafes = []
    print(search_input)
    cafes2 = db.session.query(Cafe).filter_by(location=search_input).all()
    if cafes2:
        for cafe in cafes2:
            loc_cafes.append(cafe)

    else:
        return render_template('not_found.html', loc=search_input)
    return render_template('cafe_card.html', all_cafes=loc_cafes, loc=search_input)


@app.route("/add", methods=["GET", "POST"])
def post_new_cafe():
    form = AddCafe()
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.args.get('place'),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    if form.validate_on_submit():
        db.session.add(new_cafe)
        db.session.commit()
        return search_by_location(new_cafe.location)
    return render_template("add_cafe.html", form=form)

@app.route('/update_price/<cafe_id>', methods=['PATCH'])
def update_cafe_price(cafe_id):
    new_price = request.args.get('new_price')
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


@app.route('/report-closed/<cafe_id>', methods=['GET', 'DELETE', 'POST'])
def delete_cafe(cafe_id):
    form = KeyInput()

    requested_api_key = "TopSecretAPIKey"
    api_key = form.password.data
    print(api_key)
    cafe = db.session.query(Cafe).get(cafe_id)
    if api_key == requested_api_key:
        if cafe:
            place = str(cafe.location)
            db.session.delete(cafe)
            db.session.commit()
            return search_by_location(place)

        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        print("password is not correct, try again.")
    return render_template("password_input.html", form=form)

## HTTP GET - Read Record

## HTTP POST - Create Record

## HTTP PUT/PATCH - Update Record

## HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
