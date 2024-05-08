# Jump and Run (pygame)

A simple platformer game written in python.


## Deploy and run

Install dependencies: `pipenv install`

Run game: `pipenv run python game.py`
- Use arrow keys or wasd to move
- Toggle sounds with 'm'

Run level editor:  `pipenv run python editor.py data/levels/NN.json`
- Use arrow keys or wasd to move
- Place tiles with left click
- Remove tiles with right click
- Use scroll wheel to change tile group
- Use shift + scroll wheel to change tile variant
- Use 'g' to toogle between on- and offgrid tile placement

## Packaging

`pipenv run pyinstaller --add-data data:data --onefile --windowed game.py --name JumpNRun`

## License(s)

- Font: [press-start-2p](./data/fonts/press-start-2p-LICENSE.txt) (SIL OPEN FONT LICENSE Version 1.1)
- Images, music, and sounds: CC0 / Public Domain
- Source code: MIT License (see below)

Copyright 2024, Tilman Moser

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
