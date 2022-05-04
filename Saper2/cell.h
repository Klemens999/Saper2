#pragma once
#include <string>
#include <iostream>

class Cell {
	
	
	bool isNumber = false;
	std::string sprit = " O ";
	const static std::string flag;
public:
	bool isBomb = false;
	bool isCovered = true;
	bool isFlag = false;
	Cell();
	void changeSprite(int x);
	void useFlag();
	std::string getSprite();
	std::string getDebugSprite();
	void uncover(int sprite);
};


