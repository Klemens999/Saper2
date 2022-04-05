#include <iostream>
#include "classes.h"

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