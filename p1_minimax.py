
def simulate(self):
        """
        Minimax-롤아웃 + 랜덤 폴리시
        depth=2 이하: 미니맥스, depth==0 또는 말이 없을 때 랜덤
        """
        return self._minimax_rollout(
            board=self.board.copy(),
            avail=self.available_pieces.copy(),
            piece=self.current_piece,
            player=self.current_player,
            depth=2
        )

    def _minimax_rollout(self, board, avail, piece, player, depth):
        # 1) 종료 검사
        if check_win(board):
            return player
        if depth == 0 or not avail:
            return self._random_playout(board, avail, piece, player)

        # 2) 말 선택 단계
        if piece is None:
            best_val, best_piece = -float('inf'), None
            for p in avail:
                next_avail = [x for x in avail if x != p]
                winner = self._minimax_rollout(board, next_avail, p, player, depth)
                score =  1 if winner == player else -1 if winner == 3-player else 0
                if score > best_val:
                    best_val, best_piece = score, p
            # 선택한 말로 다시 탐색
            return self._minimax_rollout(board,
                                         [x for x in avail if x != best_piece],
                                         best_piece,
                                         player,
                                         depth)

        # 3) 배치 단계
        best_val, best_move = -float('inf'), None
        for (r, c) in get_place_actions(board):
            tb = board.copy()
            tb[r, c] = pieces.index(piece) + 1
            winner = self._minimax_rollout(tb, avail, None, player, depth-1)
            score =  1 if winner == player else -1 if winner == 3-player else 0
            if score > best_val:
                best_val, best_move = score, (r, c)

        # 최적 수를 실제로 두고 다시 탐색
        new_board = board.copy()
        rr, cc = best_move
        new_board[rr, cc] = pieces.index(piece) + 1
        return self._minimax_rollout(new_board, avail, None, player, depth-1)

    def _random_playout(self, board, avail, piece, player):
        """기존 랜덤 시뮬레이션 코드"""
        sim_board  = board.copy()
        sim_avail  = avail.copy()
        sim_piece  = piece
        current    = player

        while True:
            if sim_piece is None:
                sim_piece = random.choice(sim_avail)
                sim_avail.remove(sim_piece)

            moves = get_place_actions(sim_board)
            if not moves:
                return None

            r, c = random.choice(moves)
            sim_board[r, c] = pieces.index(sim_piece) + 1

            if check_win(sim_board):
                return current
            if not sim_avail:
                return None

            current    = 3 - current
            sim_piece  = None