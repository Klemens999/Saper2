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
	
	std::string sprit = " O ";
	std::string flag = "(F)";

	Cell(int x) : id(x){
		
		if (rand() % 7 == 1) {
			isBomb = 1;
			sprit = " B ";
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
			if (isBomb == 1) {
				isBomb = 0;
				sprit = "(?)";
			}
		}
		else if (isBomb == 1) {
			std::cout << "GAME OVER";
			gameOver = 1;
		}
	}

	void changeSprite(int x){
		std::string s = std::to_string(x);
		sprit = '(' + s + ')';
		
	}

	void useFlag() {
		sprit = flag;
	}
};

class Board {
	std::vector<std::vector<Cell*>> field;
	int size;
public:
	Board(int x) : size(x){
		for (int j = 0; j < size; j++) {
			std::vector<Cell*> temp;
				for (int i = 0; i < (size); i++) {
					temp.push_back(new Cell(i));
			}
				field.push_back(temp);
		}
	}

	bool isValid(int x, int y)
	{
		return (x >= 0) && (x < size) && (y >= 0) && (y < size);
	}
	
	void selectCoord(int a, int b) {
		
		int count{};
		int y = a - 1;
		int x = b - 1;

		if(isValid(x, y) == 1) {

			Cell* ptr = field.at(x).at(y);
			ptr->checkBomb();

			Cell* n = nullptr;

			if (isValid((x - 1), y) == 1) {
				Cell* n = field.at(x - 1).at(y);
				if (n->checkNeighbour() == 1) {
					count++;
				}
			}

			if (isValid((x + 1), y) == 1) {
				Cell* n = field.at(x + 1).at(y);
				if (n->checkNeighbour() == 1) {
					count++;
				}
			}

			if (isValid((x - 1), (y + 1)) == 1) {
				Cell* n = field.at(x - 1).at(y + 1);
				if (n->checkNeighbour() == 1) {
					count++;
				}
			}

			if (isValid(x, (y + 1)) == 1) {
				Cell* n = field.at(x).at(y + 1);
				if (n->checkNeighbour() == 1) {
					count++;
				}
			}

			if (isValid((x + 1), (y + 1)) == 1) {
				Cell* n = field.at(x + 1).at(y + 1);
				if (n->checkNeighbour() == 1) {
					count++;
				}
			}

			if (isValid((x - 1), (y - 1)) == 1) {
				Cell* n = field.at(x - 1).at(y - 1);
				if (n->checkNeighbour() == 1) {
					count++;
				}
			}

			if (isValid(x, (y - 1)) == 1) {
				Cell* n = field.at(x).at(y - 1);
				if (n->checkNeighbour() == 1) {
					count++;
				}
			}

			if (isValid((x + 1), (y - 1)) == 1) {
				Cell* n = field.at(x + 1).at(y - 1);
				if (n->checkNeighbour() == 1) {
					count++;
				}
			}



			if (count > 0) {
				ptr->changeSprite(count);
			}
			n = nullptr;
			ptr = nullptr;
		}
			/*
			if(count < 1) {
				Cell* p = nullptr;
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
			*/
		
	}

	
	
	void showBoard() {

		for (int x = 0; x < field.size(); x++)  
		{
			for (int y = 0; y < field.size(); y++)  
			{
				std::cout << field[x][y] -> sprit;  
			}
			std::cout << std::endl;
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
				std::cout << "Wybierz koordynaty wpisujac liczbe od 1 do " << size << std::endl;
				std::cout << "Szerokosc: " << std::endl;
				std::cin >> x;
				std::cout << " " << std::endl;
				std::cout << "Wysokosc: " << std::endl;
				std::cin >> y;
				std::cout << " " << std::endl;
				b.selectCoord(x, y);
				move++;
				

			} while (gameOver == false);
		

	};