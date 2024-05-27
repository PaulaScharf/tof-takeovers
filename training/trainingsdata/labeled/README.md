All values are constrained to fall between 0 and 2000 mm.

## luca/
### Fahrraeder.csv
The file `Fahrraeder.csv` was recorded by Luca. He very slowly drove along the Promenade and recorded other cyclists overtaking him. this file should only be used for scenarios, where both overtaking cars AND overtaking bikes should be detected. Otherwise use `Fahrraeder_not_takeover.csv`.

### Fahrraeder_reversed.csv, Fahrraeder_90.csv, Fahrraeder_270.csv
Reversed and rotated versions of `Fahrraeder.csv`. All labels in the latter three videos are 'no takeover' (0). As we are currently not training with the bikes anyway these files can be dismissed and instead `autos_7_reversed.csv`, `autos_7_rotated_90.csv` and `autos_7_rotated_270.csv` should be used.

### Fahrraeder_not_takeover.csv
The same as `Fahrraeder.csv` except the all labels are 'no takeover' (0).

## paula/
### autos_1.csv, autos_2.csv, autos_3.csv, autos_4.csv, autos_5.csv, autos_6.csv, autos_7.csv
Paula drove past parked cars and reversed the sensor orientation, so that it looks like the cars are overtaking. Compared to their unlabeled counterparts, these files have their beginnings and ends removed, as these are mostly empty.

### autos_7_reversed.csv, autos_7_rotated_90.csv, autos_7_rotated_270.csv
Reversed or rotated versions of `autos_7.csv`. All labels in the latter three videos are 'no takeover' (0).

### passing_cars.csv
A few naturally recorded cars that Paula overtook on her bicycle. This file is similar in spirit to `autos_7_reversed.csv`.

### indoor_turning.csv
Paula recorded this inside her office. No takeovers are visible in this video.

### bike_setup.csv
A few frames from setting up the bike, as there are often false positives during that time. It does not feature any takeovers.
