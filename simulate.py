# Updated simulate_quarto.py (no time limits for both P1 and P2)

import numpy as np
import sys, os, time, random
import pandas as pd

# 1) 모듈 로드 경로 추가
sys.path.append(os.path.dirname(__file__))

import machines_p1 as m1
import machines_p2 as m2

# 2) sleep 제거, 디버그 출력 억제
time.sleep = lambda *_: None
import builtins
builtins_print = builtins.print
builtins.print = lambda *a, **k: None  # 모든 print 무시



# 4) P1과 P2 모두 원본 클래스 사용 (시간 제한 없음)
P1Class = m1.P1
P2Class = m2.P2

def simulate_game():
    board = np.zeros((4,4), dtype=int)
    available_pieces = m1.pieces.copy()
    turn = 1
    
    while True:
        # 조각 선택 (상대가 선택)
        selector = P2Class(board, available_pieces) if turn==1 else P1Class(board, available_pieces)
        piece = selector.select_piece()
        
        # 조각 배치 (현재 플레이어)
        placer = P1Class(board, available_pieces) if turn==1 else P2Class(board, available_pieces)
        r, c = placer.place_piece(piece)
        
        board[r, c] = m1.pieces.index(piece) + 1
        available_pieces.remove(piece)
        
        if m1.check_win(board):
            return turn
        if not available_pieces:
            return 0  # 무승부
        
        turn = 3 - turn

def main():
    results = {'P1 wins':0, 'P2 wins':0, 'Draws':0}
    for _ in range(100):
        outcome = simulate_game()
        if outcome == 1:
            results['P1 wins'] += 1
        elif outcome == 2:
            results['P2 wins'] += 1
        else:
            results['Draws'] += 1

    # 출력 복원
    builtins.print = builtins_print

    # 결과 출력
    df = pd.DataFrame([results])
    print("=== 1000 Games Simulation Results ===")
    print(df.to_string(index=False))
    total = sum(results.values())
    print(f"P1 win rate: {results['P1 wins']/total*100:.1f}%")
    print(f"P2 win rate: {results['P2 wins']/total*100:.1f}%")
    print(f"Draw rate: {results['Draws']/total*100:.1f}%")

if __name__ == "__main__":
    main()
