// Adds 1+...+100
  @i // i refers to some location in memory
  M=1 // i=1
  @sum // sum refers to some location in memory
  M=0 // sum=0
(LOOP)
  @i // load the address represented by i into A
  D=M // store the value at i in D (D=i)
  @100 // load 100 into A
  D=D-A // D=i-100
  @END // prepare to possibly jump to END
  D;JGT // if (i-100) > 0 goto END, i.e. loop is done
  @i
  D=M // D=i
  @sum // sum refers to some location in memory
  M=D+M // add the value stored in D to the value stored at sum (and store that result in sum), i.e. sum=sum+i
  @i
  M=M+1 // i=i+1
  @LOOP // prepare to jump to LOOP
  0;JMP // unconditional jump
(END)
  @END
  0;JMP // infinite loop
