from app import *
from sqlalchemy.dialects.mysql import INTEGER



class User(db.Model):
    __tablename__ = "user"

    id_user = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(255), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20))


class Deck(db.Model):
    __tablename__ = "deck"

    id_deck = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    background = db.Column(db.String(255), nullable=False)


class Card(db.Model):
    __tablename__ = "card"

    id_card = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    front_text = db.Column(db.String(255), nullable=False)
    back_text = db.Column(db.String(255), nullable=False)


class Deck_has_card(db.Model):
    __tablename__ = "deck_has_card"

    id_deck = db.Column(INTEGER(unsigned=True), db.ForeignKey("deck.id_deck"))
    id_card = db.Column(INTEGER(unsigned=True), db.ForeignKey("card.id_card"))


class User_has_deck(db.Model):
    __tablename__ = "user_has_deck"

    id_user = db.Column(INTEGER(unsigned=True), db.ForeignKey("user.id_user"))
    id_deck = db.Column(INTEGER(unsigned=True), db.ForeignKey("deck.id_deck"))
