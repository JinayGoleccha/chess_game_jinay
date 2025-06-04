class GameState():
    def __init__(self):
        # Board setup
        self.board = [
            ['bR','bN','bB','bQ','bK','bB','bN','bR'],
            ['bp','bp','bp','bp','bp','bp','bp','bp'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['wp','wp','wp','wp','wp','wp','wp','wp'],
            ['wR','wN','wB','wQ','wK','wB','wN','wR']
        ]
        self.move_functions = {
            'p': self.getPawnMoves,
            'R': self.getRookMoves,
            'N': self.getKnightMoves,
            'B': self.getBishopMoves,
            'Q': self.getQueenMoves,
            'K': self.getKingMoves
        }
        self.white_to_move = True
        self.move_log = []
        self.white_king_loc = (7, 4)
        self.black_king_loc = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.in_check = False
        self.pins = []
        self.checks = []
        self.enpassantPossible = ()
        self.moves_log = []  # This will store move strings in algebraic notation
        self.fullmove_number = 1  # Starts at 1, increments after black moves
        
        # Castling rights
        self.white_castle_kingside = True
        self.white_castle_queenside = True
        self.black_castle_kingside = True
        self.black_castle_queenside = True
        self.castle_log = []

    def makeMove(self, move):
        # Clear the square where the piece was
        self.board[move.start_row][move.start_col] = '--'
        
        # Handle pawn promotion
        if move.isPawnPromotion:
            promoted_piece = move.piece_moved[0] + move.promotion_choice
            self.board[move.end_row][move.end_col] = promoted_piece
        # Handle en passant capture
        elif move.isEnpassantMove:
            self.board[move.end_row][move.end_col] = move.piece_moved
            self.board[move.start_row][move.end_col] = '--'  # Remove the captured pawn
        # Normal move
        else:
            self.board[move.end_row][move.end_col] = move.piece_moved
        
        # Update move log
        self.move_log.append(move)
        
        # Update en passant opportunity
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
            self.enpassantPossible = ((move.start_row + move.end_row) // 2, move.end_col)
        else:
            self.enpassantPossible = ()
        
        # Update king position if king moved
        if move.piece_moved == 'wK':
            self.white_king_loc = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_loc = (move.end_row, move.end_col)
        
        # Store current castling rights before updating them
        self.castle_log.append((
            self.white_castle_kingside, 
            self.white_castle_queenside,
            self.black_castle_kingside, 
            self.black_castle_queenside
        ))
        
        # Update castling rights
        self.updateCastleRights(move)
        
        # Handle castling move
        if move.isCastleMove:
            if move.end_col > move.start_col:  # Kingside
                # Move rook
                self.board[move.end_row][move.end_col-1] = self.board[move.end_row][7]
                self.board[move.end_row][7] = '--'
                # Update rook position for tracking if needed
            else:  # Queenside
                # Move rook
                self.board[move.end_row][move.end_col+1] = self.board[move.end_row][0]
                self.board[move.end_row][0] = '--'
        
        # Update moves log
        move_notation = move.getChessNotation()
        
        if self.white_to_move:
            # White's move - create new move pair
            self.moves_log.append(f"{self.fullmove_number}. {move_notation}")
        else:
            # Black's move - append to last move or create new if needed
            if len(self.moves_log) > 0 and len(self.moves_log[-1].split()) < 3:
                # Append black's move to existing white's move
                self.moves_log[-1] += f" {move_notation}"
                self.fullmove_number += 1
            else:
                # Shouldn't normally happen, but just in case
                self.moves_log.append(f"{self.fullmove_number}... {move_notation}")
                self.fullmove_number += 1

        # Switch turns
        self.white_to_move = not self.white_to_move
        

    def undoMove(self):
        if len(self.move_log) == 0:
            return  # No moves to undo
        
        move = self.move_log.pop()
        
        # Put the moved piece back
        self.board[move.start_row][move.start_col] = move.piece_moved
        
        # Handle en passant undo
        if move.isEnpassantMove:
            self.board[move.end_row][move.end_col] = '--'  # Remove moved pawn
            self.board[move.start_row][move.end_col] = move.piece_captured  # Put back captured pawn
        # Handle normal capture undo
        else:
            self.board[move.end_row][move.end_col] = move.piece_captured
        
        # Update king position if moved
        if move.piece_moved == 'wK':
            self.white_king_loc = (move.start_row, move.start_col)
        elif move.piece_moved == 'bK':
            self.black_king_loc = (move.start_row, move.start_col)
        
        # Restore en passant possibility
        self.enpassantPossible = move.enpassantPossible if hasattr(move, 'enpassantPossible') else ()
        
        # Restore castling rights
        if len(self.castle_log) > 0:
            castle_rights = self.castle_log.pop()
            self.white_castle_kingside = castle_rights[0]
            self.white_castle_queenside = castle_rights[1]
            self.black_castle_kingside = castle_rights[2]
            self.black_castle_queenside = castle_rights[3]
            
            # Restore rook position if castling was undone
            if move.isCastleMove:
                if move.end_col - move.start_col == 2:  # Kingside
                    # Move rook back from f to h
                    self.board[move.end_row][7] = self.board[move.end_row][5]
                    self.board[move.end_row][5] = '--'
                else:  # Queenside
                    # Move rook back from d to a
                    self.board[move.end_row][0] = self.board[move.end_row][3]
                    self.board[move.end_row][3] = '--'
        
        # Update moves log
                if len(self.moves_log) > 0:
                    if not self.white_to_move:
                        # If undoing black's move, we need to remove both moves
                        if len(self.moves_log[-1].split()) == 3:  # Contains both white and black moves
                            self.fullmove_number -= 1
                            self.moves_log.pop()
                        else:
                            # Just remove black's move
                            parts = self.moves_log[-1].split()
                            self.moves_log[-1] = parts[0]  # Keep just the move number and white's move
                    else:
                        # Undoing white's move - remove the last entry
                        if len(self.moves_log[-1].split()) == 3:  # Contains both moves
                            parts = self.moves_log[-1].split()
                            self.moves_log[-1] = f"{parts[0]} {parts[1]}"  # Keep just white's move
                        else:
                            self.moves_log.pop()

        # Switch turns back
        self.white_to_move = not self.white_to_move
        

    def updateCastleRights(self, move):
        # King moves - revoke all castling rights for that color
        if move.piece_moved == 'wK':
            self.white_castle_kingside = False
            self.white_castle_queenside = False
        elif move.piece_moved == 'bK':
            self.black_castle_kingside = False
            self.black_castle_queenside = False
        
        # Rook moves - revoke specific castling right
        elif move.piece_moved == 'wR':
            if move.start_row == 7:  # Only check if it's a rook in the back rank
                if move.start_col == 0:  # Queenside rook (a1)
                    self.white_castle_queenside = False
                elif move.start_col == 7:  # Kingside rook (h1)
                    self.white_castle_kingside = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:  # Only check if it's a rook in the back rank
                if move.start_col == 0:  # Queenside rook (a8)
                    self.black_castle_queenside = False
                elif move.start_col == 7:  # Kingside rook (h8)
                    self.black_castle_kingside = False
        
        # Rook captures - revoke specific castling right
        if move.piece_captured == 'wR':
            if move.end_row == 7:  # Only check if it's a rook in the back rank
                if move.end_col == 0:  # Queenside rook
                    self.white_castle_queenside = False
                elif move.end_col == 7:  # Kingside rook
                    self.white_castle_kingside = False
        elif move.piece_captured == 'bR':
            if move.end_row == 0:  # Only check if it's a rook in the back rank
                if move.end_col == 0:  # Queenside rook
                    self.black_castle_queenside = False
                elif move.end_col == 7:  # Kingside rook
                    self.black_castle_kingside = False

    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        moves = []
        self.in_check, self.pins, self.checks = self.checkForPinsAndChecks()
    
        if self.white_to_move:
            king_row, king_col = self.white_king_loc
        else:
            king_row, king_col = self.black_king_loc
        
        if self.in_check:
            if len(self.checks) == 1:  # Only 1 check, block or move king
                moves = self.getAllPossibleMoves()
                # Must block check or capture checking piece
                check = self.checks[0]
                
                # Get check information
                if len(check) >= 3:  # For normal pieces (row, col, direction)
                    check_row, check_col = check[0], check[1]
                    if len(check) >= 4:  # Direction provided
                        direction = (check[2], check[3])
                    else:
                        direction = None
                else:
                    check_row, check_col = check[0], check[1]
                    direction = None
                
                checking_piece = self.board[check_row][check_col]
                
                valid_squares = []
                if checking_piece[1] == 'N':  # Knight must be captured
                    valid_squares = [(check_row, check_col)]
                else:
                    if direction:  # Only proceed if we have a direction
                        for i in range(1, 8):
                            valid_square = (king_row + direction[0] * i, 
                                      king_col + direction[1] * i)
                            valid_squares.append(valid_square)
                            if valid_square[0] == check_row and valid_square[1] == check_col:
                                break
                
                # Remove moves that don't block check or move king
                for i in range(len(moves)-1, -1, -1):
                    if i < len(moves):  # Check if index is still valid
                        move = moves[i]
                        if move.piece_moved[1] != 'K':  # Not king move
                            if not (move.end_row, move.end_col) in valid_squares:
                                moves.remove(move)
                
                # Get king moves
                king_moves = []
                self.getKingMoves(king_row, king_col, king_moves)
                
                # Filter king moves to those that don't result in check
                for move in king_moves:
                    self.makeMove(move)
                    self.white_to_move = not self.white_to_move  # Switch turn back
                    in_check, _, _ = self.checkForPinsAndChecks()
                    if not in_check:
                        moves.append(move)
                    self.white_to_move = not self.white_to_move
                    self.undoMove()
            else:  # Double check, king must move
                self.getKingMoves(king_row, king_col, moves)
                # Filter to valid king moves
                valid_king_moves = []
                for i in range(len(moves)-1, -1, -1):
                    if i < len(moves):  # Check index validity
                        move = moves[i]
                        self.makeMove(move)
                        self.white_to_move = not self.white_to_move
                        in_check, _, _ = self.checkForPinsAndChecks()
                        if not in_check:
                            valid_king_moves.append(move)
                        self.white_to_move = not self.white_to_move
                        self.undoMove()
                moves = valid_king_moves
        else:
            # Get all possible moves when not in check
            moves = self.getAllPossibleMoves()
            
            for i in range(len(moves)-1, -1, -1):
                if i < len(moves):  # Check index validity
                    self.makeMove(moves[i])
                    in_check, _, _ = self.checkForPinsAndChecks()
                    if in_check:
                        moves.remove(moves[i])
                    self.undoMove()
        
        # Check for checkmate or stalemate
        if len(moves) == 0:
            if self.in_check:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        
        self.enpassantPossible = tempEnpassantPossible
        return moves

    def getKingMoves(self, r, c, moves):
        row_moves = [-1, -1, -1, 0, 0, 1, 1, 1]
        col_moves = [-1, 0, 1, -1, 1, -1, 0, 1]
        ally_color = 'w' if self.white_to_move else 'b'
        
        # Regular king moves
        for i in range(8):
            end_row = r + row_moves[i]
            end_col = c + col_moves[i]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # Not an ally piece
                    # Place king on new square temporarily
                    self.board[r][c] = '--'
                    if ally_color == 'w':
                        self.white_king_loc = (end_row, end_col)
                    else:
                        self.black_king_loc = (end_row, end_col)
                    
                    # Store the captured piece
                    captured_piece = self.board[end_row][end_col]
                    self.board[end_row][end_col] = ally_color + 'K'
                    
                    # Check if the move would result in check
                    in_check = self.inCheck(ally_color)
                    
                    # Restore the board
                    self.board[r][c] = ally_color + 'K'
                    self.board[end_row][end_col] = captured_piece
                    if ally_color == 'w':
                        self.white_king_loc = (r, c)
                    else:
                        self.black_king_loc = (r, c)
                    
                    # If the move doesn't result in check, add it
                    if not in_check:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
        
        # Castling moves
        self.getCastleMoves(r, c, moves, ally_color)

    def getCastleMoves(self, r, c, moves, ally_color):
        if self.in_check:
            return  # Can't castle while in check
        
        if (self.white_to_move and self.white_castle_kingside) or (not self.white_to_move and self.black_castle_kingside):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.white_to_move and self.white_castle_queenside) or (not self.white_to_move and self.black_castle_queenside):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if (self.board[r][c+1] == '--' and 
            self.board[r][c+2] == '--' and
            not self.squareUnderAttack(r, c) and
            not self.squareUnderAttack(r, c+1) and
            not self.squareUnderAttack(r, c+2)):
            moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if (self.board[r][c-1] == '--' and 
            self.board[r][c-2] == '--' and 
            self.board[r][c-3] == '--' and
            not self.squareUnderAttack(r, c) and
            not self.squareUnderAttack(r, c-1) and
            not self.squareUnderAttack(r, c-2)):
            moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))

    def inCheck(self, color):
        if color == 'w':
            king_row, king_col = self.white_king_loc
        else:
            king_row, king_col = self.black_king_loc
        
        # Temporarily switch turns to get opponent's perspective
        self.white_to_move = not (color == 'w')
        opponent_moves = self.getAllPossibleMoves()
        self.white_to_move = (color == 'w')  # Switch back
        
        for move in opponent_moves:
            if move.end_row == king_row and move.end_col == king_col:
                return True
        return False

    def squareUnderAttack(self, r, c):
        original_turn = self.white_to_move
        self.white_to_move = not original_turn  # Switch to opponent's perspective
        
        # Check for attacking pawns
        pawn_dir = 1 if self.white_to_move else -1
        for dc in [-1, 1]:  # Check diagonal pawn attacks
            if 0 <= r+pawn_dir < 8 and 0 <= c+dc < 8:
                piece = self.board[r+pawn_dir][c+dc]
                if piece == ('w' if self.white_to_move else 'b') + 'p':
                    self.white_to_move = original_turn
                    return True
        
        # Check knight attacks
        knight_moves = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
        for dr, dc in knight_moves:
            if 0 <= r+dr < 8 and 0 <= c+dc < 8:
                piece = self.board[r+dr][c+dc]
                if piece == ('w' if self.white_to_move else 'b') + 'N':
                    self.white_to_move = original_turn
                    return True
        
        # Check sliding pieces (queen, rook, bishop)
        directions = [(-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
        for dr, dc in directions:
            for i in range(1, 8):
                end_row, end_col = r + dr*i, c + dc*i
                if not (0 <= end_row < 8 and 0 <= end_col < 8):
                    break
                piece = self.board[end_row][end_col]
                if piece != '--':
                    if piece[0] == ('w' if self.white_to_move else 'b'):
                        piece_type = piece[1]
                        if (dr in (-1,0,1)) and (dc in (-1,0,1)):  # Diagonal
                            if piece_type in ['B', 'Q']:
                                self.white_to_move = original_turn
                                return True
                        else:  # Orthogonal
                            if piece_type in ['R', 'Q']:
                                self.white_to_move = original_turn
                                return True
                    break
        
        self.white_to_move = original_turn
        return False

    def getAllPossibleMoves(self):
        """Get all possible moves without considering checks"""
        moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece != '--':
                    piece_color = piece[0]
                    if (piece_color == 'w' and self.white_to_move) or (piece_color == 'b' and not self.white_to_move):
                        piece_type = piece[1]
                        if piece_type in self.move_functions:
                            self.move_functions[piece_type](r, c, moves)
        return moves

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        in_check = False
        
        if self.white_to_move:
            enemy_color = 'b'
            ally_color = 'w'
            start_row, start_col = self.white_king_loc
        else:
            enemy_color = 'w'
            ally_color = 'b'
            start_row, start_col = self.black_king_loc
            
        # Check outward from king for pins and checks
        directions = [(-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = ()
            for i in range(1,8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != 'K':
                        if possible_pin == ():  # First allied piece could be pinned
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else:  # Second allied piece, no pin
                            break
                    elif end_piece[0] == enemy_color:
                        type = end_piece[1]
                        # Check if piece can attack king
                        if (0 <= j <= 3 and type == 'R') or \
                           (4 <= j <= 7 and type == 'B') or \
                           (i == 1 and type == 'p' and ((enemy_color == 'w' and 6 <= j <= 7) or (enemy_color == 'b' and 4 <= j <= 5))) or \
                           (type == 'Q') or (i == 1 and type == 'K'):
                            if possible_pin == ():  # No blocking piece
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:  # Piece blocking, so pin
                                pins.append(possible_pin)
                                break
                        else:  # Enemy piece not applying check
                            break
                else:  # Off board
                    break
        
        # Check for knight checks
        knight_moves = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
        for m in knight_moves:
            end_row = start_row + m[0]
            end_col = start_col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == 'N':
                    in_check = True
                    checks.append((end_row, end_col, m[0], m[1]))
        
        return in_check, pins, checks


    def getPawnMoves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
    
        if self.white_to_move:
            move_amount = -1
            start_row = 6
            enemy_color = 'b'
        else:
            move_amount = 1
            start_row = 1
            enemy_color = 'w'
    
        # Pawn pushes
        if self.board[r+move_amount][c] == '--':
            if not piece_pinned or pin_direction == (move_amount, 0):
                # Check if this move would result in promotion
                if (r+move_amount == 0 and self.white_to_move) or (r+move_amount == 7 and not self.white_to_move):
                    moves.append(Move((r,c), (r+move_amount,c), self.board, promotion_choice='Q'))
                else:
                    moves.append(Move((r,c), (r+move_amount,c), self.board))
                # Double pawn push
                if r == start_row and self.board[r+2*move_amount][c] == '--':
                    moves.append(Move((r,c), (r+2*move_amount,c), self.board))
    
        # Pawn captures
        for d in [-1, 1]:  # Left and right capture
            if 0 <= c+d < 8:
                if not piece_pinned or pin_direction == (move_amount, d):
                    # Normal capture
                    if self.board[r+move_amount][c+d][0] == enemy_color:
                        # Promotion capture
                        if (r+move_amount == 0 and self.white_to_move) or (r+move_amount == 7 and not self.white_to_move):
                            moves.append(Move((r,c), (r+move_amount,c+d), self.board, promotion_choice='Q'))
                        else:
                            moves.append(Move((r,c), (r+move_amount,c+d), self.board))
                    # En passant
                    elif (r+move_amount, c+d) == self.enpassantPossible:
                        moves.append(Move((r,c), (r+move_amount,c+d), self.board, isEnpassantMove=True))

    def getRookMoves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                # Queen can be pinned and still move along pin direction
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break
        
        directions = [(-1,0),(0,-1),(1,0),(0,1)]  # up, left, down, right
        enemy_color = 'b' if self.white_to_move else 'w'
        
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    # Check if moving along pin direction or not pinned
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == '--':  # Empty square
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:  # Capture
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break
                        else:  # Friendly piece
                            break
                    else:  # Moving against pin direction
                        break
                else:  # Off board
                    break

    def getBishopMoves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                # Queen can be pinned and still move along pin direction
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break
        
        directions = [(-1,-1),(-1,1),(1,-1),(1,1)]  # diagonals
        enemy_color = 'b' if self.white_to_move else 'w'
        
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    # Check if moving along pin direction or not pinned
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == '--':  # Empty square
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:  # Capture
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break
                        else:  # Friendly piece
                            break
                    else:  # Moving against pin direction
                        break
                else:  # Off board
                    break

    def getKnightMoves(self, r, c, moves):
        piece_pinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break
        
        knight_moves = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
        ally_color = 'w' if self.white_to_move else 'b'
        
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if not piece_pinned:  # Knight cannot move while pinned
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally_color:  # Empty or enemy square
                        moves.append(Move((r, c), (end_row, end_col), self.board))

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        row_moves = [-1, -1, -1, 0, 0, 1, 1, 1]
        col_moves = [-1, 0, 1, -1, 1, -1, 0, 1]
        ally_color = 'w' if self.white_to_move else 'b'
        
        for i in range(8):
            end_row = r + row_moves[i]
            end_col = c + col_moves[i]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    # Placeholder for king
                    original_king_pos = self.board[r][c]
                    original_target_pos = self.board[end_row][end_col]
                    
                    # Make the move
                    self.board[r][c] = '--'
                    self.board[end_row][end_col] = ally_color + 'K'
                    
                    # Update king position temporarily
                    if ally_color == 'w':
                        temp_king_loc = self.white_king_loc
                        self.white_king_loc = (end_row, end_col)
                    else:
                        temp_king_loc = self.black_king_loc
                        self.black_king_loc = (end_row, end_col)
                    
                    # Check for checks
                    in_check, _, _ = self.checkForPinsAndChecks()
                    
                    # Undo the move
                    self.board[r][c] = original_king_pos
                    self.board[end_row][end_col] = original_target_pos
                    if ally_color == 'w':
                        self.white_king_loc = temp_king_loc
                    else:
                        self.black_king_loc = temp_king_loc
                    
                    if not in_check:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
        
        # Castling moves
        if not self.in_check:
            if self.white_to_move:
                if r == 7 and c == 4:  # White king
                    # Kingside
                    if (self.white_castle_kingside and 
                        self.board[7][5] == '--' and 
                        self.board[7][6] == '--' and
                        not self.squareUnderAttack(7, 4) and  # Changed here
                        not self.squareUnderAttack(7, 5) and  # Changed here
                        not self.squareUnderAttack(7, 6)):    # Changed here
                        moves.append(Move((7,4), (7,6), self.board, isCastleMove=True))
                    # Queenside
                    if (self.white_castle_queenside and 
                        self.board[7][3] == '--' and 
                        self.board[7][2] == '--' and 
                        self.board[7][1] == '--' and
                        not self.squareUnderAttack(7, 4) and  # Changed here
                        not self.squareUnderAttack(7, 3) and  # Changed here
                        not self.squareUnderAttack(7, 2)):    # Changed here
                        moves.append(Move((7,4), (7,2), self.board, isCastleMove=True))
            else:
                if r == 0 and c == 4:  # Black king
                    # Kingside
                    if (self.black_castle_kingside and 
                        self.board[0][5] == '--' and 
                        self.board[0][6] == '--' and
                        not self.squareUnderAttack(0, 4) and  # Changed here
                        not self.squareUnderAttack(0, 5) and  # Changed here
                        not self.squareUnderAttack(0, 6)):    # Changed here
                        moves.append(Move((0,4), (0,6), self.board, isCastleMove=True))
                    # Queenside
                    if (self.black_castle_queenside and 
                        self.board[0][3] == '--' and 
                        self.board[0][2] == '--' and 
                        self.board[0][1] == '--' and    
                        not self.squareUnderAttack(0, 4) and  # Changed here
                        not self.squareUnderAttack(0, 3) and  # Changed here
                        not self.squareUnderAttack(0, 2)):     # Changed here
                        moves.append(Move((0,4), (0,2), self.board, isCastleMove=True))   

    def getKingsideCastleMoves(self, r, c, moves):
        if (self.board[r][5] == '--' and  # f-file
            self.board[r][6] == '--'):    # g-file
            if (not self.squareUnderAttack(r, 4) and  # e-file (king)
            not self.squareUnderAttack(r, 5) and   # f-file
            not self.squareUnderAttack(r, 6)):     # g-file
                if (self.white_to_move and self.white_castle_kingside) or \
                (not self.white_to_move and self.black_castle_kingside):
                    if self.board[r][7][1] == 'R':  # h-file rook
                        moves.append(Move((r, 4), (r, 6), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if (self.board[r][1] == '--' and  # b-file
            self.board[r][2] == '--' and   # c-file
            self.board[r][3] == '--'):     # d-file
            if (not self.squareUnderAttack(r, 4) and  # e-file (king)
            not self.squareUnderAttack(r, 3) and   # d-file
            not self.squareUnderAttack(r, 2)):     # c-file
                if (self.white_to_move and self.white_castle_queenside) or \
                (not self.white_to_move and self.black_castle_queenside):
                    if self.board[r][0][1] == 'R':  # a-file rook
                        moves.append(Move((r, 4), (r, 2), self.board, isCastleMove=True))



class Move():
    ranks_to_rows = {'1':7, '2':6, '3':5, '4':4,
                     '5':3, '6':2, '7':1, '8':0}
    rows_to_ranks = {v:k for k,v in ranks_to_rows.items()}
    files_to_cols = {'a':0, 'b':1, 'c':2, 'd':3,
                     'e':4, 'f':5, 'g':6, 'h':7}
    cols_to_files = {v:k for k,v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, isEnpassantMove=False,isCastleMove=False, promotion_choice='Q' ):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.isCastleMove = isCastleMove
        # Pawn promotion
        self.isPawnPromotion = (self.piece_moved == 'wp' and self.end_row == 0) or \
                              (self.piece_moved == 'bp' and self.end_row == 7)
        self.promotion_choice = promotion_choice
        
        # En passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.piece_captured = 'bp' if self.piece_moved == 'wp' else 'wp'
            
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other):
        if isinstance(other, Move):
            return (self.start_row == other.start_row and 
                    self.start_col == other.start_col and
                    self.end_row == other.end_row and
                    self.end_col == other.end_col and
                    self.piece_moved == other.piece_moved)
        return False

    def getChessNotation(self):
        # Castling
        if self.isCastleMove:
            return "O-O" if self.end_col > self.start_col else "O-O-O"
        
        piece = self.piece_moved[1]
        notation = ""
        
        # Piece notation (except pawns)
        if piece != 'p':
            notation += piece.upper()
        
        # Capture indicator
        if self.piece_captured != '--':
            if piece == 'p':
                notation += self.cols_to_files[self.start_col]  # Pawn captures include file
            notation += 'x'
        
        # Destination square
        notation += self.getRankFile(self.end_row, self.end_col)
        
        # Promotion
        if self.isPawnPromotion:
            notation += f"={self.promotion_choice.upper()}"
        
        return notation

    def getRankFile(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]