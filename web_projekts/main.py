from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from peewee import *

app = Flask(__name__)

matplotlib.use('Agg')

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

    return render_template("visualize.html", weapon_class=weapon_class)

app.config["SECRET_KEY"] = "turku kebabs"

db = SqliteDatabase("members_db.sqlite")

class BaseModel(Model):
    class Meta:
        database = db

class Member(BaseModel):
    name = CharField()
    role = CharField()
    weapon = CharField()

def initialize_db():
    db.connect()
    db.create_tables([Member], safe=True)

class AddPartyMember(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    role = StringField("Class", validators=[DataRequired()])
    weapon = StringField("Weapon", validators=[DataRequired()])
    submit = SubmitField("Add member")

@app.route("/party", methods=["GET", "POST"])
def member():
    form = AddPartyMember()

    if form.validate_on_submit():
  
        Member.create(
            name=form.name.data,
            role=form.role.data,
            weapon=form.weapon.data
        )
        
        form.name.data = ""
        form.role.data = ""
        form.weapon.data = ""
        
        return redirect(url_for('member'))

    members = Member.select()
    return render_template("party.html", form=form, members=members)

@app.route('/members')
def show_members():
    members = Member.select()
    return render_template('members.html', members=members)

@app.route("/remove_member/<string:name>", methods=["POST"])
def remove_member(name):
    delete_member = Member.delete().where(Member.name == name)
    delete_member.execute()
    return redirect(url_for('member'))

if __name__ == "__main__":
    initialize_db()
    app.run(debug=True)