#include "classes.h"
#include <vector>
#include <algorithm>
#include <string>
#include <iostream>


Board::Board(int x) : size(x) {
	field.resize(size);
	std::generate(field.begin(), field.end(), [x]() mutable {return std::vector<Cell>(x); });
}

bool Board::isValid(int x, int y)
{
	return (x >= 0) && (x < size) && (y >= 0) && (y < size);
}

void Board::selectCoord(int a, int b) {
	int count{};
	int y = a - 1;
	int x = b - 1;

	if (isValid(x, y)) {

		auto Cell = field.at(x).at(y);
		if (!Cell.isCovered) return;
		Cell.checkBomb();
		if (gameOver) return;

		if (isValid((x - 1), y) == 1) {
			auto n = field.at(x - 1).at(y);
			if (n.checkNeighbour() == 1) {
				count++;
			}
		}
		if (isValid((x + 1), y) == 1) {
			auto n = field.at(x + 1).at(y);
			if (n.checkNeighbour() == 1) {
				count++;
			}
		}
		if (isValid((x - 1), (y + 1)) == 1) {
			auto n = field.at(x - 1).at(y + 1);
			if (n.checkNeighbour() == 1) {
				count++;
			}
		}
		if (isValid(x, (y + 1)) == 1) {
			auto n = field.at(x).at(y + 1);
			if (n.checkNeighbour() == 1) {
				count++;
			}
		}
		if (isValid((x + 1), (y + 1)) == 1) {
			auto n = field.at(x + 1).at(y + 1);
			if (n.checkNeighbour() == 1) {
				count++;
			}
		}
		if (isValid((x - 1), (y - 1)) == 1) {
			auto n = field.at(x - 1).at(y - 1);
			if (n.checkNeighbour() == 1) {
				count++;
			}
		}
		if (isValid(x, (y - 1)) == 1) {
			auto n = field.at(x).at(y - 1);
			if (n.checkNeighbour() == 1) {
				count++;
			}
		}
		if (isValid((x + 1), (y - 1)) == 1) {
			auto n = field.at(x + 1).at(y - 1);
			if (n.checkNeighbour() == 1) {
				count++;
			}
		}
		Cell.uncover();
		if (count > 0) {
			Cell.changeSprite(count);
			Cell.uncover();
			return;
		}
	}
	if (count == 0) {

		if (isValid((a + 1), b) == 1)
			selectCoord((a + 1), b);
		if (isValid((a - 1), b) == 1)
			selectCoord((a - 1), b);
		if (isValid((a + 1), (b + 1)) == 1)
			selectCoord((a + 1), (b + 1));
		if (isValid(a, (b + 1)) == 1)
			selectCoord(a, (b + 1));
		if (isValid((a - 1), (b + 1)) == 1)
			selectCoord((a - 1), (b + 1));
		if (isValid((a + 1), (b - 1)) == 1)
			selectCoord((a + 1), (b - 1));
		if (isValid(a, (b - 1)) == 1)
			selectCoord(a, (b - 1));
		if (isValid((a - 1), (b - 1)) == 1)
			selectCoord((a - 1), (b - 1));
	}
}
void Board::showBoard() {
	for (int x = 0; x < field.size(); x++) {
		for (int y = 0; y < field.size(); y++) {
			std::cout << field[x][y].getSprite();
		}
		std::cout << std::endl;
	}
}



Cell::Cell() {
	if (rand() % 7 == 1) {
		isBomb = 1;
		sprit = " B ";
	}
}
//przenies do boarda
int Cell::checkNeighbour() {
	if (isBomb == 1) {
		return 1;
	}
}
//niech zwraca boola
void Cell::checkBomb() {
	if (move < 1) {
		if (isBomb) {
			isBomb = false;
		}
	}
	else if (isBomb) {
		std::cout << "GAME OVER";
		gameOver = true;
	}
}
void Cell::changeSprite(int x) {
	sprit = '(' + std::to_string(x) + ')';
}
void Cell::useFlag() {
	sprit = flag;
}
std::string Cell::getSprite() {
	return sprit;
}
void Cell::uncover() {
	isCovered = false;
}


