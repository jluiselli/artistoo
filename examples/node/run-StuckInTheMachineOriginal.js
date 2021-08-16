let CPM = require("../../build/artistoo-cjs.js")


/*	----------------------------------
	CONFIGURATION SETTINGS
	----------------------------------
*/
let config = {

	// Grid settings
	ndim : 2,
	field_size : [256,144],
	
	// CPM parameters and configuration
	conf : {
		// Basic CPM parameters
		torus : [true,true],				// Should the grid have linked borders?
		seed : 1,							// Seed for random number generation.
		T : 2,								// CPM temperature
		
		// Constraint parameters. 
		// Mostly these have the format of an array in which each element specifies the
		// parameter value for one of the cellkinds on the grid.
		// First value is always cellkind 0 (the background) and is often not used.

		IMG_MODE : [NaN,"LUMINOSITY","LUMINOSITY", "LUMINOSITY","LUMINOSITY", "LUMINOSITY"],
        IMG_LAMBDA : [0, 20, 40, 60, 80, 100],
		IMG_PATH : "./input/144bmps/072.bmp",
		IMG_CELL : [true, true, true, true, true, true],
   
		LAMBDA_ACT : [0,100, 100,100, 100,100],				// ActivityConstraint importance per cellkind
		MAX_ACT : [0, 30, 30,30, 30, 30],					// Activity memory duration per cellkind
		ACT_MEAN : "geometric",				// Is neighborhood activity computed as a
				
		// Adhesion parameters:
		J : [ 
			[NaN,10, 10, 10,10, 10], 
			[10,10, 10, 10,10, 10] ,
			[10,10, 10, 10,10, 10] ,
			[10,10, 10, 10,10, 10] ,
			[10,10, 10, 10,10, 10] ,
			[10,10, 10, 10,10, 10]
		],
		
		// VolumeConstraint parameters
		LAMBDA_V : [0,50, 50,50, 50,50],					// VolumeConstraint importance per cellkind
		V : [0,152, 152, 152, 152, 152],						// Target volume of each cellkind
		

		
		// // PerimeterConstraint parameters
		// LAMBDA_P : [0,0, ],					// PerimeterConstraint importance per cellkind
		// P : [0,145] 						// Target perimeter of each cellkind

	},
	
	// Simulation setup and configuration
	simsettings : {
	
		// Cells on the grid
		NRCELLS : [ 50, 50 , 50, 50,50],					// Number of cells to seed for all
		// non-background cellkinds.
		// Runtime etc
		BURNIN : 0,
		RUNTIME : 100000000,
		RUNTIME_BROWSER : "Inf",
		
		// Visualization
		CANVASCOLOR : "CCCCCC",
		CELLCOLOR : ["#CCEEFF", "9ECCFA", "75B2F0", "5299E0", "337FCC", "336699"],
		ACTCOLOR : 	[false , false, false , false, false , false],		// Should pixel activity values be displayed?
		// SHOWBORDERS : [false , false, false , false, false , false],				// Should cellborders be displayed?
		SHOWBORDERS : [true , true, true , true, true , true],	
		zoom : 4,							// zoom in on canvas with this factor.
	

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
	if (this.C.time < 00){
		return
	} 
	if (this.C.time % 10 == 0) {
		++filenum
		imgconstraint.setImage("./input/144bmps/"+pad(filenum, 3)+".bmp")
		console.log("changed img to " + "./input/144bmps/"+pad(filenum, 3)+".bmp")
	}
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
