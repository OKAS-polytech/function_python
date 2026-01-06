from typing import Tuple, Optional, Literal, NamedTuple

# ----------------------------------------------------------------
# データ構造 (Entities)
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
    show_hints: bool = False
    game_mode: Literal["PVP", "PVC"] = "PVP"  # Player vs Player, Player vs Computer
    computer_player: Optional[Player] = None
