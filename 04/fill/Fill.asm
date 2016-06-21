// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, the
// program clears the screen, i.e. writes "white" in every pixel.

// Put your code here.
@SCREEN
D=A
@i
M=D // initialize tracker variable i to 16384 (start of screen memory)
(LOOP)
  @KBD
  D=M
  @FILL
  D;JGT
  @EMPTY
  0;JMP
(FILL)
  @i
  D=M
  @KBD
  D=A-D
  @WRITE
  D;JGT // if i < KBD (i.e. still in bounds of screen memory), paint black
  @LOOP
  0;JMP // else do nothing and loop again
(WRITE)
  @i
  D=M // D = i
  A=D // A = memory location represented by i
  M=-1 // value at memory location represented by i = -1, i.e. paint black
  @i
  M=D+1
  @LOOP
  0;JMP
(EMPTY)
  @i
  D=M
  @SCREEN
  D=D-A
  @CLEAR
  D;JGE // if i <= SCREEN (i.e. still in bounds of screen memory), paint white
  @LOOP
  0;JMP
(CLEAR)
  @i
  D=M // D = i
  A=D // A = memory location represented by i
  M=0 // value at memory location represented by i = 1, i.e. paint white
  @i
  M=D-1
  @LOOP
  0;JMP
