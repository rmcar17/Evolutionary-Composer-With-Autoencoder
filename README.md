# Evolutionary Composer with Autoencoder

This repository contains all necessary files to run the evolutionary composer.

## Setup

Use the [anaconda](https://anaconda.org/) distribution of Python to set up the environment. Install the necessary packages.

```bash
conda env create -f environment.yml 
```

Also, please extract the contents of the ``.rar`` files in ``data\model`` directly into the director (there should be no subdirectories).

## Running the Application

Activate the installed environment and run the ```application.py``` file.
```bash
conda activate evolutionary-composer-with-autoencoder
python -m application.py
```

## Instructions
### Listening to the Songs
Click on a pale green box to hear the respective song played.
### Saving Songs
Click on 'Select Save' then select the songs which you want to save. Finish by clicking the 'Save' button. The files will appear in savedSongs named ``<song-id>.midi``. Be careful  if you restart the application as saving a song which has the same id as a saved song will cause the previous song to be overwritten.
### Removing Songs
Click the 'Select Kill' button then select the songs you want to remove. Finish by clicking the 'Kill' button.
### Generating New Songs
Once some old songs removed, click the 'Reproduce' button to create new songs based on the old ones. Ensure there are at least two songs remaining before clicking the button.
### Adding New Random Songs
If none of the music if enjoyed, or if the music is wanted to be evolved in a new direction, one can add new random songs by clicking the 'Random New' button.
### Evolution Parameters
All of the following can be incremented or decremented.
#### Population Size
The number of songs generated after clicking the reproduce button (songs may need to be killed first if one wants the population size to be smaller).
#### NF Mut Rate
This reflects how likely the threshold controlling note frequency is to change. If too many notes are being played, or too few, try increasing this value.
#### NF Mut Fac
This reflects by how much the threshold controlling note frequency changes by on the condition it does change. Increase this value to quickly change how many notes are played. Decrease if the current frequency of notes is desired.
#### Mut Rate
This relects how likely the parameters controlling the music are to change. Increase this value if the reproduced songs sound too similar.
#### Mut Fac
This reflects by how much the parameters controlling the music change by on the condition it does change. Increase this value if you want to hear more of a difference in the reproduced songs from the originals.
