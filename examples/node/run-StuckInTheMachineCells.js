let CPM = require("../../build/artistoo-cjs.js")


/*	----------------------------------
	CONFIGURATION SETTINGS
	----------------------------------
*/
let config = {

	// Grid settings
	ndim : 2,
	field_size : [1920,1080],
	
	// CPM parameters and configuration
	conf : {
		// Basic CPM parameters
		torus : [true,true],				// Should the grid have linked borders?
		seed : 1,							// Seed for random number generation.
		T : 2,								// CPM temperature
		
		CELLS : [NaN, CPM.Cell],
		// Constraint parameters. 
		// Mostly these have the format of an array in which each element specifies the
		// parameter value for one of the cellkinds on the grid.
		// First value is always cellkind 0 (the background) and is often not used.

		IMG_MODE : [NaN,"RGB"],
        IMG_LAMBDA : [0, 1],
		IMG_PATH : "./input/1080bmps/075.bmp",
		IMG_CELL : [true, true],
   
		LAMBDA_ACT : [0,100],				// ActivityConstraint importance per cellkind
		MAX_ACT : [0, 30],					// Activity memory duration per cellkind
		ACT_MEAN : "geometric",				// Is neighborhood activity computed as a
				
		// Adhesion parameters:
		J : [ 
			[NaN,10],
			[10, 10]
		],
		
		// VolumeConstraint parameters
		LAMBDA_V : [0,50],					// VolumeConstraint importance per cellkind
		V : [0,180],						// Target volume of each cellkind
		

		
		// // PerimeterConstraint parameters
		// LAMBDA_P : [0,0, ],					// PerimeterConstraint importance per cellkind
		// P : [0,145] 						// Target perimeter of each cellkind

	},
	
	// Simulation setup and configuration
	simsettings : {
	
		// Cells on the grid
		NRCELLS : [6000],					// Number of cells to seed for all
		// non-background cellkinds.
		// Runtime etc
		BURNIN : 0,
		RUNTIME : 100000000,
		RUNTIME_BROWSER : "Inf",
		
		// Visualization
		CANVASCOLOR : "CCCCCC",
		CELLCOLOR : ["#CCEEFF"],
		ACTCOLOR : 	[false],		// Should pixel activity values be displayed?
		// SHOWBORDERS : [false , false, false , false, false , false],				// Should cellborders be displayed?
		SHOWBORDERS : [false],	
		zoom : 2,							// zoom in on canvas with this factor.
	

		// Output images
		SAVEIMG : true,					// Should a png image of the grid be saved
		// during the simulation?
		IMGFRAMERATE : 1,					// If so, do this every <IMGFRAMERATE> MCS.
		SAVEPATH : "output/img/StuckInTheMachine",	// ... And save the image in this folder.
		EXPNAME : "StuckInTheMachine",					// Used for the filename of output images.
		
		// Output stats etc
		STATSOUT : { browser: false, node: true }, // Should stats be computed?
		LOGRATE : 10							// Output stats every <LOGRATE> MCS.

	}
}
/*	---------------------------------- */
let custommethods = {
	drawCanvas : drawCanvas,
	initializeGrid : initializeGrid,
    postMCSListener : postMCSListener,
    logStats : logStats
    }

let sim = new CPM.Simulation( config, custommethods )

let imgconstraint = new CPM.ImageConstraint( config.conf 
    )
sim.C.add( imgconstraint )

function pad(number, length) {
	var str = '' + number;
	while (str.length < length) {
	  str = '0' + str;
	}
	return str;
}

function logStats(){
	console.log(this.C.time)
}
var filenum = 105
function postMCSListener(){
	if (this.C.time < 20){
		return
	} 
	if (this.C.time % 20 == 0) {
		++filenum
		imgconstraint.setImage("./input/1080bmps/"+pad(filenum, 3)+".bmp")
		console.log("changed img to " + "./input/1080bmps/"+pad(filenum, 3)+".bmp")
	}
}


/* The following custom methods will be added to the simulation object
below. */
function initializeGrid(){
	// add the initializer if not already there
	if( !this.helpClasses["gm"] ){ this.addGridManipulator(); }

	// reset C and clear cache (important if this method is called
	// again later in the sim).
	this.C.reset();

	let nrcells = this.conf["NRCELLS"], cellkind, i;
	
	// Seed the right number of cells for each cellkind
	for( cellkind = 0; cellkind < nrcells.length; cellkind ++ ){
		
		for( i = 0; i < nrcells[cellkind]; i++ ){
			// first cell always at the midpoint. Any other cells
			// randomly.				
			
			let nid = this.gm.seedCell( cellkind+1 );
			this.C.cells[nid].R = Math.floor(this.C.random() * 256)
			// let lum = Math.floor(this.C.random() * this.C.cells[nid].B *0.4)
			
			this.C.cells[nid].G =Math.floor(this.C.random() * 256)
			this.C.cells[nid].B =Math.floor(this.C.random() * 256)
			// let lum = this.C.random()
			// this.C.cells[nid].R = Math.floor(this.C.cells[nid].R * lum) 
			// this.C.cells[nid].G = Math.floor(this.C.cells[nid].G * lum) 
			// this.C.cells[nid].B = Math.floor(this.C.cells[nid].B * lum) 
			// this.C.cells[nid].R = lum
			// this.C.cells[nid].G =lum
			// this.C.cells[nid].B =0
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

function getColor (cid) {
	let cell = this.C.cells[cid]
	return rgbToHex(cell.R, cell.G, cell.B)
}
function componentToHex(c) {
	var hex = c.toString(16);
	return hex.length == 1 ? "0" + hex : hex;
  }
  
  function rgbToHex(r, g, b) {
	return  componentToHex(r) + componentToHex(g) + componentToHex(b);
  }
  

// /* The following custom methods will be added to the simulation object
// below. */
// function initializeGrid(){
// 	// Seed epidermal cell layer
// 	let step = 12
	
// 	for( let i = 1 ; i < this.C.extents[0] ; i += step ){
// 		for( let j = 1 ; j < this.C.extents[1] ; j += step ){
// 			this.C.setpix( [i,j], this.C.makeNewCellID(1) )
// 		}
// 	}
// }



sim.run()
