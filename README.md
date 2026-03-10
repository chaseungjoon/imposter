# Imposter Game

## ⚠️ DISCLAIMER

This game uses the **OpenAI API** to generate word pairs for the game. 

The model used is `gpt-4o-mini`, which is a lightweight low cost version ***($0.15 input, $0.075 output per 1M tokens)***.

## ❓ About 

For an ***N*** player game, ***N-1*** players (**civilians**) are given the same secret word, and one randomly selected player (**the imposter**) is given a different (but similar) secret word.

> ex) For a 4 player game, 3 players will be given "kitchen" and 1 player will be given "restaurant".

No one knows whether they are an **imposter** or a **civilian**.

The goal of the **imposter** is to blend in and not get caught, while the goal of the **civilians** is to identify and eliminate the **imposter**.


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

- After a few (2~3) rounds of discussion, the players vote on who they think the imposter is. 

### 5) Reveal 

- The player with the most votes is revealed and terminated.

### 6) End Game 

#### Imposter Terminated

> **If the imposter is terminated, the imposter has a chance to guess the civilian secret word.**

**A)** If the imposter guesses the civilian word correctly, the imposter wins and recieves points. 

**B)** If the imposter fails to guess the word, the civilians win and recieve points.

#### Civilian Terminated

> The imposter wins and recieves points, and the civilians who voted for the imposter also recieves points.

### 7) Next Round

- The game can continue for multiple rounds, with players accumulating points based on their performance in each round.

## ❇️ Features

- Pre configured scoring system for civilians and imposter
- Customizable number of players and rounds
- Word pair (different from pre-used words in log.csv) generation using OpenAI API


