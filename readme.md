# ChessCore

*A comprehensive chess engine built with Python and Pygame, combining traditional AI algorithms with modern deep learning approaches.*

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.x-green.svg)
![Status](https://img.shields.io/badge/status-v0.1.0-orange.svg)
![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)

> “Every master was once a beginner. Every pro was once an amateur. Every icon was once an unknown.”

---

## 🎯 Overview

**ChessCore** starts as a fully playable chess game and evolves into a sophisticated engine capable of smart, human-like play. The project is designed to be educational *and* competitive—showcasing clean game architecture, classic search algorithms, and (eventually) deep learning.

---



## ✨ Features

### Complete Chess Implementation (v0.1.0)
- Full rules (all pieces, legal moves)
- Interactive GUI with **Pygame**
- Move validation & game state management
- Visual feedback for valid moves and selected pieces
- Turn-based gameplay with square highlighting
- **Undo** last move (`Z` key)
- Algebraic-like **notation output**

### Core Architecture
- Clean, modular codebase
- Efficient board representation
- Extensible move generation
- Object-oriented design for growth

---

## 🗺️ Roadmap

### Phase 1: Enhanced Game Features ⏳
- [x] **Special Moves:** Castling (both sides), En Passant, Promotion UI
- [ ] **Game State:** Check, Checkmate, Stalemate, Draw (50-move, repetition)
- [ ] **UI:** Move history panel, captured pieces, game clock, SFX

### Phase 2: Traditional AI Engine 🤖
- [ ] **Search:** Minimax, Alpha-Beta, Iterative Deepening, Transposition Tables
- [ ] **Evaluation:** Material, positional factors, king safety, endgame heuristics
- [ ] **Enhancements:** Quiescence, move ordering, null-move pruning, LMR

### Phase 3: Deep Learning Integration 🧠
- [ ] **NN Design:** Board encoding, CNNs, policy/value heads
- [ ] **Training:** Datasets, self-play generation, PyTorch/TensorFlow pipeline
- [ ] **Advanced:** AlphaZero-style with MCTS, RL from self-play

### Phase 4: Advanced Features 🎯
- [ ] **Engine I/O:** UCI protocol, GUI integration, engine vs engine
- [ ] **Analysis:** Position/game analysis, opening book, endgame tablebases
- [ ] **Performance:** Multithreading, GPU for NN, memory optimization, profiling

### Phase 5: Web & Mobile 🌐
- [ ] **Web:** Flask/FastAPI UI, online multiplayer (WebSockets), real-time play
- [ ] **Mobile:** React Native/Flutter, touch UI, offline AI opponent

---

## 🛠️ Tech Stack

- **Core:** Python 3.8+
- **GUI:** Pygame
- **AI/ML (planned):** PyTorch or TensorFlow
- **Database (planned):** SQLite (game storage)
- **Web (planned):** Flask or FastAPI
- **Testing (planned):** pytest

