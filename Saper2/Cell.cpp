#include <string>
#include <iostream>
#include "cell.h"

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


