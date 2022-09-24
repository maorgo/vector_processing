# Vector Processing #

## About the program ##
### This program calculates the mean and standard deviation of vectors received ###

This program has 1 file, `main.py` that launches 2 different processes:
1. `VectorGenerator.py` that generates vectors and sends it through IPC to a second process.<br>This process attempts to keep a temporal steady transport pace of 1000Hz.
2. `VectorProcessor.py` that accepts the sent vectors and groups them into a 100 vectors long matrices.<br>Then it calculates some statistics about them and persists the results to the filesystem. 

## Tests ##
In order to execute tests, just run the relevant test class inside this path. 
<br>For example: `python3 VectorGeneratorTest.py`

## Running the program itself ##
In order to run the program itself, please run the `main.py` file. 
<br>In order to start the program in a "noisy mode", which mimics network packet drops, please pass the `-n` when running the `main.py` file.

### Examples ###
In order to run the application from the root directory `multiprocessing`: `python3 main.py`
<br>In order to run this application in noisy mode: `python3 main.py -n`