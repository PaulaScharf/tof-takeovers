# Detecting dangerous takeovers on a bicycle

This repo contains code for:
- `./training/`: training and testing a neural network for detecting when something overtakes a bicycle at a dangerously close distance based on low resolution depth videos. Currently the network is trained to detect anything overtaking, but as a next step it should detect specifically cars overtaking.
- `./deployment/`: deploying the trained network on a senseBox MCU S2 with a VL53L8CX sensor for recording the depth images
- `./data-collection/`: collecting more data for training the neural network

## Concept

![figures/concept.png](figures/concept.png)

## Hardware setup on a bicycle carrier

![figures/bike_carrier_setup.jpg](figures/bike_carrier_setup.jpg)

