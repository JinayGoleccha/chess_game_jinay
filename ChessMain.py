import os
import pygame as p
import ChessEngine
from SmartMoveFinder import findBestMove, findRandomMove
import time
import math

WIDTH = HEIGHT = 750
PANEL_WIDTH = 300   # Side panel width
SCREEN_WIDTH = WIDTH + PANEL_WIDTH  # Total window width
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 60
IMAGES = {}

def loadImages():
    try:
        SCALE_FACTOR = 0.8
        image_folder = os.path.join(os.path.dirname(__file__), 'images')
        
        pieces = ['wp','wR','wN','wB','wQ','wK','bp','bR','bN','bB','bK','bQ']
        for piece in pieces:
            image_path = os.path.join(image_folder, f"{piece}.png")
            IMAGES[piece] = p.transform.scale(p.image.load(image_path), 
                            (int(SQ_SIZE * SCALE_FACTOR), int(SQ_SIZE * SCALE_FACTOR)))
    except Exception as e:
        print(f"Error loading images: {e}")
        for piece in pieces:
            IMAGES[piece] = p.Surface((int(SQ_SIZE * SCALE_FACTOR), int(SQ_SIZE * SCALE_FACTOR)))
            color = p.Color('white') if piece[0] == 'w' else p.Color('black')
            IMAGES[piece].fill(color)
            font = p.font.SysFont('Arial', 24)
            text = font.render(piece[1], True, p.Color('red'))
            IMAGES[piece].blit(text, (10, 10))

def drawPiece(screen, piece, col, row):
    screen.blit(IMAGES[piece], 
               (col * SQ_SIZE + (SQ_SIZE - IMAGES[piece].get_width()) // 2,
                row * SQ_SIZE + (SQ_SIZE - IMAGES[piece].get_height()) // 2))

def main():
    p.init()
    screen = p.display.set_mode((SCREEN_WIDTH, HEIGHT))
    p.display.set_caption('Chess')
    clock = p.time.Clock()
    gs = ChessEngine.GameState()
    valid_moves = gs.getValidMoves()
    move_made = False
    loadImages()
    
    # Animation variables
    animating = False
    animation_move = None
    animation_start_time = 0
    animation_duration = 0.2  # seconds
    animation_start_pos = (0, 0)
    animation_piece = None
    current_x, current_y = 0, 0
    
    running = True
    sq_selected = ()
    player_clicks = []
    game_over = False
    promotion_pending = False
    promotion_move = None
    font = p.font.SysFont('Arial', 32)
    #Game mode flags
    playerOne = False # if human is playing white
    playerTwo = False # if human is playing black
    vs_computer = False
    buttons = {}
    moves_log = []
    
    while running:
        current_time = time.time()
        humanTurn = (gs.white_to_move and playerOne) or (not gs.white_to_move and playerTwo)
        
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            
            elif e.type == p.MOUSEBUTTONDOWN and not animating:
                location = p.mouse.get_pos()

                # Check side panel buttons
                if location[0] > WIDTH:
                    if buttons['reset'].collidepoint(location):
                        gs = ChessEngine.GameState()
                        valid_moves = gs.getValidMoves()
                        sq_selected = ()
                        player_clicks = []
                        game_over = False
                        promotion_pending = False
                        animating = False
                        moves_log = []
                    elif buttons['resign'].collidepoint(location):
                        winner = "White" if not gs.white_to_move else "Black"
                        if vs_computer and winner == "Black":
                            winner = "Computer"
                        game_over_text = f"{winner} wins by resignation!"
                        game_over = True
                        gs = ChessEngine.GameState()
                        valid_moves = gs.getValidMoves()
                        moves_log = []
                    elif buttons['computer'].collidepoint(location):
                        vs_computer = True
                        playerOne = True  # Human plays white by default
                        playerTwo = False
                    elif buttons['duo'].collidepoint(location):
                        vs_computer = False
                        playerOne = True
                        playerTwo = True
                    continue
                
                if not game_over and not promotion_pending and humanTurn:
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    
                    if sq_selected == (row, col):
                        sq_selected = ()
                        player_clicks = []
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)
                    
                    if len(player_clicks) == 2:
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                        for valid_move in valid_moves:
                            if (move.start_row == valid_move.start_row and 
                                move.start_col == valid_move.start_col and
                                move.end_row == valid_move.end_row and 
                                move.end_col == valid_move.end_col):
                                
                                if valid_move.isPawnPromotion:
                                    promotion_pending = True
                                    promotion_move = valid_move
                                elif valid_move.isCastleMove:  # Handle castling
                                    animating = True
                                    animation_move = valid_move
                                    animation_start_time = current_time
                                    animation_start_pos = (valid_move.start_col, valid_move.start_row)
                                    animation_piece = gs.board[valid_move.start_row][valid_move.start_col]
                                    gs.board[valid_move.start_row][valid_move.start_col] = '--'
                                else:
                                    # Regular move handling
                                    animating = True
                                    animation_move = valid_move
                                    animation_start_time = current_time
                                    animation_start_pos = (valid_move.start_col, valid_move.start_row)
                                    animation_piece = gs.board[valid_move.start_row][valid_move.start_col]
                                    gs.board[valid_move.start_row][valid_move.start_col] = '--'
                                
                                sq_selected = ()
                                player_clicks = []
                                break
                        else:
                            player_clicks = [sq_selected]
            
            elif e.type == p.KEYDOWN and not animating:
                if e.key == p.K_z and not promotion_pending and not game_over:
                    gs.undoMove()
                    if moves_log:
                        moves_log.pop()
                    move_made = True
                elif e.key == p.K_r:  # Reset game
                    gs = ChessEngine.GameState()
                    valid_moves = gs.getValidMoves()
                    sq_selected = ()
                    player_clicks = []
                    game_over = False
                    promotion_pending = False
                    animating = False
                
                elif promotion_pending and e.key in (p.K_q, p.K_r, p.K_b, p.K_n):
                    if e.key == p.K_q:
                        promotion_move.promotion_choice = 'Q'
                    elif e.key == p.K_r:
                        promotion_move.promotion_choice = 'R'
                    elif e.key == p.K_b:
                        promotion_move.promotion_choice = 'B'
                    elif e.key == p.K_n:
                        promotion_move.promotion_choice = 'N'
                    
                    gs.makeMove(promotion_move)
                    moves_log.append(promotion_move.getChessNotation())
                    move_made = True
                    promotion_pending = False
                    promotion_move = None
        
        # AI move logic
        if not animating and not game_over and not humanTurn and vs_computer:
            AImove = findBestMove(gs, valid_moves)
            if AImove not in valid_moves:
                AImove = findRandomMove(valid_moves)
            
            # Start animation
            animating = True
            animation_move = AImove
            animation_start_time = current_time
            animation_start_pos = (AImove.start_col, AImove.start_row)
            animation_piece = gs.board[AImove.start_row][AImove.start_col]
            gs.board[AImove.start_row][AImove.start_col] = '--'
                
        # Animation logic
        if animating:
            elapsed = current_time - animation_start_time
            if elapsed < animation_duration:
                # Calculate progress (0 to 1) with easing
                progress = elapsed / animation_duration
                progress = math.sin(progress * math.pi/2)  # Ease-in-out
                
                # Calculate current position
                start_x = animation_start_pos[0] * SQ_SIZE + SQ_SIZE//2
                start_y = animation_start_pos[1] * SQ_SIZE + SQ_SIZE//2
                end_x = animation_move.end_col * SQ_SIZE + SQ_SIZE//2
                end_y = animation_move.end_row * SQ_SIZE + SQ_SIZE//2
                
                current_x = start_x + (end_x - start_x) * progress
                current_y = start_y + (end_y - start_y) * progress
            else:
                # Animation complete - finalize move
                animating = False
                gs.makeMove(animation_move)
                moves_log.append(animation_move.getChessNotation())
                move_made = True
                if animation_piece[1] == 'K':  # If it was a king
                    if animation_piece[0] == 'w':
                        gs.white_king_loc = (animation_move.end_row, animation_move.end_col)
                    else:
                        gs.black_king_loc = (animation_move.end_row, animation_move.end_col)
        
        if move_made:
            valid_moves = gs.getValidMoves()
            move_made = False
        
        drawGameState(screen, gs, sq_selected, valid_moves, animating, animation_move, animation_piece, current_x, current_y)
        # Draw side panel and get buttons
        buttons = draw_side_panel(screen, gs, vs_computer, moves_log)
        
        if promotion_pending:
            drawPromotionMenu(screen)

        if game_over:
            drawEndGameText(screen, game_over_text)        
        elif gs.checkmate or gs.stalemate:
            game_over = True
            text = "Stalemate" if gs.stalemate else f"{'Black' if gs.white_to_move else 'White'} wins by checkmate!"
            drawEndGameText(screen, text)

        clock.tick(MAX_FPS)
        p.display.flip()


def draw_side_panel(screen, gs, vs_computer, moves_log):
    panel_rect = p.Rect(WIDTH, 0, PANEL_WIDTH, HEIGHT)
    p.draw.rect(screen, p.Color(240, 240, 240), panel_rect)  # Light gray background
    
    # Font setup
    title_font = p.font.SysFont('Arial', 24, bold=True)
    button_font = p.font.SysFont('Arial', 18)
    small_font = p.font.SysFont('Arial', 16)
    
    buttons = {}
    y_pos = 20  # Starting Y position
    
    # 1. Title Section
    title = title_font.render("Chess Game", True, p.Color('black'))
    screen.blit(title, (WIDTH + (PANEL_WIDTH - title.get_width())//2, y_pos))
    y_pos += 50
    
    # 2. Action Buttons (45px height)
    btn_height = 45
    btn_width = PANEL_WIDTH - 40
    
    # Reset Button
    reset_rect = p.Rect(WIDTH + 20, y_pos, btn_width, btn_height)
    p.draw.rect(screen, p.Color('white'), reset_rect, border_radius=5)
    p.draw.rect(screen, p.Color('black'), reset_rect, 2, border_radius=5)
    reset_text = button_font.render("Reset Game", True, p.Color('black'))
    screen.blit(reset_text, (reset_rect.centerx - reset_text.get_width()//2, 
                           reset_rect.centery - reset_text.get_height()//2))
    buttons['reset'] = reset_rect
    y_pos += btn_height + 15
    
    # Resign Button
    resign_rect = p.Rect(WIDTH + 20, y_pos, btn_width, btn_height)
    p.draw.rect(screen, p.Color(255, 200, 200), resign_rect, border_radius=5)  # Light red
    p.draw.rect(screen, p.Color('black'), resign_rect, 2, border_radius=5)
    resign_text = button_font.render("Resign", True, p.Color('black'))
    screen.blit(resign_text, (resign_rect.centerx - resign_text.get_width()//2, 
                            resign_rect.centery - resign_text.get_height()//2))
    buttons['resign'] = resign_rect
    y_pos += btn_height + 30
    
    # 3. Game Mode Section
    mode_header = button_font.render("Game Mode", True, p.Color('dark blue'))
    screen.blit(mode_header, (WIDTH + 20, y_pos))
    y_pos += 30
    
    # Current Mode Indicator
    current_mode = "VS Computer" if vs_computer else "Two Players"
    mode_text = small_font.render(f"Current: {current_mode}", True, p.Color('black'))
    screen.blit(mode_text, (WIDTH + 20, y_pos))
    y_pos += 30
    
    # Mode Selection Buttons (40px height)
    mode_btn_height = 40
    
    # VS Computer Button
    computer_rect = p.Rect(WIDTH + 20, y_pos, btn_width, mode_btn_height)
    btn_color = p.Color(200, 230, 200) if vs_computer else p.Color('white')
    p.draw.rect(screen, btn_color, computer_rect, border_radius=5)
    p.draw.rect(screen, p.Color('black'), computer_rect, 2, border_radius=5)
    computer_text = small_font.render("VS Computer", True, p.Color('black'))
    screen.blit(computer_text, (computer_rect.centerx - computer_text.get_width()//2, 
                              computer_rect.centery - computer_text.get_height()//2))
    buttons['computer'] = computer_rect
    y_pos += mode_btn_height + 10
    
    # Two Players Button
    duo_rect = p.Rect(WIDTH + 20, y_pos, btn_width, mode_btn_height)
    btn_color = p.Color(200, 230, 200) if not vs_computer else p.Color('white')
    p.draw.rect(screen, btn_color, duo_rect, border_radius=5)
    p.draw.rect(screen, p.Color('black'), duo_rect, 2, border_radius=5)
    duo_text = small_font.render("Two Players", True, p.Color('black'))
    screen.blit(duo_text, (duo_rect.centerx - duo_text.get_width()//2, 
                         duo_rect.centery - duo_text.get_height()//2))
    buttons['duo'] = duo_rect
    y_pos += mode_btn_height + 30
    
    # 4. Moves History Section
    moves_header = button_font.render("Moves History", True, p.Color('dark blue'))
    screen.blit(moves_header, (WIDTH + 20, y_pos))
    y_pos += 30
    
    # Moves Display Area
    moves_rect = p.Rect(WIDTH + 20, y_pos, btn_width, HEIGHT - y_pos - 20)
    p.draw.rect(screen, p.Color('white'), moves_rect, border_radius=5)
    p.draw.rect(screen, p.Color('black'), moves_rect, 2, border_radius=5)
    
    # Display moves
    line_height = 20
    padding = 8
    max_lines = (moves_rect.height - 2*padding) // line_height
    
    for i, move in enumerate(moves_log[-max_lines:]):
        text = small_font.render(move, True, p.Color('black'))
        screen.blit(text, (moves_rect.x + padding, 
                         moves_rect.y + padding + i*line_height))
    
    return buttons

def drawBoard(screen):
    colors = [p.Color("white"), p.Color("light green")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawGameState(screen, gs, sq_selected, valid_moves, animating=False, animation_move=None, animation_piece=None, current_x=0, current_y=0):
    drawBoard(screen)
    highlightSquares(screen, gs, sq_selected, valid_moves)
    
    # Draw all pieces except the one being animated
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = gs.board[r][c]
            if piece != "--":
                if not animating or (r != animation_move.start_row or c != animation_move.start_col):
                    drawPiece(screen, piece, c, r)
    
    # Draw the moving piece on top if animating
    if animating and animation_piece:
        piece_img = IMAGES[animation_piece]
        screen.blit(piece_img, 
                   (current_x - piece_img.get_width()//2, 
                    current_y - piece_img.get_height()//2))

def highlightSquares(screen, gs, sq_selected, valid_moves):
    if sq_selected:
        r, c = sq_selected
        if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'):
            # Highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            
            # Highlight valid moves
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    end_r, end_c = move.end_row, move.end_col
                    # Special highlight for castling
                    if move.isCastleMove:
                        if end_c > c:  # Kingside
                            screen.blit(s, ((end_c+1) * SQ_SIZE, end_r * SQ_SIZE))
                        else:  # Queenside
                            screen.blit(s, ((end_c-1) * SQ_SIZE, end_r * SQ_SIZE))
                    screen.blit(s, (end_c * SQ_SIZE, end_r * SQ_SIZE))

def drawPromotionMenu(screen):
    menu = p.Surface((WIDTH // 2, HEIGHT // 4))
    menu.fill(p.Color('white'))
    font = p.font.SysFont('Arial', 32)
    
    text = font.render("Promote to: Q (Queen), R (Rook), B (Bishop), N (Knight)", True, p.Color('black'))
    menu.blit(text, (10, 10))
    
    screen.blit(menu, (WIDTH // 4, HEIGHT // 2 - HEIGHT // 8))

def drawEndGameText(screen, text):
    # Dark overlay
    s = p.Surface((WIDTH, HEIGHT), p.SRCALPHA)
    s.fill((0, 0, 0, 180))  # Semi-transparent black
    screen.blit(s, (0, 0))
    
    # Text with border
    font = p.font.SysFont('Helvetica', 40, True)
    text_surface = font.render(text, True, p.Color('white'))
    text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
    
    # Text background
    p.draw.rect(screen, p.Color('dark green'), 
               (text_rect.x-10, text_rect.y-10, 
                text_rect.width+20, text_rect.height+20))
    
    screen.blit(text_surface, text_rect)

if __name__ == "__main__":
    main()