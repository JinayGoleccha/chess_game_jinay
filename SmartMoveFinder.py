import random
from stockfish import Stockfish
import os
import platform
from ChessEngine import Move

class ChessAI:
    def __init__(self, skill_level=10, time_limit=0.5):
        # List of potential Stockfish paths
        stockfish_paths = [
            r"C:\Users\DELL\Desktop\CGG\stockfish.exe.exe",
        ]
        
        # Add platform-specific paths
        if platform.system() == "Windows":
            program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
            stockfish_paths.append(os.path.join(program_files, "Stockfish", "stockfish.exe"))
        elif platform.system() in ["Linux", "Darwin"]:
            stockfish_paths.extend([
                "/usr/local/bin/stockfish",
                "/usr/bin/stockfish",
                os.path.expanduser("~/stockfish")
            ])
        
        self.stockfish = None
        success = False
        
        # Try each path
        for path in stockfish_paths:
            try:
                print(f"Trying Stockfish path: {path}")
                if os.path.exists(path):
                    self.stockfish = Stockfish(path=path)
                    self.stockfish.get_board_visual()
                    print(f"Successfully initialized Stockfish at: {path}")
                    success = True
                    break
            except Exception as e:
                print(f"Failed to initialize Stockfish at {path}: {e}")
                self.stockfish = None
                continue
        
        # If all paths failed, try without specifying a path
        if not success:
            try:
                print("Trying to initialize Stockfish without path...")
                self.stockfish = Stockfish()
                self.stockfish.get_board_visual()
                print("Successfully initialized Stockfish without path")
                success = True
            except Exception as e:
                print(f"Failed to initialize Stockfish without path: {e}")
                self.stockfish = None
        
        # Configure Stockfish if successfully initialized
        if success and self.stockfish:
            try:
                self.stockfish.set_skill_level(skill_level)
                self.time_limit = time_limit * 1000
                self.stockfish.set_depth(18)
                self.stockfish.update_engine_parameters({
                    "UCI_Chess960": "false",
                    "Contempt": 0,
                    "Threads": 4
                })
                print("Stockfish configured successfully")
            except Exception as e:
                print(f"Error configuring Stockfish: {e}")
        else:
            print("WARNING: Stockfish initialization FAILED - will use random moves")

    def find_best_move(self, fen_position):
        if not self.stockfish:
            raise ValueError("Stockfish is not initialized")
            
        try:
            self.stockfish.set_fen_position(fen_position)
            best_move = self.stockfish.get_best_move_time(self.time_limit)
            
            # Get top moves to help debug
            try:
                top_moves = self.stockfish.get_top_moves(3)
                if top_moves:
                    print(f"Top 3 moves: {', '.join([f'{m['Move']} ({m['Centipawn']}cp)' for m in top_moves])}")
            except Exception as e:
                print(f"Warning: Couldn't get top moves: {e}")
                
            return best_move
        except Exception as e:
            print(f"Stockfish move error: {e}")
            raise

# Global AI instance (initialize once)
try:
    print("Initializing AI...")
    ai = ChessAI(skill_level=10, time_limit=0.5)
    if not ai.stockfish:
        print("AI initialized but Stockfish is not available")
    else:
        print("AI initialized successfully with Stockfish")
except Exception as e:
    print(f"AI initialization failed: {e}")
    ai = None

def convert_to_fen(gs):
    fen_parts = []
    
    # 1. Piece placement
    for row in range(8):
        empty = 0
        fen_row = ""
        for col in range(8):
            piece = gs.board[row][col]
            if piece == '--':
                empty += 1
            else:
                if empty > 0:
                    fen_row += str(empty)
                    empty = 0
                # Convert piece notation
                color, piece_type = piece[0], piece[1]
                fen_piece = piece_type.upper() if color == 'w' else piece_type.lower()
                fen_row += fen_piece
        if empty > 0:
            fen_row += str(empty)
        fen_parts.append(fen_row)
    piece_placement = "/".join(fen_parts)
    
    # 2. Active color
    active_color = 'w' if gs.white_to_move else 'b'
    
    # 3. Castling availability
    castling = []
    # White kingside
    if gs.white_castle_kingside:
        castling.append('K')
    if gs.white_castle_queenside:
        castling.append('Q')
    if gs.black_castle_kingside:
        castling.append('k')
    if gs.black_castle_queenside:
        castling.append('q')
    castling = "".join(castling) or "-"
    
    # 4. En passant
    ep = "-"
    if gs.enpassantPossible:
        row, col = gs.enpassantPossible
        ep = f"{'abcdefgh'[col]}{8 - row}"
    
    # 5. Halfmove clock (estimated from move log)
    halfmove = "0"
    
    # 6. Fullmove number
    fullmove = str(max(1, len(gs.move_log) // 2 + 1))
    
    fen = f"{piece_placement} {active_color} {castling} {ep} {halfmove} {fullmove}"
    return fen

def find_castle_move_in_valid_moves(gs, valid_moves, king_row, king_col, target_col):
    # Look for matching castle move in valid moves
    for move in valid_moves:
        if (move.start_row == king_row and 
            move.start_col == king_col and 
            move.end_col == target_col and
            move.isCastleMove):
            return move
    return None

def convert_to_your_move(chess_move, gs, valid_moves):
    if not chess_move or len(chess_move) < 4:
        print(f"Invalid move format from Stockfish: {chess_move}")
        return None
    
    # Standard conversion from algebraic notation to coordinates
    start_col = ord(chess_move[0]) - ord('a')
    start_row = 8 - int(chess_move[1])
    end_col = ord(chess_move[2]) - ord('a')
    end_row = 8 - int(chess_move[3])
    
    # Get the piece being moved
    piece = gs.board[start_row][start_col] if 0 <= start_row < 8 and 0 <= start_col < 8 else None
    
    # Enhanced castling detection
    if piece and piece[1] == 'K' and abs(start_col - end_col) == 2:
        # Determine castle side
        if end_col > start_col:  # Kingside
            target_col = start_col + 2
        else:  # Queenside
            target_col = start_col - 2
            
        castle_move = find_castle_move_in_valid_moves(gs, valid_moves, start_row, start_col, target_col)
        if castle_move:
            return castle_move
        
        print(f"Castling move {chess_move} not found. Valid moves:")
        for move in valid_moves:
            if move.isCastleMove:
                print(f"  {move.getChessNotation()}")
        return None
    
    # Handle promotion if present
    promotion = chess_move[4].upper() if len(chess_move) >= 5 else None
    
    # Find matching move in valid moves
    for move in valid_moves:
        if (move.start_row == start_row and 
            move.start_col == start_col and 
            move.end_row == end_row and 
            move.end_col == end_col):
            
            # Handle promotion
            if promotion and move.isPawnPromotion:
                move.promotion_choice = promotion
            
            return move
    
    # If no matching move found, print debug info
    print(f"Move {chess_move} not found in valid moves")
    print(f"Looking for: ({start_row},{start_col}) to ({end_row},{end_col})")
    print("Valid moves:")
    for valid_move in valid_moves:
        print(f"  {valid_move.getChessNotation()} - ({valid_move.start_row},{valid_move.start_col}) to ({valid_move.end_row},{valid_move.end_col})")
    
    return None

def findBestMove(gs, valid_moves):
    if not ai or not ai.stockfish:
        return findRandomMove(valid_moves)
    
    try:
        # Convert current position to FEN
        fen = convert_to_fen(gs)
        
        # Get best move from Stockfish
        best_move_uci = ai.find_best_move(fen)
        if not best_move_uci:
            return findRandomMove(valid_moves)
            
        # Convert Stockfish move to our Move format
        move = convert_to_your_move(best_move_uci, gs, valid_moves)
        
        # If conversion succeeded
        if move:
            # Format the move based on whose turn it is
            move_str = f"{len(gs.move_log)//2 + 1}.{'W' if gs.white_to_move else 'B'}({best_move_uci})"
            print(move_str)
            return move
        
        return findRandomMove(valid_moves)
    except Exception as e:
        print(f"Error in findBestMove: {e}")
        return findRandomMove(valid_moves)

def findRandomMove(valid_moves):
    if not valid_moves:
        raise ValueError("No valid moves available")
    return random.choice(valid_moves)