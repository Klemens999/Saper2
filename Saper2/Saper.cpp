#include <iostream>
#include <vector>
#include <string>

	bool gameOver = false;
	int move;
	class GameControl {
		
};

class Cell {
public:
	bool isBomb = false;
	bool isFlag = false;
	bool isNumber = false;
	int id;
	int neighbour{};
	std::string sprit; 
	std::string flag = "(F)";

	Cell(int x) : id(x){
		sprit = "(?)";
		if (rand() % 4 == 1) {
			isBomb = 1;
			sprit = "(B)";
		}
		
		
	}

	void showID(){
		std::cout << id << std::endl;
	}
	int checkNeighbour() {
		if (isBomb == 1) {
			return 1;
		}
	}
	void checkBomb() {
		if (move < 1) {
			isBomb = 0;
		}
		if (isBomb == 1) {
			std::cout << "GAME OVER";
			gameOver = 1;
		}
	}
	void changeSprite(int x){
		std::string s = std::to_string(x);
		sprit = '(' + s + ')';
		
	}

	

};

class Board {
	std::vector<Cell*> field;
	int size;
public:
	Board(int x) : size(x){
		for (int i = 0; i < (size*size); i++) {
			field.push_back(new Cell(i));
	}
	}
	bool isValid(int x)
	{
		return (x >= 0) && (x <= (size*size));
	}

	void selectCoord(int x, int y) {
		int count{};
		int algo= (y - 1) * size + (x - 1);
		Cell* ptr = field.at(algo);
		ptr->checkBomb();
		
		Cell* n = nullptr;
		algo = (y - 0) * size + (x - 2);
		if (isValid(algo) == 1) {
			n = field.at(algo);
			if (n->checkNeighbour() == 1) {
				count++;
			}
		}

		algo = (y - 0) * size + (x - 1);
		if (isValid(algo) == 1) {
			n = field.at(algo);
			if (n->checkNeighbour() == 1) {
				count++;
			}
		}
		
		algo = (y - 0) * size + (x + 0);
		if (isValid(algo) == 1) {
			n = field.at(algo);
			if (n->checkNeighbour() == 1) {
				count++;
			}
		}

		algo = (y - 1) * size + (x - 2);
		if (isValid(algo) == 1) {
			n = field.at(algo);
			if (n->checkNeighbour() == 1) {
				count++;
			}
		}

		algo = (y - 1) * size + (x - 0);
		if (isValid(algo) == 1) {
			n = field.at(algo);
			if (n->checkNeighbour() == 1) {
				count++;
			}
		}

		algo = (y + 1) * size + (x - 2);
		if (isValid(algo) == 1) {
			n = field.at(algo);
			if (n->checkNeighbour() == 1) {
				count++;
			}
		}

		algo = (y + 1) * size + (x - 1);
		if (isValid(algo) == 1) {
			n = field.at(algo);
			if (n->checkNeighbour() == 1) {
				count++;
			}
		}

		algo = (y + 1) * size + (x - 0);
		if (isValid(algo) == 1) {
			n = field.at(algo);
			if (n->checkNeighbour() == 1) {
				count++;
			}
		}

		algo = (y - 1) * size + (x - 1);
		if (isValid(algo) == 1) {
			n = field.at(algo);
			if (n->checkNeighbour() == 1) {
				count++;
			}
		}
		
		if (count > 0) {
			ptr->changeSprite(count);
		}
	
	}
	
	void showBoard() {
		
		for (int i = 0; i < (size*size); i++) {
			if (i != 0 && i != 1 && i % size == 0) {
				std::cout << " " << std::endl;
			}
				std::cout << field[i]->sprit << ' ';
		}
	}
};

int main() {
	
		int x, y;
		int size;
		std::cout << "Wybierz wielkosc planszy, wpisujac liczbe od 0-16" << std::endl;
		std::cin >> size;
		Board b(size);
		do {
		b.showBoard();
		std::cout << " " << std::endl;
		std::cout << "Wybierz koordynaty" << std::endl;
		std::cin >> x;
		std::cin >> y;
		b.selectCoord(x, y);
		move++;
		

	}
	while(gameOver == false);
	

};