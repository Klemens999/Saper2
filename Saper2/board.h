#include <vector>
#pragma once
#include "Cell.h"

class Board {
	std::vector<std::vector<Cell>> field;
	int size{};
	
public:
	Board() = default;
	Board(int x);
	bool isValid(int x, int y);
	bool selectCoord(int x, int y);
	bool validateCoords(int x, int y);
	bool checkBomb(const Cell& c) const;
	bool isCovered(const Cell& c) const;
	void checkNeighbourCell(int x, int y);
	void showDebugBoard();
	void showBoard();
	int countNeighbourBombs(int x, int y);
	int checkNeighbourBombs(int x, int y);
	void checkNeighboursRecursivly(int x, int y);
	Cell& getCell(int x, int y);
};

