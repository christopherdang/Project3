import kivy
import requests
import os
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.config import Config
import json
import time

Config.set('graphics', 'resizable', True)

# API Key and information in order to access Riot's API
API = os.environ.get('RiotAPI')
APItemp = "RGAPI-44a93cc5-b22f-4e8c-8f13-4badcd51d6e2"
KEY = "?api_key=" + APItemp

# Node class to store data in a binary tree
class Node:

    # Constructor
    def __init__(self, name, left, right):

        self.name = name
        self.left = left
        self.right = right

    # Insertion function
    def insertAcc(self, name):
        curr = self

        while True:
            # If name is less than the current node's name
            if name < curr.name:

                # If the node's left child is null, assign it to the new node
                if curr.left is None:
                    curr.left = Node(name, None, None)
                    return

                # Else, assign curr to curr left
                else:
                    curr = curr.left

            # Else if the name is greater than the current node's name
            elif name > curr.name:

                # If the node's right child is null, assign it to the new node
                if curr.right is None:
                    curr.right = Node(name, None, None)
                    return

                # Else, assign curr to curr right
                else:
                    curr = curr.right

    def searchAcc(self, name):
        curr = self

        while True:

            # If name is found, retrieve info from Riot API
            if name == curr.name:
                return

            # If name is less than the current node's name, set curr to curr left
            elif name < curr.name:
                curr = curr.left

            # Else if the name is greater than the current node's name, set curr to curr right
            elif name > curr.name:
                curr = curr.right

# Global variable for binary tree of accounts
global accTree
accTree = Node("root", None, None)

# Global variable for unordered set of accounts
global accSet
accSet = set(["root"])

# Opens json file of champion information
f = open('champions.json', encoding="utf8")
global champData
champData = json.load(f)

# pos_hint: {"x":, "y":, "top":, "bottom":, "left":, "right":}

# Class for the User-Interface
class MyApp(App):

    def build(self):
        FL = FloatLayout()

        # Variables that hold the string to display on the GUI
        self.convo = ["", "", "", "", "", "", "", "", "", ""]
        self.data = []
        self.cmdConvo = ""

        # Buttons to display on the GUI connected with a function as it's pushed
        self.searchAccTreeBtn = Button(text='Search Account Info (Binary Tree)', size_hint=(.4, .1), pos_hint={"right": 0.38, "top": 1},
                                 on_press=self.searchAccTreePushed)
        self.searchAccSetBtn = Button(text='Search Account Info (Unordered Set)', size_hint=(.4, .1),pos_hint={"right": 0.38, "top": .9},
                                      on_press=self.searchAccSetPushed)
        self.IdtoChampBtn = Button(text="Convert ID to Champion Name", size_hint=(.3, .1), pos_hint={"right": 1, "bottom": 1}, on_press=self.IdtoChampBtnPushed)
        self.messageInpBtn = TextInput(text='', size_hint=(.7, .1))
        self.messageOutBtn = Label(text="", size_hint=(1, 1))
        self.searchChampionBtn = Button(text="Search Champion Stats", size_hint=(.25, .1), pos_hint={"right": 1, "top": 1}, on_press=self.champStatsBtnPushed)
        self.insertAccBtn = Button(text='Insert Account Name', size_hint=(.2, .1), pos_hint={"left": 1, "top": .2}, on_press=self.insertAccPushed)

        # Adds the buttons to the GUI
        FL.add_widget(self.searchAccTreeBtn)
        FL.add_widget(self.searchAccSetBtn)
        FL.add_widget(self.messageInpBtn)
        FL.add_widget(self.messageOutBtn)
        FL.add_widget(self.searchChampionBtn)
        FL.add_widget(self.IdtoChampBtn)
        FL.add_widget(self.insertAccBtn)

        return FL

    # Function that converts champion ID number to the champion name
    def IdtoChampBtnPushed(self, obj):
        idTag = self.messageInpBtn.text

        for i in champData['data']:
            if champData['data'][i]['key'] == idTag:
                print(champData['data'][i])
                self.updateLabel("Champion: " + champData['data'][i]['id'])
                return

    # Function that displays the stats for the champion
    def champStatsBtnPushed(self, obj):
        champName = self.messageInpBtn.text

        # Finds the champion name in the json file
        for i in champData['data']:

            # If the champion is found, display the champion stats
            if i == champName:
                print(champData['data'][i]['info'])

                # Store the ints of stats in these variables
                attack = champData['data'][i]['info']['attack']
                defense = champData['data'][i]['info']['defense']
                magic = champData['data'][i]['info']['magic']
                difficulty = champData['data'][i]['info']['difficulty']

                # Display the stats on the GUI
                self.updateLabel("Champion Stats for: " + champName)
                self.updateLabel("Attack: " + str(attack))
                self.updateLabel("Defense: " + str(defense))
                self.updateLabel("Magic: " + str(magic))
                self.updateLabel("Difficulty: " + str(difficulty))
                self.updateLabel("")

                return

    # Function that inserts the account names into the binary tree and unordered set
    def insertAccPushed(self, obj):
        accName = self.messageInpBtn.text
        accTree.insertAcc(self.messageInpBtn.text)
        accSet.add(self.messageInpBtn.text)
        print("Inserted account: " + self.messageInpBtn.text)
        self.updateLabel(accName + " inserted")

    # Search for the account information through the binary tree
    def searchAccTreePushed(self, obj):
        time1 = time.perf_counter()

        print("Searching info through Binary Tree for: " + self.messageInpBtn.text)
        accTree.searchAcc(self.messageInpBtn.text)

        userInput = self.messageInpBtn.text

        # Requests information from Riot's API
        response = requests.get("https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + userInput + KEY)
        accJSON = response.json()

        # Retrieves varying account information
        id = accJSON['id']
        accId = accJSON['accountId']
        puuid = accJSON['puuid']
        name = accJSON['name']
        summonerLevel = accJSON['summonerLevel']

        response = requests.get("https://na1.api.riotgames.com/lol/champion-mastery/v4/scores/by-summoner/" + id + KEY)
        masteryTotal = response.json()

        response = requests.get("https://americas.api.riotgames.com/riot/account/v1/accounts/by-puuid/" + puuid + KEY)
        accJSON = response.json()

        response = requests.get("https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/" + id + KEY)
        output = response.json()
        accRank = output[0]["tier"]
        accRank2 = output[0]["rank"]

        response = requests.get("https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/" + id + KEY)
        output = response.json()
        accChamp = output[0]["championId"]
        accChampPts = output[0]["championPoints"]

        tagLine = accJSON['tagLine']

        # Display the account information on the GUI
        print("")
        self.updateLabel("")
        print("Summoner name: " + userInput)
        self.updateLabel("Summoner name: " + userInput)
        print("ID: " + id)
        self.updateLabel("ID: " + id)
        print("Account ID: " + accId)
        self.updateLabel("Account ID: " + accId)
        print("puuid: " + puuid)
        self.updateLabel("puuid: " + puuid)
        print("Summoner Level: " + str(summonerLevel))
        self.updateLabel("Summoner Level: " + str(summonerLevel))
        print("Tag Line: " + tagLine)
        self.updateLabel("Tag Line: " + tagLine)
        print("Rank: " + accRank + " " + accRank2)
        self.updateLabel("Rank: " + accRank + " " + accRank2)
        print("Most Played Champion: Champion ID " + str(accChamp) + " with " + str(accChampPts) + " points")
        self.updateLabel("Most Played Champion: Champion ID " + str(accChamp) + " with " + str(accChampPts) + " points")

        # Displays the execution time of the function
        time2 = time.perf_counter()
        finalTime = time2 - time1
        print("Time of exec: " + str(finalTime))
        print("Execution Time: " + str(finalTime))
        self.updateLabel("Execution Time: " + str(finalTime))

        print("")
        self.updateLabel("")

    # Function that searches account information through unordered set
    def searchAccSetPushed(self, obj):
        time1 = time.perf_counter()

        print("Searching info through Unordered Set for: " + self.messageInpBtn.text)
        # Traverses unordered set until the account is found
        for name_ in accSet:
            if name_ == self.messageInpBtn.text:
                userInput = name_

                # Requests information from Riot's API
                response = requests.get("https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + userInput + KEY)
                accJSON = response.json()

                # Retrieves varying account information
                id = accJSON['id']
                accId = accJSON['accountId']
                puuid = accJSON['puuid']
                name = accJSON['name']
                summonerLevel = accJSON['summonerLevel']

                response = requests.get("https://na1.api.riotgames.com/lol/champion-mastery/v4/scores/by-summoner/" + id + KEY)
                masteryTotal = response.json()

                response = requests.get("https://americas.api.riotgames.com/riot/account/v1/accounts/by-puuid/" + puuid + KEY)
                accJSON = response.json()

                response = requests.get("https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/" + id + KEY)
                output = response.json()
                accRank = output[0]["tier"]
                accRank2 = output[0]["rank"]

                response = requests.get("https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/" + id + KEY)
                output = response.json()
                accChamp = output[0]["championId"]
                accChampPts = output[0]["championPoints"]

                tagLine = accJSON['tagLine']

                # Displays account information on GUI
                print("")
                self.updateLabel("")
                print("Summoner name: " + userInput)
                self.updateLabel("Summoner name: " + userInput)
                print("ID: " + id)
                self.updateLabel("ID: " + id)
                print("Account ID: " + accId)
                self.updateLabel("Account ID: " + accId)
                print("puuid: " + puuid)
                self.updateLabel("puuid: " + puuid)
                print("Summoner Level: " + str(summonerLevel))
                self.updateLabel("Summoner Level: " + str(summonerLevel))
                print("Tag Line: " + tagLine)
                self.updateLabel("Tag Line: " + tagLine)
                print("Rank: " + accRank + " " + accRank2)
                self.updateLabel("Rank: " + accRank + " " + accRank2)
                print("Most Played Champion: Champion ID " + str(accChamp) + " with " + str(accChampPts) + " points")
                self.updateLabel("Most Played Champion: Champion ID " + str(accChamp) + " with " + str(accChampPts) + " points")

                # Displays execution time on GUI
                time2 = time.perf_counter()
                finalTime = time2 - time1
                print("Time of exec: " + str(finalTime))
                print("Execution Time: " + str(finalTime))
                self.updateLabel("Execution Time: " + str(finalTime))

                print("")
                self.updateLabel("")

    # Function that displays message on GUI
    def updateLabel(self, msg):
        self.convo[9] = self.convo[8]
        self.convo[8] = self.convo[7]
        self.convo[7] = self.convo[6]
        self.convo[6] = self.convo[5]
        self.convo[5] = self.convo[4]
        self.convo[4] = self.convo[3]
        self.convo[3] = self.convo[2]
        self.convo[2] = self.convo[1]
        self.convo[1] = self.convo[0]
        self.convo[0] = msg
        self.messageOutBtn.text = self.convo[9] + "\n" + "\n" + self.convo[8] + "\n" + "\n" + self.convo[7] + "\n" + "\n" + \
                               self.convo[6] + "\n" + "\n" + self.convo[5] + "\n" + "\n" + self.convo[4] + "\n" + "\n" + \
                               self.convo[3] + "\n" + "\n" + self.convo[2] + "\n" + "\n" + self.convo[1] + "\n" + "\n" + \
                               self.convo[0]

if __name__ == "__main__":
    MyApp().run()