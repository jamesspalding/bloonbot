# Bloonbot


* [x] Save game stats and tower stats for each attempt
      
* [x] Have bot play full game without bugs

* [x] Use training map to improve placement accuracy

* [ ] Use round data to inform purchase decisions

* [ ] Take data as input

A bot which plays BTD6 without human interaction.

Uses tesseract to read game values from screen. Trained off bloons.traineddata to recognize font.

Places towers in grid over map.

Attempts to maximize money while minimizing lives lost.

# Model

* [x] Create model

* [ ] Train model

* [ ] Obtain misclassification rates for inheritance vs crossover vs hybrid

Each attempt (Round 1 - game over) as an observation.

Fitness determined by rount count, least lives lost, most money saved.

Starts entirely random. Begins making decisions 2nd generation onward.

For each pair of parents in a generation, 2 offspring are created. One using column-wise inheritance, and one using row-wise crossover.
