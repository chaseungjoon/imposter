# Imposter Game

## ⚠️ DISCLAIMER

This game uses the **OpenAI API** to generate word pairs for the game. 

The model used is `gpt-4o-mini`, which is a lightweight low cost version ***($0.15 input, $0.075 output per 1M tokens)***.

## ❓ About 

For an ***N*** player game, ***N-1*** players (**civillians**) are given the same secret word, and one player (**the imposter**) is given a different (but similar) secret word.

> ex) For a 4 player game, 3 players will be given "kitchen" and 1 player will be given "restaurant".

No one knows whether they are an **imposter** or a **civillian**.

The goal of the **imposter** is to blend in and not get caught, while the goal of the **civillians** is to identify and eliminate the **imposter**.


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

### 1) Setup 

- Enter the names of all players

### 2) Initilize 

- The device is passed around so each player privately sees their secret word

### 3) Discussion 

- Players take turns each saying one word related to their secret word and try to figure out who the imposter is

### 4) Voting 

- After a few (2~3) rounds of discussion, the players vote on who they think the Imposter is. 

### 5) Reveal 

- The player with the most votes is revealed and terminated.

### 6) End Game 

- If the imposter is terminated, the imposter has a chance to guess the civillian secret word.
- If the imposter guesses the civillian's word correctly, the imposter wins and recieves points. 
- If the imposter fails to guess the word, the civillians win.

- If the imposter is not terminated, the imposter wins and recieves the highest points.
- The civillians who voted for the imposter recieves points. 

### 7) Next Round

- The game can continue for multiple rounds, with players accumulating points based on their performance in each round.

## ❇️ Features

- Pre configured scoring system for Civillians and Imposter
- Customizable number of players and rounds
- New word pair (new from log.csv) generation using OpenAI API


