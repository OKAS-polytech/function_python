import time
from othello.use_cases import game_logic as core
from othello.entities.game import GameState

def render_view(state: core.GameState) -> str:
    """
    現在のゲーム状態を受け取り、CUI表示用の文字列を生成する純粋関数。
    """
    # 石のシンボルマッピング
    symbols = {
        "Black": "●",
        "White": "○",
        None: "."
    }

    # スコア計算
    black_score = sum(row.count("Black") for row in state.board)
    white_score = sum(row.count("White") for row in state.board)

    # CUI表示を構築
    lines = []
    # ヘッダー (a-h)
    lines.append("  a b c d e f g h")

    # 盤面
    for i, row in enumerate(state.board):
        line = f"{i + 1} " + " ".join(symbols[stone] for stone in row)
        lines.append(line)

    lines.append("") # 空行

    # ゲームオーバー時の表示
    if state.game_over:
        lines.append("Game Over!")
        if state.winner:
            lines.append(f"Winner: {state.winner} ({symbols[state.winner]})")
        else:
            lines.append("Draw!")
        lines.append(f"Final Score: Black {black_score}, White {white_score}")
    # ゲーム中の表示
    else:
        player_symbol = symbols[state.current_player]
        lines.append(f"Turn: {state.current_player} ({player_symbol})")
        lines.append(f"Score: Black {black_score}, White {white_score}")

    # ユーザーへのメッセージ (エラーなど)
    if state.message:
        lines.append(state.message)

    # ヒントの表示
    if state.show_hints:
        valid_moves = core.get_valid_moves(state)
        if valid_moves:
            formatted_moves = ", ".join([format_position(pos) for pos in valid_moves])
            lines.append(f"Hint: Valid moves are {formatted_moves}")
        else:
            lines.append("Hint: No valid moves available.")

    return "\n".join(lines)

from typing import Optional, Tuple

def format_position(position: Tuple[int, int]) -> str:
    """座標タプルを "a1" 形式の文字列に変換する。"""
    row, col = position
    return f"{chr(ord('a') + col)}{row + 1}"

def parse_move_input(user_input: str) -> Optional[Tuple[int, int]]:
    """
    ユーザーの入力文字列 ("c4"など) を座標タプル ((3, 2)など) に変換する。
    無効な入力の場合はNoneを返す。
    """
    user_input = user_input.lower().strip()
    if len(user_input) != 2:
        return None

    col_char, row_char = user_input[0], user_input[1]

    if not ('a' <= col_char <= 'h' and '1' <= row_char <= '8'):
        return None

    col = ord(col_char) - ord('a')
    row = int(row_char) - 1

    return (row, col)


def setup_game() -> GameState:
    """ゲーム開始前にモード選択などを行う。"""
    print("Welcome to CUI Othello!")

    # モード選択
    while True:
        mode = input("Select game mode: (1) Player vs Player (2) Player vs Computer\n> ").strip()
        if mode in ["1", "2"]:
            break
        print("Invalid input. Please enter 1 or 2.")

    initial_state = core.create_initial_state()

    if mode == "1":
        return initial_state._replace(game_mode="PVP")
    else:
        # コンピュータの担当色選択
        while True:
            color = input("Select your color: (1) Black (2) White\n> ").strip().lower()
            if color in ["1", "b", "black"]:
                computer_player = "White"
                break
            elif color in ["2", "w", "white"]:
                computer_player = "Black"
                break
            print("Invalid input.")
        return initial_state._replace(game_mode="PVC", computer_player=computer_player)

def game_loop():
    """
    ゲームのメインループ。
    副作用(print, input) はこの関数に集約する。
    """
    state = setup_game()

    while True:
        # 1. View: 現在の状態を描画
        print(render_view(state))

        # 2. ゲーム終了判定
        if state.game_over:
            break

        # 3. ターンに応じた処理
        if state.game_mode == "PVC" and state.current_player == state.computer_player:
            # コンピュータのターン
            print(f"Computer ({state.current_player}) is thinking...")
            time.sleep(1) # 思考しているように見せる

            position = core.find_best_move(state)
            if position:
                print(f"Computer plays {format_position(position)}")
                state = core.handle_move(state, position)
            else:
                # コンピュータがパスする場合（基本的にはゲーム終了時のみ）
                state = core.handle_move(state, None) # パスをハンドル（将来的な拡張用）
        else:
            # 人間のプレイヤーのターン
            state = handle_human_player_turn(state)


def handle_human_player_turn(state: GameState) -> GameState:
    """人間のプレイヤーの入力を処理し、新しい状態を返す。"""
    prompt = f"Enter your move ('h' for hint, e.g., c4) ({state.current_player}): "
    user_input = input(prompt).strip().lower()

    if user_input in ['h', 'hint']:
        return state._replace(show_hints=True, message="")

    position = parse_move_input(user_input)

    state_after_input = state._replace(show_hints=False)

    if position is None:
        return state_after_input._replace(message=f"Invalid input format '{user_input}'. Please use 'a1'-'h8'.")
    else:
        return core.handle_move(state_after_input, position)


if __name__ == "__main__":
    game_loop()
