#include <string>
#include <iostream>
#include "cell.h"

	Cell::Cell() {
		if (rand() % 7 == 1) {
			isBomb = 1;
		}
	}
	void Cell::changeSprite(int x) {
		//std::cout << "DEBUG SPRITE VALUE: " << x << std::endl;

		if (x == 0) sprit = " # ";
		else {
			sprit = '(' + std::to_string(x) + ')';
		}
		//std::cout << "DEBUG CELL SPRITE AFTER CHANGE: " << sprit << std::endl;
	}
	void Cell::useFlag() {

		sprit = flag;
		
	}
	std::string Cell::getSprite() {
		return sprit;
	}
	std::string Cell::getDebugSprite() {
		if (isBomb)
			return " B ";
		else
			return " O ";
	}
	void Cell::uncover(int sprite) {
		isCovered = false;
		changeSprite(sprite);
	}


	const std::string Cell::flag = { "(F)" };
