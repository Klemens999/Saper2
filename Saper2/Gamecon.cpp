#include "Gamecon.h"

bool Gamecon::checkBomb(Cell& c) {
	if (move < 1) {
		if (c.isBomb) {
			c.isBomb = false;
			return false;
		}
	}
	return c.isBomb;
}

void Gamecon::createBoard(int size) {
	board = std::make_unique<Board>(size);
}

void Gamecon::showBoard() {
	board->showBoard();
}
void Gamecon::gameOver() {
	std::cout << "GAME OVER";
	gameGoing = true;
}

void Gamecon::selectCoord(int x, int y, char option) {
	if(!board->validateCoords(x, y)) return;
	if (option == 'f') {
		if (board->getCell(x, y).isFlag) {
			return;
		}
		board->getCell(x, y).useFlag(); 
		return;
	}
	if (board->checkBomb(board->getCell(x,y))) {
		gameOver();
		return;
	};
	int count = board->checkNeighbourBombs(x, y);
	board->getCell(x, y).uncover(count);
	
	if (count) {
		return;
	}
	std::vector<std::pair<int, int>> coords{
					{(x - 1), y}, {(x + 1), y},
					{(x - 1), (y + 1)}, {x, (y + 1)}, {(x + 1), (y + 1)},
					{(x - 1), (y - 1)}, {x, (y - 1)}, {(x + 1), (y - 1)} };
	for (const auto& pair : coords) {
		selectCoord(pair.first, pair.second, 'c');
	}

}

void Gamecon::nextTurn() {
	std::cout << "MOVE: " << ++move << std::endl;
}


void Gamecon::showDebugBoard() {
	board->showDebugBoard();
}
