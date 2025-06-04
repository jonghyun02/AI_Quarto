import random
import numpy as np
import time
from joblib import Parallel, delayed, cpu_count
from numba import njit

from machines_p2 import P2
from machines_p1 import P1

TF = (0, 1)
ITERATIONS = 100  # 더 빠르니 늘려도 됨

@njit
def check_group_numba(group):
    # Numba용 순수 numpy 배열만 허용
    has_zero = False
    for x in group:
        if x == 0:
            has_zero = True
            break
    if has_zero:
        return False
    for i in range(4):
        val = (group[0] - 1) & (1 << i)
        same = True
        for x in group:
            if ((x - 1) & (1 << i)) != val:
                same = False
                break
        if same:
            return True
    return False

@njit
def check_win_numba(board):
    # 행, 열
    for i in range(4):
        if check_group_numba(board[i, :]) or check_group_numba(board[:, i]):
            return True
    # 대각선
    if check_group_numba(np.array([board[i, i] for i in range(4)])):
        return True
    if check_group_numba(np.array([board[i, 3 - i] for i in range(4)])):
        return True
    # 2x2
    for i in range(3):
        for j in range(3):
            sub = np.array([board[i, j], board[i, j+1], board[i+1, j], board[i+1, j+1]])
            if check_group_numba(sub):
                return True
    return False

def simulate_game(idx):
    random.seed(time.time() + idx)  # 병렬일 때 seed 충돌 방지

    players = [P1, P2]
    board = np.zeros((4, 4), dtype=np.int32)  # numba는 int32로 맞추는 게 안전
    pieces = [(i, j, k, l) for i in TF for j in TF for k in TF for l in TF]
    available_pieces = pieces[:]

    for turn in range(16):
        p1, p2 = players[turn % 2](board.copy(), available_pieces[:]), players[(turn + 1) % 2](board.copy(), available_pieces[:])
        selected_piece = p2.select_piece()
        r, c = p1.place_piece(selected_piece)
        available_pieces.remove(selected_piece)
        board[r, c] = pieces.index(selected_piece) + 1
        # --- numba를 위해 numpy 배열로 넘김
        if check_win_numba(board):
            return turn % 2
    return 2

def show_result(r):
    print(f"{ITERATIONS} games played.")
    print(f"P1 win: {r[0]}, P2 win: {r[1]}, Draw: {r[2]}")

if __name__ == "__main__":
    start = time.time()
    results = Parallel(n_jobs=cpu_count())(delayed(simulate_game)(i) for i in range(ITERATIONS))
    result = [results.count(0), results.count(1), results.count(2)]
    show_result(result)
    print(f"Time elapsed: {time.time()-start:.2f}s")
