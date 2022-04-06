#include "Cell.h"
class Gamecon {
public:
	int move = 0;
	bool gameOver = false;
	Gamecon() {};
	void checkBomb(Cell c) {
		if (move < 1) {
			if (c.isBomb) {
				c.isBomb = false;
			}
		}
		else if (c.isBomb) {
			std::cout << "GAME OVER";
			gameOver = true;
		}
	};
};