    def simulate(self):
        sim_board  = self.board.copy()
        sim_avail  = self.available_pieces.copy()
        sim_piece  = self.current_piece
        player     = self.current_player

        # ── 간단한 휴리스틱: 한 줄마다 남은 빈칸이 많을수록 승리 기회 ↑ ──
        def line_potential(bd, pl):
            if sim_piece is None:
                return 0
            lines = []
            # 행/열
            lines += [list(bd[r,:]) for r in range(4)]
            lines += [list(bd[:,c]) for c in range(4)]
            # 대각선
            lines += [[bd[i,i] for i in range(4)], [bd[i,3-i] for i in range(4)]]
            score = 0
            for line in lines:
                # 내가 채울 수 있는 줄(상대 조각 없을 때)
                if all(cell==0 or cell==pieces.index(sim_piece)+1 for cell in line):
                    empties = sum(1 for cell in line if cell==0)
                    score += empties
            return score

        while True:
            # ── 1) 선택 단계: 다음 놓을 piece 결정 ──
            if sim_piece is None:
                best_val = float('inf')
                best_pieces = []
                for piece in sim_avail:
                    # 이 조각을 주고 상대가 최선으로 놓았을 때 남는 potential 계산
                    worst = -float('inf')
                    for (r0, c0) in get_place_actions(sim_board):
                        tb = sim_board.copy()
                        tb[r0,c0] = pieces.index(piece)+1
                        val = line_potential(tb, 3-player)
                        worst = max(worst, val)
                    if worst < best_val:
                        best_val = worst
                        best_pieces = [piece]
                    elif worst == best_val:
                        best_pieces.append(piece)
                sim_piece = random.choice(best_pieces)
                sim_avail.remove(sim_piece)

            # ── 2) 배치 단계: 위치 결정 ──
            moves = get_place_actions(sim_board)
            if not moves:
                return None   # 무승부

            # 2-1) 즉시 승리 수 확인
            for (r0, c0) in moves:
                tb = sim_board.copy()
                tb[r0,c0] = pieces.index(sim_piece)+1
                if check_win(tb):
                    r, c = r0, c0
                    break
            else:
                # 2-2) 상대 즉시 승리 블록
                block = None
                for opp_piece in sim_avail:
                    for (r0, c0) in moves:
                        tb = sim_board.copy()
                        tb[r0,c0] = pieces.index(sim_piece)+1
                        # 상대가 이 piece를 가져가서 놓았을 때 이기는지
                        tb2 = tb.copy()
                        tb2[r0,c0] = pieces.index(opp_piece)+1
                        if check_win(tb2):
                            block = (r0,c0)
                            break
                    if block: break
                if block:
                    r, c = block
                else:
                    # 2-3) 휴리스틱으로 best potential 위치
                    best_score = -float('inf')
                    best_moves = []
                    for (r0, c0) in moves:
                        tb = sim_board.copy()
                        tb[r0,c0] = pieces.index(sim_piece)+1
                        val = line_potential(tb, player)
                        if val > best_score:
                            best_score = val
                            best_moves = [(r0,c0)]
                        elif val == best_score:
                            best_moves.append((r0,c0))
                    r, c = random.choice(best_moves)

            sim_board[r,c] = pieces.index(sim_piece)+1

            # ── 종료 검사 ──
            if check_win(sim_board):
                return player
            if not sim_avail:
                return None  # 무승부

            # 턴 교대
            player    = 3 - player
            sim_piece = None