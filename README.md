
# Chess Game with Stockfish AI Integration

## Project Overview

This is a desktop-based Chess game built using **Python** with a graphical interface powered by `pygame`. The game supports both **Player vs Player** and **Player vs AI** modes. In AI mode, the game utilizes **Stockfish**, a powerful open-source chess engine, to generate intelligent moves based on the current board state.

## Features

* Classic 8x8 Chessboard GUI
* Support for standard chess rules
* Legal move highlighting
* Check, checkmate, and stalemate detection
* Undo/redo functionality
* Player vs Player mode
* Player vs Computer (AI) mode
* Integration with Stockfish engine for AI move computation

## Technologies Used

* Python 3
* `pygame` for game GUI and rendering
* `python-chess` for chessboard logic and move validation
* `Stockfish` engine for AI computations

---

## What is Stockfish?

**Stockfish** is one of the strongest open-source chess engines in the world. It is used in professional chess tools and platforms to analyze games, suggest moves, and even play at superhuman levels. In this project, Stockfish is used as the AI opponent in the Player vs AI mode.

### Key Features of Stockfish:

* **UCI Protocol**: Stockfish communicates using the Universal Chess Interface (UCI), a standard protocol for chess engines.
* **Highly Efficient Search**: It uses alpha-beta pruning and iterative deepening to evaluate millions of positions per second.
* **Evaluation Function**: Considers piece activity, king safety, pawn structure, and positional advantages.
* **Open-source and extensible**: Freely available for integration and modification.
* **Multiple skill levels**: You can configure Stockfish to play at various skill levels depending on user preference.

### Stockfish in This Project:

* The `python-chess` library acts as a bridge between our GUI and the Stockfish engine.
* The engine is loaded through the UCI protocol.
* After each move by the player, the current FEN (Forsyth–Edwards Notation) is passed to Stockfish.
* Stockfish calculates the best possible move and returns it.
* The returned move is then applied to the board and reflected on the GUI.

---

## Installation Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/chess-stockfish-project.git
cd chess-stockfish-project
```

### 2. Install Dependencies

```bash
pip install pygame python-chess
```

### 3. Download and Setup Stockfish

* Download the Stockfish engine from the official site: [https://stockfishchess.org/download/](https://stockfishchess.org/download/)
* Extract the binary and place it in the project folder.
* Update the engine path in the code if necessary:

```python
stockfish = chess.engine.SimpleEngine.popen_uci("stockfish.exe")  # or the correct path on Linux/Mac
```

---

## How to Run

```bash
python main.py
```

You will be prompted to choose between Player vs Player or Player vs AI mode.

---

## Folder Structure

```
Chess_full_jinay/
│
├── assets/                  # Images and resources
├── stockfish.exe            # AI engine binary (place here after downloading)
├── main.py                  # Entry point of the application
├── game_logic.py            # Contains chess logic and interaction with Stockfish
├── gui.py                   # All rendering and input logic using pygame
└── README.md                # Project documentation
```

---

 License

This project is open-source and available under the MIT License. Please check the `LICENSE` file for more details.



## Acknowledgements

* [Stockfish Chess Engine](https://stockfishchess.org/)
* [python-chess Documentation](https://python-chess.readthedocs.io/en/latest/)
* [pygame Library](https://www.pygame.org/)




