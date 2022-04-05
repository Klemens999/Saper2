#pragma once
#include <string>
#include <iostream>
#include <vector>

bool gameOver = false;
int move{};

class Cell {
	bool isBomb = false;
	bool isFlag = false;
	bool isNumber = false;
	std::string sprit = " O ";
	const static std::string flag;
public:
	bool isCovered = true;
	Cell();
	int checkNeighbour();
	void checkBomb();
	void changeSprite(int x);
	void useFlag();
	std::string getSprite();
	void uncover();
};

const std::string Cell::flag = { "(F)" };

class Board {
	int size;
	std::vector<std::vector<Cell>> field;

public:
	Board(int x);
	bool isValid(int x, int y);
	void selectCoord(int a, int b);
	void showBoard();
};