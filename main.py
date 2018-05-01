
import requests
from flask import Flask
from sklearn.externals.joblib import Memory
from sklearn.datasets import load_svmlight_file
from sklearn.svm import SVC
from os import listdir
from flask import Flask, request
import csv
from sklearn.linear_model import Perceptron
from sklearn.metrics import accuracy_score
import pandas as pd
"""
Created on Wed Apr 25 23:10:36 2018

@author: krish
"""

app = Flask(__name__)
def download_data(url, filename):
    r = requests.get(url)
    open(filename, 'wb').write(r.content)

def data_partition(filename, test_season, team1, team2):
    ftrain =csv.writer(open('train.csv','wb'))
    ftest =csv.writer(open('test.csv','wb'))
    
    fields = ['season', 'city', 'team1', 'team2', 'toss_winner', 'toss_decision', 'winner']
    match = pd.read_csv(filename, usecols=fields)
    ftrain.writerow(fields)
    ftest.writerow(fields)
    for i in range(len(match)):
        if ((int(match.iloc[i].season) < int(test_season)) and ((team1 == match.iloc[i].team1 and team2 == match.iloc[i].team2) or (team2 == match.iloc[i].team1 and team1 == match.iloc[i].team2))):
            ftrain.writerow((match.iloc[i]))
        elif(((int(match.iloc[i].season) >= int(test_season)) and ((team1 == match.iloc[i].team1 and team2 == match.iloc[i].team2) or (team2 == match.iloc[i].team1 and team1 == match.iloc[i].team2)))):
            ftest.writerow((match.iloc[i]))

def get_data(filename, team1, team2):
    fields = ['season', 'city', 'team1', 'team2', 'toss_winner', 'toss_decision', 'winner']
    match = pd.read_csv(filename, usecols=fields)
    home_venue = { 'Kolkata Knight Riders' : 'Kolkata',
'Royal Challengers Bangalore' : 'Bangalore',
'Chennai Super Kings' : 'Chennai',
'Kings XI Punjab' : 'Chandigarh',
'Rajasthan Royals' : 'Jaipur',
'Delhi Daredevils' : 'Delhi',
'Mumbai Indians' : 'Mumbai',
'Sunrisers Hyderabad' : 'Hyderabad',
'Rising Pune Supergiants' : 'Pune',
'Gujarat Lions' : 'Rajkot' }
    
    x = []
    y = []
    
    for i in range(len(match)):
        home = 0
        toss = 0
        bat_first = 0
        win = 0
        if(match.iloc[i].city == home_venue.get(team1)):
            home = 1
        if(match.iloc[i].toss_winner == team1):
            toss = 1
        if(match.iloc[i].toss_decision == 'bat'):
            bat_first = 1
        if(match.iloc[i].winner == team1 or match.iloc[i].winner == 'tied'):
            win = 1
        x.append([home, toss, bat_first])
        y.append(win)
    return x, y

  

@app.route('/')
def index():
    intro = "<br/>To download data : /api/download/data<br/>To partition data (provide arguments - team1 (use team code), team2 (use team code), test season(enter a season from 2008 - 2016)) : api/data/partition/--test_season--/--team1Code--/--team2Code--/<br/>To predict : /api/predict/--team1--/--team2--<br/>"
    teams = "<br/><br/>Teams:<br/>Royal Challengers Bangalore - code - RCB<br/>Mumbai Indians - code - MI<br/>Kings XI Punjab - code - KXIP<br/>Kolkata Knight Riders - code - KKR<br/>Delhi Daredevils - code - DD<br/>Sunrisers Hyderabad - code - SRH<br/><br/>"
    warning = "<br/>WARNING: ENTER SAME TEAM CODE AND IN THE SAME ORDER IN PARTITIONING AND PREDICTING DATA <br/>"
    footer = "<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>*Team Chennai Super Kings(Code - CSK) and Team Rajasthan Royals(Code - RR) not included due to suspension, but can be tested on seasons before and including 2015"
    return "IPL CRICKET MATCH PREDICTOR<br/>By Krish Hemant Mhatre<br/>" + intro + teams + warning + footer

@app.route('/api/download/data')
def download():
    url = 'https://www.dropbox.com/s/knm48gwdpm08xx7/matches.csv?dl=1'
    download_data(url=url, filename='match.csv')
    return "Data Downloaded" 

@app.route('/api/data/partition/<test_season>/<team1Code>/<team2Code>')
def partition(test_season, team1Code, team2Code):
    teams = {'CSK' : 'Chennai Super Kings', 'RR' : 'Rajasthan Royals', 'RCB' : 'Royal Challengers Bangalore', 'MI' : 'Mumbai Indians', 'KXIP' : 'Kings XI Punjab', 'KKR' : 'Kolkata Knight Riders', 'SRH' : 'Sunrisers Hyderabad', 'DD' : 'Delhi Daredevils'}
    team1 = teams[team1Code]
    team2 = teams[team2Code]
    data_partition('match.csv', test_season, team1, team2)
    return "Successfully Partitioned data for <br/><br/>" + team1 + "<br/>" + team2


@app.route('/api/get/data/test')
def gettestdata():
    Xtest, ytest = get_data("test.csv")
    return "Return Xtest and Ytest arrays"

@app.route('/api/get/data/train')
def gettraindata():
    Xtrain, ytrain = get_data("train.csv")
    
    return "Return Xtrain and Ytrain arrays"

@app.route('/api/predict/<team1Code>/<team2Code>')
def ptn(team1Code, team2Code):
    teams = {'CSK' : 'Chennai Super Kings', 'RR' : 'Rajasthan Royals', 'RCB' : 'Royal Challengers Bangalore', 'MI' : 'Mumbai Indians', 'KXIP' : 'Kings XI Punjab', 'KKR' : 'Kolkata Knight Riders', 'SRH' : 'Sunrisers Hyderabad', 'DD' : 'Delhi Daredevils'}
    team1 = teams[team1Code]
    team2 = teams[team2Code]
    x_train, y_train = get_data("train.csv", team1, team2)
    x_test, y_true = get_data("test.csv", team1, team2)
    ptn = Perceptron(max_iter=1000)    
    ptn.fit(x_train, y_train)                
  
    y_pred = ptn.predict(x_test)        
    accuracy = str(accuracy_score(y_true, y_pred)*100) + "%"
    if(sum(y_pred) != 0):
        return(team1 + " Wins<br/>Prediction Accuracy for " + team1 + " vs. " + team2 + " : " + str(accuracy))
    else:
        return(team2 + " Wins<br/>Prediction Accuracy for " + team1 + " vs. " + team2 + " : " + str(accuracy))


if __name__ == '__main__':
     app.run(host="127.0.0.1", debug=True, port=80)
