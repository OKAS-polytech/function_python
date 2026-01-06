from othello import core

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

    return "\n".join(lines)

from typing import Optional, Tuple

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


def game_loop():
    """
    ゲームのメインループ。
    副作用(print, input) はこの関数に集約する。
    """
    state = core.create_initial_state()

    while True:
        # 1. View: 現在の状態を描画
        print(render_view(state))

        # 2. ゲーム終了判定
        if state.game_over:
            break

        # 3. Input: ユーザーからの入力を受け取り、Update: 新しい状態を生成する
        prompt = f"Enter your move ({state.current_player}): "
        user_input = input(prompt)

        position = parse_move_input(user_input)

        if position is None:
            # 不正な入力形式の場合
            state = state._replace(message=f"Invalid input format '{user_input}'. Please use 'a1'-'h8'.")
        else:
            # コアロジックを呼び出して状態を更新
            state = core.handle_move(state, position)


if __name__ == "__main__":
    game_loop()
