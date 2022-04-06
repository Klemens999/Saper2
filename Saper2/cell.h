#pragma once
#include <string>
#include <iostream>




class Cell {
	
	bool isFlag = false;
	bool isNumber = false;
	std::string sprit = " O ";
	const static std::string flag;
public:
	bool isBomb = false;
	bool isCovered = true;
	Cell();
	void changeSprite(int x);
	void useFlag();
	std::string getSprite();
	void uncover();
};


