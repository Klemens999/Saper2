#pragma once
#include <memory>
#include "Board.h"
#include "Cell.h"


class Gamecon {
	std::unique_ptr<Board> board;
	int move = 0;

public:
	bool gameGoing = false;

	bool checkBomb(Cell& c);
	void createBoard(int size);
	void showBoard();
	void selectCoord(int x, int y, char option);
	void showDebugBoard();
	void gameOver();
	void nextTurn();
};