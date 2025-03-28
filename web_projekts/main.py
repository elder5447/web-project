from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from flask_peewee.db import Database
from flask_peewee.auth import Auth
from flask_peewee.admin import Admin, ModelAdmin
from peewee import TextField
import seaborn as sns
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, FloatField as FF
from wtforms.validators import DataRequired, Length, EqualTo

matplotlib.use('Agg')

app = Flask(__name__)

app.config["SECRET_KEY"] = "turku kebabs"

@app.route("/")
def home():
    return render_template("home_page.html")

@app.route("/weapons/<weapon_class>")
def weapons(weapon_class):
    df = pd.read_csv("static/all_weapons.csv")

    game_progression = request.args.get("progression", "any")

    if weapon_class.lower() == "all":
        filtered_df = df
    else:
        filtered_df = df[df["CLASS"].str.lower() == weapon_class.lower()]

    if game_progression.lower() == "any":
        filtered_df == filtered_df
    else:
        filtered_df = filtered_df[filtered_df["GAME PROGRESSION"].str.lower() == game_progression.lower()]

    progressions = df["GAME PROGRESSION"].dropna().unique().tolist()

    filtered_df.to_csv("static/filtered_weapons.csv", index=False)

    data = filtered_df.to_dict(orient="records")
    columns = filtered_df.columns.tolist()

    return render_template("weapons.html", columns=columns, data=data, weapon_class=weapon_class, progressions=progressions, current_progression=game_progression)

@app.route("/weapons/<weapon_class>/visualize")
def visualize_weapons(weapon_class):

    df = pd.read_csv("static/filtered_weapons.csv")

    data = df.to_dict(orient="records")
    columns = df.columns.tolist()

    sns.set_style("darkgrid")

    sns.histplot(df["DPS (SINGLE TARGET)"], bins="auto", color="blue")
    plt.savefig("static/images/histogram.png")
    plt.close()

    sns.scatterplot(df["DPS (SINGLE TARGET)"], color="blue")
    plt.savefig("static/images/scatterplot.png")
    plt.close()

    sns.histplot(df["DPS (MULTI TARGET)"], bins="auto", color="blue")
    plt.savefig("static/images/histogram2.png")
    plt.close()

    sns.scatterplot(df["DPS (MULTI TARGET)"], color="blue")
    plt.savefig("static/images/scatterplot2.png")
    plt.close()

    return render_template("visualize.html", columns=columns, data=data, weapon_class=weapon_class)

party_members = []

class AddPartyMember(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    role = StringField("Class", validators=[DataRequired()])
    weapon = StringField("Weapon", validators=[DataRequired()])
    submit = SubmitField("Add member")

@app.route("/party", methods=["GET", "POST"])
def member():
    form = AddPartyMember()

    if request.method == "POST" and form.validate_on_submit():
        new_member = {
            "name": form.name.data,
            "role": form.role.data,
            "weapon": form.weapon.data
        }
        party_members.append(new_member)

        form.name.data = ""
        form.role.data = ""
        form.weapon.data = ""

    return render_template("party.html", form=form, members=party_members)

@app.route("/redirect-to-party")
def redirect_to_party():
    return redirect(url_for("party"))

@app.route("/remove_member/<string:name>", methods=["POST"])
def remove_member(name):
    global party_members
    party_members = [m for m in party_members if m["name"] != name]
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)