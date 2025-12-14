## Perlin Noise Terrain Generation

This python program creates a perlin noise map and renders it as procedural terrain in pygame-ce

## Installation
Download and extract the zip file (or clone from git).
Create a python virtual environment for version 3.12.6 in the procedural_terrain-master  directory.
Install the necessary dependencies found in the “requirements.txt” file. 
Run the “main.py” file to start the program.

## Example Windows installation procedure (with Python 3.12.6 installed)
1. In command prompt or other terminal, navigate to the intended program file directory.
2. Enter the following commands: 
    ```
    git clone https://github.com/martinje0204/procedural_terrain.git
    cd .\procedural_terrain\
    python -m venv myenv
    myenv\Scripts\activate
    pip install -r requirements.txt
    python main.py
    ```
    
## Usage instructions
Run the main.py file to start the program.

## Controls
W,A,S,D : navigate the world  \
Q / E : zoom in / out  \
R : resets loaded chunks and generates new world with random seed 

## Changing terrain generation parameters:
Edit the noisemap_scale value at the top of "__init__.py" to change the terrain scale. Higher values create larger, smoother terrain, while smaller values create smaller, more jagged terrain.

The threshold values for each terrain tile height can be changed in "terrain.py" in the classify() method of the ChunkGenerator class.