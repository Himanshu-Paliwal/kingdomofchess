import json

import chess
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST

from .forms import SignUpForm
from .models import PlayerProfile


# ──────────────────────────────────────────────
#  Page Views
# ──────────────────────────────────────────────

def index(request):
    """Chess board page."""
    return render(request, 'chess-frontend/index.html')


def signup_view(request):
    """User registration page."""
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            PlayerProfile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.success(request, f'Welcome to Kingdom of Chess, {username}!')
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'chess-frontend/signup.html', {'form': form})


def login_view(request):
    """User login page."""
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'chess-frontend/login.html')


def rankings_view(request):
    """Player rankings / leaderboard page."""
    players = PlayerProfile.objects.select_related('user').all()[:50]
    return render(request, 'chess-frontend/rankings.html', {'players': players})


# ──────────────────────────────────────────────
#  Chess API Views  (powered by python-chess)
# ──────────────────────────────────────────────

def _board_from_session(request):
    """Load a chess.Board from the session FEN, or create a new one."""
    fen = request.session.get('chess_fen')
    if fen:
        try:
            return chess.Board(fen)
        except ValueError:
            pass
    board = chess.Board()
    request.session['chess_fen'] = board.fen()
    return board


def _save_board(request, board):
    """Persist board state to session."""
    request.session['chess_fen'] = board.fen()


def _board_to_dict(board):
    """Convert current board state into a JSON-friendly dict."""
    # Map python-chess piece symbols to Unicode glyphs
    UNICODE_PIECES = {
        'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙',
        'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
    }

    squares = {}
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece:
            prefix = 'w' if piece.color == chess.WHITE else 'b'
            squares[chess.square_name(sq)] = {
                'symbol': UNICODE_PIECES[piece.symbol()],
                'code': f"{prefix}{piece.symbol().upper()}",
                'color': 'white' if piece.color == chess.WHITE else 'black',
                'type': piece.symbol().lower(),
            }

    # Detect last move for highlighting
    last_move = None
    if board.move_stack:
        lm = board.peek()
        last_move = {
            'from': chess.square_name(lm.from_square),
            'to': chess.square_name(lm.to_square),
        }

    return {
        'fen': board.fen(),
        'squares': squares,
        'turn': 'white' if board.turn == chess.WHITE else 'black',
        'is_check': board.is_check(),
        'is_checkmate': board.is_checkmate(),
        'is_stalemate': board.is_stalemate(),
        'is_game_over': board.is_game_over(),
        'is_insufficient_material': board.is_insufficient_material(),
        'fullmove_number': board.fullmove_number,
        'last_move': last_move,
        'outcome': _outcome_text(board),
    }


def _outcome_text(board):
    """Return a human-readable outcome string, or None if game is ongoing."""
    outcome = board.outcome()
    if outcome is None:
        return None
    winner = outcome.winner
    if winner is None:
        reason = str(outcome.termination.name).replace('_', ' ').title()
        return f"Draw — {reason}"
    color = "White" if winner == chess.WHITE else "Black"
    reason = str(outcome.termination.name).replace('_', ' ').title()
    return f"{color} wins — {reason}"


@require_POST
def api_new_game(request):
    """Start a new game — reset the board."""
    board = chess.Board()
    _save_board(request, board)
    return JsonResponse({'ok': True, **_board_to_dict(board)})


def api_game_state(request):
    """Return the current game state."""
    board = _board_from_session(request)
    return JsonResponse({'ok': True, **_board_to_dict(board)})


def api_legal_moves(request):
    """Return legal destination squares for a given source square."""
    square_name = request.GET.get('square', '')
    board = _board_from_session(request)

    try:
        sq = chess.parse_square(square_name)
    except ValueError:
        return JsonResponse({'ok': False, 'error': 'Invalid square'}, status=400)

    piece = board.piece_at(sq)
    if piece is None:
        return JsonResponse({'ok': False, 'error': 'No piece on that square'}, status=400)

    # Only allow selecting pieces of the current turn's color
    if piece.color != board.turn:
        return JsonResponse({
            'ok': False,
            'error': f"It is {'white' if board.turn == chess.WHITE else 'black'}'s turn",
        }, status=400)

    destinations = []
    for move in board.legal_moves:
        if move.from_square == sq:
            dest = chess.square_name(move.to_square)
            # Mark captures
            is_capture = board.is_capture(move)
            destinations.append({'square': dest, 'capture': is_capture})

    return JsonResponse({'ok': True, 'moves': destinations, 'square': square_name})


@require_POST
def api_make_move(request):
    """Validate and execute a move. Expects JSON body: {from, to, promotion?}."""
    board = _board_from_session(request)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    from_sq = data.get('from', '')
    to_sq = data.get('to', '')
    promotion = data.get('promotion', None)

    # Build UCI string
    uci_str = from_sq + to_sq
    if promotion:
        uci_str += promotion  # e.g. 'q', 'r', 'b', 'n'

    try:
        move = chess.Move.from_uci(uci_str)
    except ValueError:
        return JsonResponse({'ok': False, 'error': 'Invalid move format'}, status=400)

    if move not in board.legal_moves:
        return JsonResponse({'ok': False, 'error': 'Illegal move'}, status=400)

    # Check if this is a pawn promotion the client didn't specify
    piece = board.piece_at(move.from_square)
    if (piece and piece.piece_type == chess.PAWN
            and chess.square_rank(move.to_square) in (0, 7)
            and move.promotion is None):
        # Need promotion choice — ask the client
        return JsonResponse({
            'ok': False,
            'needs_promotion': True,
            'from': from_sq,
            'to': to_sq,
        })

    # SAN notation before pushing
    san = board.san(move)
    board.push(move)
    _save_board(request, board)

    return JsonResponse({'ok': True, 'san': san, **_board_to_dict(board)})
