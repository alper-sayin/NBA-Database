from nba_api.stats.static import players as all_players
from nba_api.stats.static import teams as all_teams
from flask import Flask, jsonify, request, render_template, send_file
from flask_migrate import Migrate
import os
import csv
import json
from itertools import groupby
import plotly
import plotly.graph_objects as go
from openpyxl import Workbook
from io import BytesIO, StringIO
from databasemodels import *


app = Flask(__name__)
app.debug = True
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'NBA.db')
db.init_app(app)
ma.init_app(app)
migrate = Migrate(app, db)


# Flask CLI Commands

@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database created!')


@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database dropped!')


@app.cli.command('db_seed_teams')
def db_seed_teams():
    nba_teams = all_teams.get_teams()
    for data in nba_teams:
        team = Teams(**data)
        db.session.add(team)
    db.session.commit()
    print('NBA teams were added to database!')


@app.cli.command('db_seed_players')
def db_seed_players():
    nba_players = all_players.get_players()
    for data in nba_players:
        player = Players(**data)
        db.session.add(player)
    db.session.commit()
    print('NBA players were added to database!')


@app.cli.command('db_extend_player_info')
def db_extend_player_info():
    with open('nba_players.json', 'r') as file:
        player_data = json.load(file)
    for data in player_data:
        player = Players.query.filter_by(id=data['id']).first()
        if player:
            player.country = data['country']
            player.jersey = data['jersey']
            player.height = data['height']
            player.weight = data['weight']
            player.position = data['position']
            db.session.commit()
    print('Additional player information was added to the database!')


@app.cli.command('db_add_career_stats')
def db_add_career_stats():
    with open('career_stats_of_all_players.json', 'r') as file:
        players_career_data = json.load(file)
    for data in players_career_data:
        player = Players.query.filter_by(id=data['PLAYER_ID']).first()
        if player:
            player.GP = data['GP']
            player.GS = data['GS']
            player.MIN = data['MIN']
            player.FGM = data['FGM']
            player.FGA = data['FGA']
            player.FG_PCT = data['FG_PCT']
            player.FG3M = data['FG3M']
            player.FG3A = data['FG3A']
            player.FG3_PCT = data['FG3_PCT']
            player.FTM = data['FTM']
            player.FTA = data['FTA']
            player.FT_PCT = data['FT_PCT']
            player.OREB = data['OREB']
            player.DREB = data['DREB']
            player.REB = data['REB']
            player.AST = data['AST']
            player.STL = data['STL']
            player.BLK = data['BLK']
            player.TOV = data['TOV']
            player.PF = data['PF']
            player.PTS = data['PTS']
            db.session.commit()
    print('Career stats of all players were added to the database!')

# Flask Routes


@app.route('/')
def welcome():
    return render_template('index.html')


@app.route('/teams', methods=['GET'])
def teams():
    teams_list = Teams.query.all()
    result = teams_schema.dump(teams_list)
    return render_template("teams.html", teams=result)


@app.route('/players', methods=['GET'])
def players():
    show_active = request.args.get('show_active', 'false') == 'true'
    players_list = Players.query.order_by(Players.last_name).all()
    result = players_schema.dump(players_list)

    # Group players by the first letter of their last name
    grouped_players = {}
    for letter, group in groupby(result, key=lambda x: x['last_name'][0].upper()):
        grouped_players[letter] = list(group)
    return render_template('players.html', grouped_players=grouped_players, show_active=show_active)


@app.route('/player_details/<int:player_id>', methods=['GET'])
def player_details(player_id):
    player = db.session.get(Players, player_id)
    if player:
        result = player_schema.dump(player)
        return render_template('player_details.html', player=result)
    return "Player not found", 404


@app.route('/career_stats/<int:player_id>', methods=['GET'])
def career_stats(player_id):
    player = db.session.get(Players, player_id)
    if player:
        result = player_schema.dump(player)
        fig = go.Figure()
        for stat in ['PTS', 'REB', 'AST']:
            fig.add_trace(go.Bar(
                x=[stat],
                y=[result.get(stat, 0)],
                name=stat,
                text=[result.get(stat, 0)],
                textposition='auto',
            ))

        fig.update_layout(
            title={
                'text': f"{result['full_name']} Statistics",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': dict(size=24)
            },
            xaxis_title="Categories",
            yaxis_title="Values",
            legend_title="Stats",
            font=dict(
                family="Arial, sans-serif",
                size=14,
                color="RebeccaPurple"
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            bargap=0.15,
        )

        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightPink')

        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('career_stats.html', player=result, graphJSON=graphJSON)
    return "Player not found", 404


@app.route('/download_database', methods=['GET'])
def download_database():
    return render_template('download_database.html')


@app.route('/download_excel', methods=['GET'])
def download_excel():
    players_list = Players.query.all()
    wb = Workbook()
    ws = wb.active
    ws.title = "NBA Players"
    headers = [column.name for column in Players.__table__.columns]
    ws.append(headers)
    for player in players_list:
        ws.append([getattr(player, column) for column in headers])

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(output,
                     download_name='nba_players_database.xlsx',
                     as_attachment=True,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@app.route('/download_csv', methods=['GET'])
def download_csv():
    players_list = Players.query.all()
    output = StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)

    headers = [column.name for column in Players.__table__.columns]
    writer.writerow(headers)

    for player in players_list:
        writer.writerow([getattr(player, column) for column in headers])
    output.seek(0)

    return send_file(BytesIO(output.getvalue().encode('utf-8')),
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='nba_players_database.csv',)


@app.route('/api_json', methods=['GET'])
def api_json():
    players_list = Players.query.all()
    result = players_schema.dump(players_list)
    return jsonify(result)


if __name__ == '__main__':
    app.run()
