#!/bin/sh

# export variables
export $(grep -v '^#' $1 | xargs)

# export variables for vite env
export $(grep -v '^#' $1 | sed -r 's/SO_/VITE_SO_/g' | xargs)
