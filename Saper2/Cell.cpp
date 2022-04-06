#include <string>
#include <iostream>
#include "cell.h"

	Cell::Cell() {
		if (rand() % 7 == 1) {
			isBomb = 1;
			sprit = " B ";
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


	const std::string Cell::flag = { "(F)" };
