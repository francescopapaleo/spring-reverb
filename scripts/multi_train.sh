#!/bin/bash

configs=("TCN-1" "TCN-2" "TCN-3" "TCN-4" "TCN-5" "TCN-6" "TCN-7" "TCN-8")

# Change the working directory to the parent directory
cd "$(dirname "${BASH_SOURCE[0]}")/.."

n_epochs=(25)
batch_size=(16)

for epoch in "${n_epochs[@]}"; do
    for batch in "${batch_size[@]}"; do
        for config in "${configs[@]}"; do
            python3 train.py --n_epochs "$epoch" --batch_size "$batch" --config "$config" --logdir "results/runs"
        done
    done
done
