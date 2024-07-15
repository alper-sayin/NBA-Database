from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, Boolean
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()
# Database Models


class Players(db.Model):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    is_active = Column(Boolean)
    nickname = Column(String)
    country = Column(String)
    jersey = Column(Integer)
    height = Column(String)
    weight = Column(Integer)
    position = Column(String)
    GP = Column(Integer)
    GS = Column(Integer)
    MIN = Column(Float)
    FGM = Column(Float)
    FGA = Column(Float)
    FG_PCT = Column(Float)
    FG3M = Column(Float)
    FG3A = Column(Float)
    FG3_PCT = Column(Float)
    FTM = Column(Float)
    FTA = Column(Float)
    FT_PCT = Column(Float)
    OREB = Column(Float)
    DREB = Column(Float)
    REB = Column(Float)
    AST = Column(Float)
    STL = Column(Float)
    BLK = Column(Float)
    TOV = Column(Float)
    PF = Column(Float)
    PTS = Column(Float)


class PlayerSchema(ma.Schema):
    class Meta():
     fields = ('id', 'full_name', 'first_name', 'last_name', 'is_active', 'nickname', 'country', 'jersey', 'height', 'weight', 'position', 'GP', 'GS', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS')


player_schema = PlayerSchema()
players_schema = PlayerSchema(many=True)


class Teams(db.Model):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    abbreviation = Column(String)
    nickname = Column(String)
    city = Column(String)
    state = Column(String)
    year_founded = Column(Integer)


class TeamSchema(ma.Schema):
    class Meta():
        fields = ('id', 'full_name', 'abbreviation', 'nickname', 'city', 'state', 'year_founded')


team_schema = TeamSchema()
teams_schema = TeamSchema(many=True)
