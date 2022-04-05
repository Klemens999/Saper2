#pragma once
#include <string>
#include <iostream>

bool gameOver = false;
int move;

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

