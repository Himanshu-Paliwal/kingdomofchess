# ♚ Kingdom of Chess

Welcome to **Kingdom of Chess**! This is a full-stack web application where chess enthusiasts can play on an interactive board with server-verified rules, track their matches, and climb the leaderboard. 

I built this project to solve a common problem with beginner chess apps: **unreliable client-side rules**. Instead of relying on JavaScript to guess if a move is legal, every single move in Kingdom of Chess is validated server-side by the official [`python-chess`](https://python-chess.readthedocs.io/) engine. If it’s not legal by FIDE rules, it doesn’t happen.

---

## ✨ Features at a Glance

### 1. ♟️ Server-Validated Chess Board
* **FIDE-compliant rule enforcement**: Castling, en passant, pinned piece restrictions, checks, and pawn promotions are all verified by `python-chess`.
* **Two-color high-contrast pieces**: Clean vector SVG pieces (solid White with dark borders vs. deep obsidian Black with crisp contours) that look sharp on any display.
* **Interactive visual cues**:
  * Click any piece to see its legal moves (soft dots for empty squares, target rings for captures).
  * Previous moves stay highlighted so you never lose track of the action.
  * King glows in crimson check alert when under direct attack.
* **Pawn Promotion Modal**: Reach the other side of the board and choose your Queen, Rook, Bishop, or Knight with one click.
* **Live Move History**: Notation log recorded in Standard Algebraic Notation (SAN), e.g., `1. e4 e5 2. Nf3`.

### 2. 🔐 Authentication System
* Clean, dark-fantasy themed **Login** and **Sign Up** pages.
* Password hashing and session management powered by Django’s battle-tested auth engine.
* Automatic player profile initialization upon registration (starting Elo: 1200).

### 3. 🏆 Hall of Champions (Player Rankings)
* Real-time leaderboard showcasing top players, Elo ratings, total games, win/loss counts, and dynamically calculated win rates.
* Custom visual badges for the top 3 contenders (Gold 🥇, Silver 🥈, Bronze 🥉).
* Database queries optimized with `select_related('user')` to avoid N+1 performance bottlenecks.

---

## 🛠️ Tech Stack

* **Backend**: Python 3.12, Django 6.1, `python-chess`
* **Frontend**: HTML5, CSS Grid (pure custom CSS with dark-mode aesthetic), Vanilla JavaScript (Fetch API)
* **Storage**: SQLite (with Django ORM and session-backed FEN storage)
* **Assets**: High-resolution vector SVGs for all 12 standard chess pieces

---

## 🚀 Quickstart Guide

Want to run Kingdom of Chess locally? Here’s how to get it up in less than 2 minutes:

### 1. Clone the repository
```bash
git clone https://github.com/your-username/kingdomofchess.git
cd kingdomofchess
```

### 2. Set up the virtual environment
```bash
# On Windows:
python -m venv venv
venv\Scripts\activate

# On macOS / Linux:
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install django python-chess
```

### 4. Apply database migrations
```bash
python manage.py migrate
```

### 5. Launch the development server
```bash
python manage.py runserver
```

Now open your browser and navigate to **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**! ♟️

---

## 📁 Project Structure

```text
kingdomofchess/
├── config/                      # Project configuration & settings
│   ├── settings.py              # Installed apps, auth redirects, session config
│   ├── urls.py                  # Root URL dispatcher
│   └── wsgi.py / asgi.py
│
├── chess_frontend/              # Main chess application
│   ├── models.py                # PlayerProfile (rating, games, wins, win_rate)
│   ├── views.py                 # Page views & python-chess REST API handlers
│   ├── urls.py                  # API routes (/api/make-move/, /api/legal-moves/, etc.)
│   ├── forms.py                 # Registration forms
│   │
│   ├── static/chess-frontend/
│   │   ├── css/style.css        # Custom responsive styling & themes
│   │   ├── js/app.js            # Auto-dismiss notifications
│   │   └── pieces/              # 12 high-res SVG pieces (wK, bQ, etc.)
│   │
│   └── templates/chess-frontend/
│       ├── base.html            # Dark-fantasy navbar, message alerts, footer
│       ├── index.html           # Interactive chess board & game controller
│       ├── login.html           # User login card
│       ├── signup.html          # Registration card
│       └── rankings.html         # Leaderboard & player stats table
│
├── ARCHITECTURE_AND_INTERVIEW_PREP.md  # Detailed interview cheatsheet & talking points
├── architecture.mmd             # Mermaid System Architecture diagram
├── sequence_flow.mmd            # Mermaid Move Validation sequence diagram
├── database_erd.mmd             # Mermaid Database Entity Relationship diagram
├── state_machine.mmd            # Mermaid Game State Machine diagram
├── manage.py
└── README.md
```

---

## 🧠 Under the Hood: How Moves Are Validated

Here’s the step-by-step flow whenever a player moves a piece:

```
[Browser Click: e2] 
       │
       ▼
[GET /api/legal-moves/?square=e2]
       │
       ├─► Loads FEN string from Django session
       ├─► python-chess calculates legal moves for e2
       └─► Returns valid target squares (e3, e4) to highlight
       │
[Player Clicks: e4]
       │
       ▼
[POST /api/make-move/ { from: "e2", to: "e4" }]
       │
       ├─► Server validates move against board.legal_moves
       ├─► Checks for special cases (checks, checkmates, pawn promotions)
       ├─► Pushes move & updates session FEN
       └─► Returns new board state + SAN notation ("e4")
```

If you'd like to dive into the full system diagrams, check out [`ARCHITECTURE_AND_INTERVIEW_PREP.md`](ARCHITECTURE_AND_INTERVIEW_PREP.md) or open the `.mmd` files in the repository.

---

## 🗺️ Roadmap & What's Next

- [x] Responsive 8x8 board with drag-and-drop / click-to-move
- [x] Strict FIDE move validation via `python-chess`
- [x] Two-color high-contrast SVG piece set
- [x] User authentication & Elo leaderboard
- [ ] Real-time multiplayer matchmaking with WebSockets (Django Channels)
- [ ] Single-player mode vs. a Stockfish AI engine bot
- [ ] PGN game export and replay viewer

---

## 🤝 Contributing & Feedback

Got ideas or spot a bug? Feel free to open an issue or submit a pull request! Any feedback on board mechanics or UI improvements is always appreciated.

---

*Crafted with passion for the game of chess.* ♚

