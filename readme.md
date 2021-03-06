# Noise removal tool for lectures recordings

Noise removal tool is a `Python` GUI program for choosing a video file, file with sample noise and then producing a video file without noise. Uses `Audacity` and `ffmpeg`.

Perfect usage scenario is: once per week you get a new lecture recording with the exact same unbearable amount of noise🙃 Instead of removing this noise every week manually, you set up this program once and in the following weeks you just process new lecture recordings to automatically remove all noise.

# First, save all opened Audacity projects!

## How to use?

First, import audio from lecture to Audacity and export a short (1s) sample noise to separate file. Then you will need to play with Audacity and find best parameters for one or all of:

- `Normalize`
- `NoiseReduction`
- `Compressor`

I found effects listed above and applied in this order with right arguments to work best in my case.

After some work, you will need to dig deep in `AudacityCommands` class in `AudacityController.py` to put there your parameters and/or add/delete some effects.

Finally, the program should work as intended (after having installed required packages).

##### Note: if input file is audio file, then the output will be a .wav file in `macro-output` directory automatically created by Audacity in the input file directory.

## How does the program work (step by step)

After selecting right files with GUI you should press `Start` button. Then, `guiWorker.py`:

- **kills all running Audacity instances**, 
- launches new Audacity instance
    - gets noise profile from noise file
    - opens new Audacity window
    - imports, processes and exports audio from lecture file\*
- kills Audacity instances again
- executes `ffmpeg` command in a new terminal window to create a new video file with audio track without noise.

\* - it is similair to applying a Macro from within Audacity


## Requirements

- Audacity
- ffmpeg (added to PATH)

## Note

Tested only on Windows 10 with:

- Audacity `2.4.2`
- ffmpeg `4.3.2`-2021-02-27-essentials_build

## Disclaimer

This small project was created for fun to show that scripting with Audacity, Python and GUI is possible and useful. Therefore I take no responsibility for any errors you may encounter (there are many possible ways to achieve them as of now), any lost data and so on. 