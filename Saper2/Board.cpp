#include <vector>
#include <algorithm>
#include "board.h"
#include <utility>

	Board::Board(int x) : size(x) {
		field.resize(size);
		std::generate(field.begin(), field.end(), [x]() mutable {return std::vector<Cell>(x); });
		
	}

	bool Board::isValid(int x, int y)
	{
		return (x >= 0) && (x < size) && (y >= 0) && (y < size);
	}
	
	bool Board::selectCoord(int x, int y) {
		std::vector<std::pair<int, int>> coords{
					{(x - 1), y}, {(x + 1), y},
					{(x - 1), (y + 1)}, {x, (y + 1)}, {(x + 1), (y + 1)},
					{(x - 1), (y - 1)}, {x, (y - 1)}, {(x + 1), (y - 1)} };
		
		if (isValid(x, y)) {
			auto& cell = field.at(x).at(y);
			if (!isCovered(cell)) return false;

			if (checkBomb(cell)) {

			};
			
			int count{};
			for (const auto& pair : coords) {
				count += countNeighbourBombs(pair.first,pair.second);
			}

			cell.uncover(count);

			if (count > 0) {
				return true;
			}
		}
		else {
			return false;
		}
		for (const auto& pair : coords) {
			selectCoord(pair.first, pair.second);
		}
		return true;
	}
	int Board::countNeighbourBombs(int x, int y) {
		//jakby jeblo to zmien
		if (isValid(x, y) && checkBomb(field.at(x).at(y))) 
			return 1;
		return 0;
	}

	int Board::checkNeighbourBombs(int x, int y) {
		std::vector<std::pair<int, int>> coords{
					{(x - 1), y}, {(x + 1), y},
					{(x - 1), (y + 1)}, {x, (y + 1)}, {(x + 1), (y + 1)},
					{(x - 1), (y - 1)}, {x, (y - 1)}, {(x + 1), (y - 1)} };
		int count{};
		for (const auto& pair : coords) {
			count += countNeighbourBombs(pair.first, pair.second);
		}
		return count;

	}

	void Board::checkNeighboursRecursivly(int x, int y) {
	
	};

	void Board::showBoard() {
		for (int x = 0; x < field.size(); x++){
			for (int y = 0; y < field.size(); y++){
				std::cout << field[x][y].getSprite();
			}
			std::cout << std::endl;
		}
	}

	Cell& Board::getCell(int x, int y)
	{
		return field.at(x).at(y);
	}

	void Board::showDebugBoard() {
		for (int x = 0; x < field.size(); x++) {
			for (int y = 0; y < field.size(); y++) {
				std::cout << field[x][y].getDebugSprite();
			}
			std::cout << std::endl;
		}
	}

	bool Board::checkBomb(const Cell& c) const {
		return c.isBomb;
	}

	bool Board::isCovered(const Cell& c) const {
		return c.isCovered;
	}

	bool Board::validateCoords(int x, int y) {
		return isValid(x, y) && isCovered(field.at(x).at(y));
	}