// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R0 and stores the result in R1.
// (R0, R0, R1 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.
// testing
// @3
// D=A
// @R0
// M=D
// @5
// D=A
// @R1
// M=D
// program
@R2
M=0 // initialize product to zero
@i
M=1 // initialize counter i to 1
(LOOP) // loop R1 times
  @i
  D=M // D=i
  @R1
  D=D-M // D=i-R1
  @END
  D;JGT // if i-R1 > 0 goto END
  @R0
  D=M
  @R2
  M=M+D // add R2 to in-progress product on each loop
  @i
  M=M+1
  @LOOP
  0;JMP
@R2
D=M
@R1
M=D
(END)
  @END
  0;JMP
