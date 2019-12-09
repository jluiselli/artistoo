# CPMjs

Implements a simple Cellular Potts Model in JavaScript. Code includes the extension for cell migration published in 

Ioana Niculescu, Johannes Textor, Rob J. de Boer:
__Crawling and Gliding: A Computational Model for Shape-Driven Cell Migration__
PLoS Computational Biology 11(10): e1004280
http://dx.doi.org/10.1371/journal.pcbi.1004280

# How it works

This code has been ported over from our older "cpm" repository. This is now an ES6 module, 
which is compiled trough "rollup" for use in the browser. Users who wish to use this version
of CPMjs can use the compiled code in the `build/` folder as it is; there is no
need to compile anything. See below for examples and how to use them.

Developers can extend the code with their own modules; documentation will follow later
(see the Makefile).

## Browser examples

CPMjs can be used to create interactive simulations in the webbrowser. We have implemented
several examples showing various processes that can be simulated with a CPM; see the
links below. (Please note that these examples may not work properly in Internet Explorer). 

We have the following examples for web-browser CPMs (see also `examples/html`):

* [A simple Ising model](https://ingewortel.github.io/cpmjs.github.io/examples/IsingModel.html)
* [A simple 2D CPM cell](https://ingewortel.github.io/cpmjs.github.io/examples/html/SingleCell.html)
* [The classic CPM cell sorting example](https://ingewortel.github.io/cpmjs.github.io/examples/html/Cellsorting.html)
* [Dividing CPM cells](https://ingewortel.github.io/cpmjs.github.io/examples/html/CellDivision.html)
* [A cell moving through active cell migration](https://ingewortel.github.io/cpmjs.github.io/examples/html/Actmodel.html)
* [Migrating cell in a microchannel](https://ingewortel.github.io/cpmjs.github.io/examples/html/Microchannel.html)
* [Migrating cells on adhesive patterns](https://ingewortel.github.io/cpmjs.github.io/examples/html/ActOnMicroPattern.html)
* [Simulating plain diffusion](https://ingewortel.github.io/cpmjs.github.io/examples/html/Diffusion.html)
* [Cells moving up a chemokine gradient](https://ingewortel.github.io/cpmjs.github.io/examples/html/Chemotaxis.html)
* [Multiple cells migrating together, interactive web page](https://ingewortel.github.io/cpmjs.github.io/examples/html/CollectiveMigration.html)
* [Cells moving towards a target point](https://ingewortel.github.io/cpmjs.github.io/examples/html/DirectedMotionTargetPoint.html)
* [Cells moving in the same global direction](https://ingewortel.github.io/cpmjs.github.io/examples/html/DirectedMotionLinear.html)
* [A layer of tightly packed epidermal cells](https://ingewortel.github.io/cpmjs.github.io/examples/html/Epidermis.html)
* [T cells moving in the epidermis](https://ingewortel.github.io/cpmjs.github.io/examples/html/EpidermisWithTCells.html)
* [Cells producing a chemokine with other cells responding to it](https://ingewortel.github.io/cpmjs.github.io/examples/ManyCellsDiffusion.html)
* [Cells moving with a preferred direction](https://ingewortel.github.io/cpmjs.github.io/examples/html/ManyCellsPrefDir.html)
* [Particle following a random walk](https://ingewortel.github.io/cpmjs.github.io/examples/RandomWalk.html)


We also have a few examples of plain cellular automata (CAs):

* [Conway's Game of Life](https://ingewortel.github.io/cpmjs.github.io/examples/html/GameOfLife.html)
* [SIR model of a spreading infection](https://ingewortel.github.io/cpmjs.github.io/examples/html/SIR.html)

## Node examples

Simulations can also be run from the command line using nodejs. The first time you do this,
you have to install several dependencies. Go to the base folder of this package and run

```
npm install
```

which will automatically install the dependencies as supplied in the `package.json` file.

Here's an example of how to run the node script:

```
cd examples/node
node run-ActModel.js
```

This may give an error the first time, because the script is trying to store images of
the simulation to a file `output/img/ActModel` which does not exist. Create this directory
and try again:

``` 
mkdir -p output/img/ActModel
node run-ActModel.js
```

This will print some output to the console; typically the centroid of each 
cell at each timepoint. See the node script and the 
[Simulation class](https://ingewortel.github.io/cpmjs.github.io/class/src/simulation/Simulation.js~Simulation.html)
for details.


To create a movie, run:
```
mkdir -p output/mp4
ffmpeg -r 60 -f image2 -i output/img/ActModel/ActModel-t%d.png -vcodec libx264 -crf 25 -pix_fmt yuv420p output/mp4/ActModel.mp4
```
