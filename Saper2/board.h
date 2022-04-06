#include <vector>
#include "cell.h"
#include "GameController.h"
#pragma once

class Board {
	std::vector<std::vector<Cell>> field;
	int size{};
	Gamecon Game;
public:
	Board(int x);
	bool isValid(int x, int y);
	void selectCoord(int a, int b);
	void showBoard();
};

