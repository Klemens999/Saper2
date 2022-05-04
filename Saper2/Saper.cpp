#include <iostream>
#include <cctype>
#include "Gamecon.h"

	int main() {
			int x, y;
			char option;
			int size;
			std::cout << "Wybierz wielkosc planszy, wpisujac liczbe od 0-16" << std::endl;
			std::cin >> size;
			Gamecon game{};
			game.createBoard(size);
			do {

				game.showBoard();
				std::cout << " " << std::endl;
				std::cout << "DEBUG BOARD:" << std::endl;
				game.showDebugBoard();
				std::cout << " " << std::endl;
				std::cout << "Wpisz komende: 'F' jesli chcesz oflagowac pole" << std::endl;
				std::cout << "Wpisz komende: 'C' jesli chcesz sprawdzic pole" << std::endl;
				std::cin >> option;
				std::cout << "Wybierz koordynaty wpisujac liczbe od 1 do " << size << std::endl;
				std::cout << "Szerokosc: " << std::endl;
				std::cin >> y;
				std::cout << " " << std::endl;
				std::cout << "Wysokosc: " << std::endl;
				std::cin >> x;
				std::cout << " " << std::endl;
				game.selectCoord(x - 1, y - 1, std::tolower(option));
				game.nextTurn();
				

			} while (game.gameGoing == false);
		

	};