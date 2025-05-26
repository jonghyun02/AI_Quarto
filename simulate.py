# simulate_quarto.py

import numpy as np
import sys, os, time, random
import pandas as pd

# 1) 모듈 로드 경로 추가
sys.path.append(os.path.dirname(__file__))  # 현재 스크립트 폴더

import machines_p1 as m1
import machines_p2 as m2

# 2) P2의 sleep 제거, 디버그 출력 억제
time.sleep = lambda *_: None
import builtins
builtins_print = builtins.print
builtins.print = lambda *a, **k: None  # 모든 print 무시

# 3) MCTS search_actions 안전 패치 (자식 노드가 없을 때 랜덤 fallback)
orig_search = m1.MCTS.search_actions
def safe_search(self, for_place=False):
    try:
        return orig_search(self, for_place=for_place)
    except ValueError:
        if for_place:
            moves = m1.get_place_actions(self.root_board)
            return random.choice(moves)
        else:
            return random.choice(self.root_available)
m1.MCTS.search_actions = safe_search

# 4) P1을 빠르게 돌리기 위한 파생 클래스 (time_budget=0.001)
class P1Fast(m1.P1):
    def select_piece(self):
        return m1.MCTS(self.board, self.available_pieces, time_budget=0.001).search_actions(for_place=False)
    def place_piece(self, selected_piece):
        return m1.MCTS(self.board, self.available_pieces,
                       current_piece=selected_piece,
                       time_budget=0.001).search_actions(for_place=True)

# P2는 sleep 제거만 된 버전 사용
class P2Fast(m2.P2):
    pass

P1Class = P1Fast
P2Class = P2Fast

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
    for _ in range(1000):
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
