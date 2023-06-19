from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField, SelectField,PasswordField,BooleanField
from wtforms.validators import DataRequired, InputRequired, Email,Length, URL


class SearchForm(FlaskForm):

    select = SelectField("Fields",
                         choices=["name", "seats", "location", "map_url", "coffee_price"])
    query = StringField("Search", validators=[DataRequired(), Length(min=3)])
    submit = SubmitField("submit")

class LoginForm(FlaskForm):
    email = StringField(validators=[Email(check_deliverability=True), DataRequired()])
    password = PasswordField(validators=[InputRequired(), Length(min=8)])
    submit = SubmitField("submit")

class RegisterForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    email = StringField(validators=[Email(check_deliverability=True), DataRequired()])
    password = PasswordField(validators=[InputRequired(), Length(min=8)])
    submit = SubmitField("submit")

class EditListingForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    seats = StringField(validators=[DataRequired()])
    location = StringField(validators=[DataRequired()])
    map_url = StringField(validators=[DataRequired(), URL()])
    img_url = StringField(validators=[DataRequired(), URL()])
    coffee_price = StringField(validators=[DataRequired()])
    has_sockets = BooleanField(default=False)
    has_wifi = BooleanField(default=False)
    has_toilet = BooleanField(default=False)
    can_take_calls = BooleanField(default=False)
    submit = SubmitField("Update")
