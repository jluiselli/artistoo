let CPM = require("../../build/artistoo-cjs.js")

let config = {

	// Grid settings
	ndim : 2,
	field_size : [150,150],
	
	// CPM parameters and configuration
	conf : {
		// Basic CPM parameters
		torus : [false,false],				// Should the grid have linked borders?
		seed : 5,							// Seed for random number generation.
		T : 2,								// CPM temperature
		
		//This declaration of CELLS instantiates the CPMEvol model instead of the CPM model
		CELLS : ["empty", CPM.StochasticCorrector, CPM.StochasticCorrector], //The cell internal classes
        
        // used internally by StochasticCorrector subclass
        INIT_X : [0, 40, 40],
        INIT_Y: [0, 40, 40],
		INIT_V : [0, 150, 150],
		NOISE : [0,0,10],

		// only used in postMCSListener
        rX : [0, 1, 1],
        rY : [0, 0.8, 0.8],
        d : [0, 0.05, 0.05],
        speed_internal_dynamics : [0, 0.2, 0.2],
        Q : [0, 0.8, 0.8],

        division_volume : [0, 250, 250],
        shrink_rate : [0, 10, 10],
        y_growth_contribution : [0, 35, 35],

        
		// Constraint parameters. 
		// Mostly these have the format of an array in which each element specifies the
		// parameter value for one of the cellkinds on the grid.
		// First value is always cellkind 0 (the background) and is often not used.
        
        // Adhesion parameters:
         J: [ [15,15,15], 
			[15,15,15], // epidermal cells
			[15,15,15] ],
		
		
		// VolumeConstraint parameters
		LAMBDA_V : [0, 1, 1],				// VolumeConstraint importance per cellkind
		V : [0,152, 152]					// Unused - are backup.
		
	},
	
	// Simulation setup and configuration: this controls stuff like grid initialization,
	// runtime, and what the output should look like.
	simsettings : { 
	
		// Cells on the grid
		NRCELLS : [10, 10],						// Number of cells to seed for all
		// non-background cellkinds. 
		// Runtime etc
		BURNIN : 100,
		RUNTIME : 1000,
		RUNTIME_BROWSER : "Inf",
		
		// Visualization
		CANVASCOLOR : "EEEEEE",
		CELLCOLOR : ["AA111A","FFA110"],
		SHOWBORDERS : [true, true],				// Should cellborders be displayed?
		BORDERCOL : ["666666", "666666"],				// color of the cell borders
		zoom : 3,							// zoom in on canvas with this factor.
		
		// Output images
		SAVEIMG : true,						// Should a png image of the grid be saved
		// during the simulation?
		IMGFRAMERATE : 1,					// If so, do this every <IMGFRAMERATE> MCS.
		SAVEPATH : "output/img/StochasticCorrection",	// ... And save the image in this folder.
		EXPNAME : "StochasticCorrection",					// Used for the filename of output images.
		
		// Output stats etc
		STATSOUT : { browser: false, node: true }, // Should stats be computed?
		LOGRATE : 10							// Output stats every <LOGRATE> MCS.

	}
}
/*	---------------------------------- */
let sim, showYcolors

let custommethods = {
	postMCSListener : postMCSListener,
	initializeGrid : initializeGrid,
	drawCanvas : drawCanvas
}
sim = new CPM.Simulation( config, custommethods )

showYcolors = true

/* The following custom methods will be added to the simulation object*/
function postMCSListener(){
	// add the initializer if not already there
	if( !this.helpClasses["gm"] ){ this.addGridManipulator() }
	for( let i of this.C.cellIDs() ){
		updateCell(this.C, this.C.cells[i])
		if( this.C.getVolume(i) > this.C.conf.division_volume[this.C.cellKind(i)] ){
			this.gm.divideCell(i)
		}
	}
}

// Models internal concentrations of RNA replicators, with a master sequence  (X) creating mutants (Y) with lower growth rate,
//  Y population is necessary for vesicle to survive.
function updateCell(C, cell){
	if (cell.id < 0){return}
    let vol = C.getVolume(cell.id)
    let V = cell.V
    if ((cell.V - vol) < 10 && cell.X > 0){
        V += C.conf.y_growth_contribution[cell.kind]*(cell.Y/vol)/((cell.Y/vol)+0.1)
        
    }
    V -= C.conf.shrink_rate[cell.kind]
    cell.V = V
	
    let dy = C.conf.rY[cell.kind]*cell.Y*(vol-cell.X-cell.Y)/vol*C.conf.speed_internal_dynamics[cell.kind]
    let X = cell.X + (1-C.conf.Q[cell.kind])*dy+( C.conf.rX[cell.kind]*cell.X*(vol-cell.X-cell.Y)/vol - C.conf.d[cell.kind]*cell.X )*C.conf.speed_internal_dynamics[cell.kind]
    let Y = cell.Y + C.conf.Q[cell.kind]*dy - C.conf.d[cell.kind]*cell.Y*C.conf.speed_internal_dynamics[cell.kind]
	cell.setXY(X,Y)	
}

function initializeGrid(){
	
	// add the initializer if not already there
	if( !this.helpClasses["gm"] ){ this.addGridManipulator() }
    
	let nrcells = this.conf["NRCELLS"], cellkind, i
		
	// Seed the right number of cells for each cellkind 
	for( cellkind = 0; cellkind < nrcells.length; cellkind ++ ){
		
		for( i = 0; i < nrcells[cellkind]; i++ ){
			// first cell always at the midpoint. Any other cells
			// randomly.				
			if( i == 0 ){
                this.gm.seedCellAt( cellkind+1, [this.C.midpoint[0]/2, this.C.midpoint[1] ] )
			} else {
				this.gm.seedCell( cellkind+1 )
			}
		}
	}
}


// Custom drawing function to draw the preferred directions.
function drawCanvas(){
	// Add the canvas if required
	if( !this.helpClasses["canvas"] ){ this.addCanvas() }

	// Clear canvas
	this.Cim.clear( this.conf["CANVASCOLOR"] || "FFFFFF" )
	let nrcells=this.conf["NRCELLS"], cellkind, cellborders = this.conf["SHOWBORDERS"]
	
	let colfun = getColor.bind(this)
	for( cellkind = 0; cellkind < nrcells.length; cellkind ++ ){
		this.Cim.drawCells( cellkind+1, colfun)
		// Draw borders if required
		if(  cellborders[ cellkind  ]  ){
			this.Cim.drawCellBorders( cellkind+1, "000000" )
		}
	}
}

const cmap = new CPM.ColorMap({
		colormap: 'viridis',
		nshades: 100,
		format: 'hex', 
		alpha: 1
})

function getColor (cid) {
	if (!showYcolors){
		return this.conf["CELLCOLOR"][this.C.cellKind(cid)-1]
	}
	let cell = this.C.cells[cid]
	let c = Math.floor(cell.Y *3) 
	if (c >= cmap.length){
		c = cmap.length - 1
	} else if (c < 0){
		c = 0
	}
	return cmap[c].substring(1)
}

sim.run()
