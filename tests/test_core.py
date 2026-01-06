from othello import core

def test_create_initial_state():
    """
    初期状態が正しく生成されるかテストする
    - 盤面の中央に白黒2つずつの石が配置されていること
    - 現在のプレイヤーが黒であること
    - ゲームが終了していないこと
    """
    initial_state = core.create_initial_state()

    # プレイヤーは黒から始まる
    assert initial_state.current_player == "Black"
    assert not initial_state.game_over

    # 初期盤面の検証
    board = initial_state.board
    assert board[3][3] == "White"
    assert board[4][4] == "White"
    assert board[3][4] == "Black"
    assert board[4][3] == "Black"

    # 中央4マス以外のマスがすべて空であることの検証
    empty_squares = 0
    for r in range(8):
        for c in range(8):
            if board[r][c] is None:
                empty_squares += 1
    assert empty_squares == 60


def test_find_flippable_stones():
    """
    指定した位置に石を置いた場合に裏返せる石のリストが正しく取得できるかテストする
    """
    # FS-001: 初期盤面で黒が(3, 2) (c4) に置いた場合、(3, 3) (d4) の白石が裏返るはず
    initial_state = core.create_initial_state()
    flippable = core._find_flippable_stones(initial_state.board, "Black", (3, 2))
    assert flippable == [(3, 3)]

    # FS-004: 初期盤面で黒が(0, 0)に置いても何も裏返らない
    flippable_none = core._find_flippable_stones(initial_state.board, "Black", (0, 0))
    assert flippable_none == []


def test_is_valid_move():
    """
    石を置けるかどうかの判定が正しく行われるかテストする
    """
    initial_state = core.create_initial_state()
    board = initial_state.board

    # VM-001: 黒の有効な手 (c4)
    assert core.is_valid_move(board, "Black", (3, 2)) is True

    # VM-003: 既に石が置かれているマスは無効
    assert core.is_valid_move(board, "Black", (3, 3)) is False

    # VM-004: 相手の石を挟めないマスは無効
    assert core.is_valid_move(board, "Black", (0, 0)) is False


def test_handle_move():
    """
    手を処理し、新しいゲーム状態を返す機能が正しく動作するかテストする
    """
    initial_state = core.create_initial_state()

    # HM-001: 正常な手 (c4) を処理
    new_state = core.handle_move(initial_state, (3, 2))

    # - 石が正しく裏返っているか
    assert new_state.board[3][3] == "Black"
    # - 新しく石が置かれているか
    assert new_state.board[3][2] == "Black"
    # - プレイヤーが交代しているか
    assert new_state.current_player == "White"
    # - エラーメッセージがないこと
    assert new_state.message == ""

    # HM-002: 無効な手 (a1) を処理
    invalid_state = core.handle_move(initial_state, (0, 0))

    # - 盤面が変化していないか
    assert invalid_state.board == initial_state.board
    # - プレイヤーが交代していないか
    assert invalid_state.current_player == "Black"
    # - エラーメッセージが設定されているか
    assert "Invalid move" in invalid_state.message


def test_check_game_over():
    """
    ゲーム終了判定が正しく行われるかテストする
    """
    # GO-003: 盤面が埋まり、黒の勝ちでゲーム終了する盤面を準備
    board_black_wins_list = [["Black"] * 5 + ["White"] * 3] * 8
    board_black_wins = tuple(tuple(row) for row in board_black_wins_list)

    state_black_wins = core.GameState(
        board=board_black_wins,
        current_player="Black"
    )

    final_state = core.check_game_over(state_black_wins)
    assert final_state.game_over is True
    assert final_state.winner == "Black"

    # GO-005: 引き分けでゲーム終了する盤面
    board_draw_list = [["Black"] * 4 + ["White"] * 4] * 8
    board_draw = tuple(tuple(row) for row in board_draw_list)
    state_draw = core.GameState(board=board_draw, current_player="Black")
    final_state_draw = core.check_game_over(state_draw)
    assert final_state_draw.game_over is True
    assert final_state_draw.winner is None
