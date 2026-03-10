# Imposter Game

## ⚠️ DISCLAIMER

This game uses the OpenAI API to generate word pairs for the game. 

The model used is `gpt-4o-mini`, which is a lightweight low cost version ($0.15 input, $0.075 output per 1M tokens).

## ❓ About 

One player is secretly the Imposter, everyone else is a civillian. 

Civillians all recieve the same secret word, while the Imposter recieves a different secret word. 

The goal of the Imposter is to blend in and not get caught, while the goal of the Civillians is to identify and eliminate the Imposter.


## ➡️ How to run

### 1) Clone the repository
```bash
git clone https://github.com/chaseungjoon/imposter
cd imposter
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Set OpenAI API key 
```bash
echo "OPENAI_API_KEY=your_api_key" > .env
```

### 4) Run the game
```bash
python main.py
```

## 🤔 How to play

### 1) Setup - Enter the names of all players

### 2) Initilize - The device is passed around so each player privately sees their secret word

### 3) Discussion - Players take turns each saying one word related to their secret word and try to figure out who the Imposter is

### 4) Voting - After a few (2~3) rounds of discussion, the players vote on who they think the Imposter is. 

### 5) Reveal - The player with the most votes is revealed and terminated.

### 6) End Game - If the Imposter is terminated, the Civillians win. If the Imposter is not terminated, the Imposter wins.


## ❇️ Features

- Pre configured scoring system for Civillians and Imposter
- Customizable number of players and rounds
- New word pair (new from log.csv) generation using OpenAI API


