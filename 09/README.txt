SNAKE

This is a game of Snake.  Use the direction keys to guide your snake to food without hitting yourself or the walls.  The more food you get, the longer your snake becomes, and the harder it gets to avoid collisions.
Since the scale is so small (i.e. it's hard to hit a single pixel of food with the snake), I've taken some steps to make testing a bit easier:

1) Slowed down the speed.
In the moveSnake() method in SnakeGame.jack, I set Sys.wait to 35.  For faster gameplay, shrink the wait time (I was playing at around 20).

2) Made the snake grow a lot when you get the food.
This should make it a bit easier to test the self-collision detection when the Snake hits itself (i.e. you don't need to get as many pieces of food to get long enough to run into yourself).
In the grow() method in Snake.jack, I've set the snake to grow 15 pixels in length each time you get a piece of food.  I was playing with a value of 5.
With this configuration, you should only need to get 3 pieces of food to win.
