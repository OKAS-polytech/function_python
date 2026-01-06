from typing import Tuple, Optional, Literal, NamedTuple

# ----------------------------------------------------------------
# データ構造 (Model)
# ----------------------------------------------------------------

# プレイヤーと石の状態をリテラル型で定義
Player = Literal["Black", "White"]

# 石の状態 (空きマスはNone)
Stone = Optional[Player]

# 盤面 (8x8のタプルのタプルでイミュータブル)
Board = Tuple[Tuple[Stone, ...], ...]

# ゲームの状態全体を表すイミュータブルなデータ構造
class GameState(NamedTuple):
    """
    ゲームの状態を表す。すべての属性は不変。
    - board: 盤面の状態
    - current_player: 現在のターンプレイヤー
    - game_over: ゲームが終了したかどうか
    - winner: 勝者 (ゲーム終了時のみ)
    - message: ユーザーへのメッセージ (エラー等)
    """
    board: Board
    current_player: Player
    game_over: bool = False
    winner: Optional[Player] = None
    message: str = ""


# ----------------------------------------------------------------
# 純粋関数 (Update)
# ----------------------------------------------------------------

def create_initial_state() -> GameState:
    """
    ゲーム開始時の初期状態を生成する純粋関数。
    """
    # まずミュータブルなリストとして盤面を構築
    board_list = [[None for _ in range(8)] for _ in range(8)]

    # オセロの初期配置
    board_list[3][3] = "White"
    board_list[4][4] = "White"
    board_list[3][4] = "Black"
    board_list[4][3] = "Black"

    # イミュータブルなタプルのタプルに変換
    board: Board = tuple(tuple(row) for row in board_list)

    # 初期GameStateを生成して返す
    return GameState(
        board=board,
        current_player="Black",
        game_over=False
    )


def _find_flippable_stones(board: Board, player: Player, position: Tuple[int, int]) -> list[Tuple[int, int]]:
    """
    指定した位置に石を置いた場合に裏返せる相手の石の座標リストを返す純粋関数。
    裏返せる石がない場合は空のリストを返す。

    :param board: 盤面
    :param player: 石を置くプレイヤー
    :param position: 石を置く位置 (row, col)
    :return: 裏返せる石の座標のリスト
    """
    row, col = position
    opponent = "White" if player == "Black" else "Black"

    # 8方向 (dr, dc)
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
            else: # 空マス or 盤面外
                break

    return flippable_stones


def is_valid_move(board: Board, player: Player, position: Tuple[int, int]) -> bool:
    """
    指定された位置が、そのプレイヤーにとって有効な手であるかを判定する純粋関数。
    """
    row, col = position

    # 盤面の範囲外かチェック
    if not (0 <= row < 8 and 0 <= col < 8):
        return False

    # マスが空であるかチェック
    if board[row][col] is not None:
        return False

    # 相手の石を1つ以上裏返せるかチェック
    if not _find_flippable_stones(board, player, position):
        return False

    return True


def handle_move(state: GameState, position: Tuple[int, int]) -> GameState:
    """
    プレイヤーの指し手を処理し、新しいGameStateを返す純粋関数。
    """
    player = state.current_player
    board = state.board

    # 1. 有効な手か検証
    if not is_valid_move(board, player, position):
        return state._replace(message="Invalid move. Please try again.")

    # 2. 石を裏返す
    flippable_stones = _find_flippable_stones(board, player, position)

    # ミュータブルなリストに変換して更新
    new_board_list = [list(row) for row in board]

    # 新しい石を置く
    row, col = position
    new_board_list[row][col] = player

    # 石を裏返す
    for r, c in flippable_stones:
        new_board_list[r][c] = player

    # イミュータブルな盤面に戻す
    new_board = tuple(tuple(row) for row in new_board_list)

    # 3. プレイヤーを交代
    next_player = "White" if player == "Black" else "Black"

    # 4. プレイヤー交代とゲーム終了判定
    next_player = "White" if player == "Black" else "Black"

    # 新しい盤面で次のプレイヤーが手番を持つか確認
    if _has_any_valid_move(new_board, next_player):
        # 次のプレイヤーに手があれば、通常通り交代
        state_after_move = GameState(board=new_board, current_player=next_player)
    elif _has_any_valid_move(new_board, player):
        # 次のプレイヤーに手がなく、現在のプレイヤーに手があれば、パス
        state_after_move = GameState(board=new_board, current_player=player, message=f"{next_player} has no valid moves. Turn passed.")
    else:
        # どちらのプレイヤーにも手がなければ、初期状態として仮置き
        state_after_move = GameState(board=new_board, current_player=next_player)

    # 5. ゲーム終了判定を呼び出す
    return check_game_over(state_after_move)


def _has_any_valid_move(board: Board, player: Player) -> bool:
    """
    指定されたプレイヤーに、少なくとも1つの有効な手があるかどうかを判定する。
    """
    for r in range(8):
        for c in range(8):
            if is_valid_move(board, player, (r, c)):
                return True
    return False


def check_game_over(state: GameState) -> GameState:
    """
    ゲームが終了したかどうかを判定し、終了していれば勝者を決定する。
    """
    player = state.current_player
    opponent = "White" if player == "Black" else "Black"

    # 両プレイヤーに有効な手がない場合、ゲーム終了
    if not _has_any_valid_move(state.board, player) and not _has_any_valid_move(state.board, opponent):
        black_score = sum(row.count("Black") for row in state.board)
        white_score = sum(row.count("White") for row in state.board)

        winner: Optional[Player] = None
        if black_score > white_score:
            winner = "Black"
        elif white_score > black_score:
            winner = "White"

        return state._replace(game_over=True, winner=winner)

    # ゲームが続く場合は、元の状態を返す
    return state
