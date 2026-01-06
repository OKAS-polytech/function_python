from typing import Tuple, Optional
from othello.entities.game import Board, GameState, Player, Stone

# このファイルは、アプリケーション固有のビジネスルール（ユースケース）を実装します。

def create_initial_state() -> GameState:
    """
    ゲーム開始時の初期状態を生成する純粋関数。
    """
    board_list = [[None for _ in range(8)] for _ in range(8)]
    board_list[3][3] = "White"
    board_list[4][4] = "White"
    board_list[3][4] = "Black"
    board_list[4][3] = "Black"
    board: Board = tuple(tuple(row) for row in board_list)
    return GameState(
        board=board,
        current_player="Black",
        game_over=False
    )

def _find_flippable_stones(board: Board, player: Player, position: Tuple[int, int]) -> list[Tuple[int, int]]:
    row, col = position
    opponent = "White" if player == "Black" else "Black"
    DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    flippable_stones = []
    for dr, dc in DIRECTIONS:
        stones_in_direction = []
        r, c = row + dr, col + dc
        while 0 <= r < 8 and 0 <= c < 8:
            if board[r][c] == opponent:
                stones_in_direction.append((r, c))
                r, c = r + dr, c + dc
            elif board[r][c] == player:
                flippable_stones.extend(stones_in_direction)
                break
            else:
                break
    return flippable_stones

def is_valid_move(board: Board, player: Player, position: Tuple[int, int]) -> bool:
    row, col = position
    if not (0 <= row < 8 and 0 <= col < 8):
        return False
    if board[row][col] is not None:
        return False
    if not _find_flippable_stones(board, player, position):
        return False
    return True

def handle_move(state: GameState, position: Optional[Tuple[int, int]]) -> GameState:
    """
    プレイヤーの指し手（またはパス）を処理し、新しいGameStateを返す純粋関数。
    この関数の最後で必ずゲーム終了判定が呼び出される。
    """
    player = state.current_player
    board = state.board

    new_board = board
    state_after_move: GameState

    if position is not None:
        # 通常の指し手
        if not is_valid_move(board, player, position):
            return state._replace(message="Invalid move. Please try again.")

        flippable_stones = _find_flippable_stones(board, player, position)
        new_board_list = [list(row) for row in board]
        row, col = position
        new_board_list[row][col] = player
        for r, c in flippable_stones:
            new_board_list[r][c] = player
        new_board = tuple(tuple(row) for row in new_board_list)

    # ターン交代ロジック
    next_player = "White" if player == "Black" else "Black"

    if _has_any_valid_move(new_board, next_player):
        # 次のプレイヤーに手があれば、通常通り交代
        state_after_move = state._replace(board=new_board, current_player=next_player, message="")
    elif _has_any_valid_move(new_board, player):
        # 次のプレイヤーに手がなく、現在のプレイヤーに手があれば、パス
        message = f"{next_player} has no valid moves. Turn passed."
        if position is None: # 既にパスしている場合、メッセージを重ねない
             message = f"{player} passed again."
        state_after_move = state._replace(board=new_board, current_player=player, message=message)
    else:
        # どちらのプレイヤーにも手がなければ、ゲーム終了に向かう
        state_after_move = state._replace(board=new_board, current_player=next_player)

    return check_game_over(state_after_move)

def _has_any_valid_move(board: Board, player: Player) -> bool:
    for r in range(8):
        for c in range(8):
            if is_valid_move(board, player, (r, c)):
                return True
    return False

def check_game_over(state: GameState) -> GameState:
    player = state.current_player
    opponent = "White" if player == "Black" else "Black"
    if not _has_any_valid_move(state.board, player) and not _has_any_valid_move(state.board, opponent):
        black_score = sum(row.count("Black") for row in state.board)
        white_score = sum(row.count("White") for row in state.board)
        winner: Optional[Player] = None
        if black_score > white_score:
            winner = "Black"
        elif white_score > black_score:
            winner = "White"
        return state._replace(game_over=True, winner=winner)
    return state


def get_valid_moves(state: GameState) -> list[Tuple[int, int]]:
    """
    現在のプレイヤーが石を置けるすべての有効な手の座標リストを返す。
    """
    board = state.board
    player = state.current_player
    valid_moves = []
    for r in range(8):
        for c in range(8):
            if is_valid_move(board, player, (r, c)):
                valid_moves.append((r, c))
    return valid_moves


def find_best_move(state: GameState) -> Optional[Tuple[int, int]]:
    """
    コンピュータプレイヤーのための思考ルーチン。
    最も多くの石を裏返せる手を探索し、その座標を返す。
    有効な手がない場合はNoneを返す。
    """
    board = state.board
    player = state.current_player
    valid_moves = get_valid_moves(state)

    if not valid_moves:
        return None

    # 各手のスコア（裏返せる石の数）を計算
    move_scores = {}
    for move in valid_moves:
        num_flipped = len(_find_flippable_stones(board, player, move))
        move_scores[move] = num_flipped

    # 最高スコアの手を返す
    return max(move_scores, key=move_scores.get)
