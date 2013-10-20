#!/bin/bash

python generate.py \
logs/4.2/res-prob.comma.prob.txt \
"Roulette,Roulette" \
logs/4.2/res-prob.plus.prob.txt \
"Roulette+Roulette" \
logs/4.2/res-prob.plus.tourn.txt \
"Roulette+Tournament" \
logs/4.2/res-prob.comma.tourn.txt \
"Roulette,Tournament" \
logs/4.2/res-tourn.comma.prob.txt \
"Tournament,Roulette" \
logs/4.2/res-tourn.plus.prob.txt \
"Tournament+Roulette" \
logs/4.2/res-tourn.plus.tourn.txt \
"Tournament+Tournament" \
logs/4.2/res-tourn.comma.ptourn.txt \
"Tournament,Tournament" \
-t \
"Operator Comparison: K-Tournament vs Roulette Wheel vs +/,"
