"use strict"

import SubCell from "../SubCell.js" 
import ProteicComplex from "./ProteicComplex.js"
import mtDNA from "./mtDNA.js" 
import Products from "./Products.js" 

/**
 * Simulates mitochondria in combination with HostCell
 * This inherits from SubCell, which handles which host it
 * belongs to (note: setting the first host during seeding is still required)
 */
class Mitochondrion extends SubCell {

	/**
     * Constructor for Mitochondrion
     * -- standard CPM.Cell parameters:
     * @param {Object} conf - config of the model
     * @param {Number} kind - the CellKind of this
     * @param {Number} id - the CellId of this
     * @param {CPMEvol} C - the CPMEvol (or inherited) model where it is attached to
     * 
     * - specific conf parameters necessary --
     * - initialization -
     * @param {Number} conf.N_INIT_DNA - initial number of mtDNA copies
     * @param {Number} conf.INIT_MITO_V - initial target Volume at t=0
     * - growth -
     * @param {Number} conf.MITO_V_PER_OXPHOS - scalar value for amount of ∆V the mitochondrion gets per oxphos
     * @param {Number} conf.MITO_SHRINK - shrinkage in ∆V (expects positive value)
     * @param {Number} conf.MITO_GROWTH_MAX - max amount of ∆V per timestep
     * - mitophagy -
     * @param {Number} conf.MITOPHAGY_THRESHOLD - amount of oxphos under which conf.MITOPHAGY_SHRINK will be applied
     * @param {Number} conf.MITOPHAGY_SHRINK - shrinkage that is only applied with oxphos < conf.MITOPHAGY_THRESHOLD
     * - proteolysis -
     * @param {Number} conf.deprecation_rate - rate at which proteins are proteolysed/removed from the Mitochondrion (/MCS/gene product)
     * - mutation -
     * @param {Number} conf.MTDNA_MUT_INIT - initial mtDNA mutation /gene at t=0 
     * @param {Number} conf.MTDNA_MUT_REP - mtDNA mutation /gene/replication event, only new daughter is affected
     * @param {Number} conf.MTDNA_MUT_ROS - mtDNA mutation rate /gene/ROS 
     * -
     * @param {Number} conf.REPLICATE_TIME - the number of timesteps an mtDNA replication event takes.
     * 
     * Any parameters can also be controlled by the HostCell through 'evolvables' - but this still requires an 
     * initial value to be present in the conf object
	 * 
     */
	constructor (conf, kind, id, C) {
		super(conf, kind, id, C)
        
		/** initialize DNA + mutate this initial pool */
		/** tracks how many new dna's have come from this mitochondrion (does not track well with fusion)
         * is meant to at least allow fully unique DNA id's
         * @type {Number} */
		this.last_dna_id = 0

		/** All mtDNA copies
         * @type {Array} containing @type {DNA} Objects
        */
		this.DNA = []
		for (let i= 0; i<this.conf["N_INIT_DNA"];i++){
			let dna = new mtDNA(this.conf, this.C, String(this.id) +"_"+ String(++this.last_dna_id))
			dna.mutate(this.conf["MTDNA_MUT_INIT"])
			this.DNA.push(dna) // new js object arrays need to be filled one-by-one to not add the same object multiple times
		}
        
		/** Target volume @type {Number}*/
		this.V = this.conf["INIT_MITO_V"]

		/** boolean to set whether this mitochondrion is currently fusing
         * this is used to not record fusion events as death events (as a mitochondrial id does disappear)
         * @type {boolean}
         */
		this.fusing = false

		/**
         * buffer for all imported and produced proteins per timestep
         * This is to ensure import and production have a similar priority for the carrying capacity
         * @type {Array}
         */
		this.proteinbuffer = []
		/** to get oxphos average readouts, record last 5 MCS oxphos in this @type {Array} */
		this.oxphos_q = new Array(5).fill(0)

		/** save time of birth @type {Number} */
		this.time_of_birth = this.C.time
        
		/**
         * Holder for all gene products from nonmutated genes 
         * @type {Products} - a wrapper for an array of integers
         */
		this.products = new Products(this.conf, this.C)
		/** set initial numbers at start of run 
         *  NOTE: this is called in  construction - so needs to be removed for any other birth event
         */
		this.products.init()
		/**
         * Holder for all gene products from mutated genes 
         * @type {Products}- a wrapper for an array of integers
         */
		this.bad_products = new Products(this.conf, this.C)

		/**
		 * Array containing all proteic complexes
		 * @type {Array}
		 */
		this.complexes = []

		this.oxphos_cplx = 0 // Number of viable metabolic complexes
		this.total_oxphos = 0 // Total number of metabolic complexes (for ROS production)
		this.replicate_cplx = 0 // Number of viable replication complexes
		this.translate_cplx = 0 // Number of viable translation complexes
		this.makeAssemblies()
		
	}
	
	/**
     * Clear this cell from any initialization 
     * TODO: make it so init() is called on initialization, and this is default, seems less likely to cause problems
     * esp. because hosting is already a seeding-specific action
     */
	clear(){
		this.DNA = []
		this.products = new Products(this.conf, this.C)
		this.bad_products = new Products(this.conf, this.C)
		this.complexes = []
	}

	/** Get standard Normal variate from univariate using Box-Muller transform.
	 *  Code edited from https://stackoverflow.com/questions/25582882/javascript-math-random-normal-distribution-gaussian-bell-curve
	 */ 
	rand_normal() {
		let u = 0, v = 0
		while(u === 0) u = this.C.random() //Converting [0,1) to (0,1)
		while(v === 0) v = this.C.random()
		return Math.sqrt( -2.0 * Math.log( u ) ) * Math.cos( 2.0 * Math.PI * v )
	}

	/**
     * Birth call on new mitochondrion, handles stochastic division of products and 
     * mtDNA copies. 
     * @param {Mitochondrion} parent - the other daughter of division (not newly created)
     * @param {Number} partition - the fraction of the pixels this daughter received
     */
	birth(parent, partition){
		/** handle superclass things */
		super.birth(parent)
		/** clear unnecessary initialization */
		this.clear()

		/** stochastically divide products between daughters with rate partition */
		this.divideProducts(parent.products, this.products, partition)
		this.divideProducts(parent.bad_products, this.bad_products, partition)

		/** stochastically divide mtDNA copies between daughters with rate partition */
		let new_parent = []
		for (let dna of parent.DNA){
			if (this.C.random() < partition){
				this.DNA.push(dna)
			} else {
				new_parent.push(dna)
			}
		}
		parent.DNA = new_parent

		/** stochastically divide complexes between daughters with rate partition */
		let new_complexes = []
		for (let cplx of parent.complexes){
			if (this.C.random() < partition){
				this.complexes.push(cplx)
			} else {
				new_complexes.push(cplx)
			}
		}
		parent.complexes = new_complexes

		parent.recountComplexes()
		this.recountComplexes()

		/** alter target volume */
		this.V = parent.V * partition
		parent.V *= (1-partition)
		//unused assemblies that cause less visualization errors:
		this.makeAssemblies()
		parent.makeAssemblies()

	}

	/**
     * death listener for Mitochondrion -also catches fusion events
     * Writes state to file deaths.txt if actually death event
     */
	death(){
		super.death()
		if (this.fusing){
			return
		}

		this.write("./Mit_deaths.txt", this.stateDct())
	}


	recountComplexes(){
		let ox = 0; let tr = 0; let rep = 0; let tot_ox = 0
		for (let i = 0; i<this.complexes.length; i++){
			if (this.complexes[i].t == 0 && this.complexes[i].bad_pos.length == 0){
				ox++
			}
			else if (this.complexes[i].t == 1 && this.complexes[i].bad_pos.length == 0){
				tr++
			}
			else if (this.complexes[i].t == 2 && this.complexes[i].bad_pos.length == 0){
				rep ++
			}
			if (this.complexes[i].t == 0){
				tot_ox++
			}
		}
		this.oxphos_cplx = ox
		this.translate_cplx = tr
		this.replicate_cplx = rep
		this.total_oxphos = tot_ox
	}


	checkComplexes(){
		let ox = 0; let tr = 0; let rep = 0
		for (let i = 0; i<this.complexes.length; i++){
			if (this.complexes[i].t == 0 && this.complexes[i].bad_pos.length == 0){
				ox++
			}
			else if (this.complexes[i].t == 1 && this.complexes[i].bad_pos.length == 0){
				tr++
			}
			else if (this.complexes[i].t == 2 && this.complexes[i].bad_pos.length == 0){
				rep ++
			}
		}
		if (this.oxphos_cplx != ox){
			console.log("wrong number of oxphos cplx")
			throw " "
		}
		if (this.translate_cplx != tr){
			console.log("wrong number of translation cplx")
			throw " "
		}
		if (this.replicate_cplx != rep){
			console.log("wrong number of replication cplx")
			throw " "
		}
	}

	/**
     * update loop of Mitochondrion
     * should be called by host for orderly working
     */
	update(){
		/** do proteolysis - Put at the beginning to happen *after* fusion/fission */

		/** sets this timesteps oxphos, translate and replicate capability
         * which are drawn from the gene products pool
        */
		this.makeAssemblies()

		/**
         * do ∆V 
         */
		let dV = 0
		dV += this.oxphos * this.cellParameter("MITO_V_PER_OXPHOS")
		dV-= this.cellParameter("MITO_SHRINK")
		dV = Math.min(this.cellParameter("MITO_GROWTH_MAX"), dV)
		// optional mitophagy thresholding
		if (this.oxphos < this.cellParameter("MITOPHAGY_THRESHOLD")) {
			dV -= this.cellParameter("MITOPHAGY_SHRINK")
		}
		if (this.closeToV()){
			this.V += dV
		}

		/** replicate mtdna and translate mtdna into proteinbuffer */
		this.repAndTranslate()

		this.deprecateProducts()
		this.deprecateComplexes()
		this.mutateDNA()
		this.mutateProducts()
		this.mutateComplexes()
		
		/** add newly produced products only once all import also has been created */
		// importandcreate() - called by host, as this controls import!
		// these lines are only here to show program flow
	}

	/**
     * Divide products array stochastically based on the partition
     * of the two vesicles. 
     * @param {Products} parent_products - original Mitochondrion's products
     * @param {Products} child_products - new Mitochondrion's products
     * @param {Number} partition - new Mitochondrion's fraction of pixels after division (used as rate)
     */
	divideProducts(parent_products, child_products, partition){
		// loops over each object and adds it to new daughter with rate partition
		for (const [ix, product] of parent_products.arr.entries()){
			for (let i = 0; i < product; i ++){
				if (this.C.random() < partition){
					parent_products.arr[ix]--
					child_products.arr[ix]++
				}
			}
		}  
	}

	/**
     * Remove products with rate 'deprecation rate' 
     */
	deprecateProducts(){
		this.products.deprecate(this.cellParameter("deprecation_rate"))
		this.bad_products.deprecate(this.cellParameter("deprecation_rate"))
	}

	/**
	 * Mutate DNA with ROS
	 */
	mutateDNA(){        
		for (let dna of this.DNA.values()){
			dna.mutate(this.cellParameter("MTDNA_MUT_ROS") * this.ros)
		}
		let mutated_prot = this.products.mutate(Math.min(0.9999,this.cellParameter("PROT_MUT_ROS") * this.ros))
		this.products.remove(mutated_prot)
		this.bad_products.add(mutated_prot)
	}

	/**
	 * Mutate Products with ROS
	 */
	mutateProducts(){        
		let mutated_prot = this.products.mutate(Math.min(0.9999,this.cellParameter("PROT_MUT_ROS") * this.ros))
		this.products.remove(mutated_prot)
		this.bad_products.add(mutated_prot)
	}

	/**
	 * Mutate Complexes with ROS
	 */
	mutateComplexes(){        
		for (const [idx, cplx] of this.complexes.entries()){
			cplx.mutate(Math.min(0.9999,this.cellParameter("PROT_MUT_ROS") * this.ros))
		}
	}


	deprecateComplexes(){
		let deleted_p = [] // temporary storage of the id of the protein that was suppressed
		let destroyed_cplx = [] // total number of destroyed complexes
		for (const [idx, cplx] of this.complexes.entries()){
			deleted_p = cplx.deprecate(this.cellParameter("deprecation_rate"))
			if (deleted_p.length != 0){
				// add the remaining proteins to the pull of products
				for (let i = 0; i < cplx.l; i++){
					if (cplx.bad_pos.includes(i) && !deleted_p.includes(i)){
						// If the protein was bad and is not deleted
						this.bad_products.arr[i+cplx.start]++
					}
					else if (!deleted_p.includes(i)) {
						// If the protein was good and is not deleted
						this.products.arr[i+cplx.start]++
					}
				}
				if (cplx.bad_pos.length == 0){ // Only good complexes were counted
					if (cplx.t == 0){ this.oxphos_cplx-- }
					else if (cplx.t == 1){ this.translate_cplx-- }
					else if (cplx.t == 2){ this.replicate_cplx-- }
				}
				if (cplx.t == 0){ this.total_oxphos-- }
				destroyed_cplx.push(idx)
			}
		}
		let acc = 0
		for (let j =0; j<destroyed_cplx.length; j++){
			let i=destroyed_cplx[j]

			this.complexes = [...this.complexes.slice(0,i-acc), ...this.complexes.slice(i+1-acc)]
			acc++
		}

	}

	/**
     * Do all internal processes of fusing:
     * combine Products 
     * combine target volume
     * combine mtDNA
	 * combine Proteic complexes
     * @param {Mitochondrion} partner 
     */
	fuse(partner) {
		this.products.arr = this.sum_arr(this.products.arr, partner.products.arr)
		this.bad_products.arr = this.sum_arr(this.bad_products.arr, partner.bad_products.arr)

		this.DNA = [...this.DNA, ...partner.DNA]
		this.complexes = [...this.complexes, ...partner.complexes]
		this.V += partner.V
		partner.fusing = true // partner will be deleted - but does not die - this flags this process
		this.oxphos_cplx += partner.oxphos_cplx
		this.translate_cplx += partner.translate_cplx
		this.replicate_cplx += partner.replicate_cplx
		this.total_oxphos += partner.total_oxphos
	}

	/**
     * Do all internal processes of sharing:
     * combine Products and form complexes
     * combine mtDNA
     *  * divide mtDNA, Products dans complexes
     * @param {Mitochondrion} partner 
     */
	share(partner) {
		// console.log("sharing ", this.id, "with", partner.id)
		// console.log(this.products.arr, this.bad_products.arr)
		/** add things */
		// console.log("before sharing",this.oxphos_cplx,
		// 	this.translate_cplx,
		// 	this.replicate_cplx,
		// 	this.total_oxphos)
		this.products.arr = this.sum_arr(this.products.arr, partner.products.arr)
		this.bad_products.arr = this.sum_arr(this.bad_products.arr, partner.bad_products.arr)
		this.DNA = [...this.DNA, ...partner.DNA]
		this.complexes = [...this.complexes, ...partner.complexes]
		this.oxphos_cplx += partner.oxphos_cplx
		this.translate_cplx += partner.translate_cplx
		this.replicate_cplx += partner.replicate_cplx
		this.total_oxphos += partner.total_oxphos
		// console.log("common complexes",this.oxphos_cplx,
		// 	this.translate_cplx,
		// 	this.replicate_cplx,
		// 	this.total_oxphos)
		/** Clear partner of this products, complexes and DNA */
		partner.clear()
	
		/** Form potention new complexes */
		this.makeAssemblies()

		/** Separate everything again based on their respective volume */
		let partition = partner.vol/(this.vol + partner.vol) // propotion of things that should go to partner
		// console.log(this.vol, partner.vol, partition)
		this.divideProducts(this.products, partner.products, partition)
		this.divideProducts(this.bad_products, partner.bad_products, partition)

		/** stochastically divide mtDNA copies between the 2 mitochondria */
		let this_cell = []
		let new_partner = []
		for (let dna of this.DNA){
			if (this.C.random() < partition){
				new_partner.push(dna)
			} else {
				this_cell.push(dna)
			}
		}
		partner.DNA = new_partner
		this.DNA = this_cell

		/** stochastically divide complexes between mitochondria */
		let new_partner_complexes = []
		let new_complexes = []
		for (let cplx of this.complexes){
			if (this.C.random() < partition){
				new_partner_complexes.push(cplx)
				
			} else {
				new_complexes.push(cplx)
			}
		}
		partner.complexes = new_partner_complexes
		this.complexes = new_complexes

		/** Update nb of complexes */
		partner.recountComplexes()
		this.recountComplexes()
		// console.log("after division",this.oxphos_cplx,
		// 	this.translate_cplx,
		// 	this.replicate_cplx,
		// 	this.total_oxphos)
	}

	/**
     * Checks against carrying capacity (defined by volume) whether the current product can be added
     * @returns {Boolean} - whether the addition is successful
     */
	tryIncrement(){
		let total_products = this.sum_arr(this.products.arr, this.bad_products.arr).reduce((t, e) => t + e)
		// number of free proteins
		for ( let cplx of this.complexes.values() ){
			total_products += cplx.l
			// adding proteins from the complexes to the count
		}
		return this.C.random() < (this.vol / total_products)
	}

	/**
     * Reimplements CPM.Cell implementation to ask Host cell
     * returns conf value if host not extant
     * TODO add all parameters at birth to mito so they stay with extant subcells after host death
	*/
	cellParameter(param){
		if (this.C.cells[this.host] !== undefined){
			return this.C.cells[this.host].cellParameter(param)
		}
		return this.conf[param]
	}

	/** gets number of replicating DNA copies
     */
	get n_replisomes(){ 
		return this.DNA.reduce((t,e) =>  e.replicating > 0 ? t+1 : t, 0)
	}

	/** gets number of unmutated DNA copies */
	get unmutated(){
		return this.DNA.reduce((t,e) =>  e.sumQuality() == new mtDNA(this.conf, this.C).sumQuality() ? t+1 : t, 0)
	}

	/**
     * Imports and Produces gene products from proteinbuffer in random order
     * Checks against carrying capacity.
     * 
     * Shuffles and then just works throught the proteinbuffer based on @function tryIncrement()
     * Rejected proteins are removed from the model
     */
	importAndProduce(){
		this.shuffle(this.proteinbuffer)
		while (this.proteinbuffer.length > 0){
			let p = this.proteinbuffer.pop()
			if (this.tryIncrement(p.which)){
				if (p.good){
					this.products.arr[p.which]++
				} else {
					this.bad_products.arr[p.which]++
				}
			} 
		}
	}

	/**
     * Replicate and translate mtDNA  
     * based on attempts gathered from @function makeAssemblies()
     */
	repAndTranslate() {
		if (this.DNA.length == 0 || this.complexes.length == 0 ){ return }
		let replicate_attempts = this.replicate_cplx, translate_attempts = this.translate_cplx // shallow copies
		// replication and translation machinery try to find DNA to execute on
		/** shuffle DNA in place to make sure that ordering does not affect translation */
		this.shuffle(this.DNA) 

		/** new dna is initizalized and not yet translatable @type {[DNA]} */
		let new_dna = []
		/** Finish up all replicating mtDNA before starting a new one */
		for (let dna of this.DNA){
			if (replicate_attempts <= 0){
				break
			}
			if (dna.replicating > 0){
				replicate_attempts--
				dna.replicating--
				if (dna.replicating == 0){
					new_dna.push(new mtDNA(this.conf, this.C, String(this.id) + "_" + String(++this.last_dna_id), dna)) 
				}
			}
		}
        
		/** Start new replication attempts and do translation events
         * NOTE:  replication only blocks translation on the first step, which is 
		 * weird! it might be good to go back to mutex replication/translation 
         * anyway as this is more like the biological system (although it is
         * harder with the proteolysis and division of replisome machinery)
		 * 
		 * NOTE2:
		 * Translation does all proteins of this mtDNA copy - big assumption;
		 * 
         */
		for (let dna of this.DNA){
			if (replicate_attempts + translate_attempts <= 0){
				break
			}
			/** draw from chance whether you do replication or translation */
			if (this.C.random() < replicate_attempts/(replicate_attempts + translate_attempts)){
				// start new replication event
				dna.replicating = this.cellParameter("REPLICATE_TIME")
				replicate_attempts--
			} else {
				// translate all proteins on this piece of DNA
				for (let ix = 0 ; ix < dna.quality.length; ix++){
					if (dna.exists[ix] !== 0){
						this.proteinbuffer.push({"which":ix,"good":dna.quality[ix]})
					}
				}
				translate_attempts-- 
			}
		}
		// Newly made DNA does not participate in replication/translation in t=birthtime
		this.DNA = [...this.DNA, ...new_dna]
	}

    
	/**
	 * DESCRIPTION TO DO 
     * @param {Integer} t - Type of the proteic complex.
	 * 0 = oxphos ; 1 = translate ; 2 = replicate 
     */
	assemble(t){
		let arr = []
		let bad_arr = []
		if (t == 0){	
			arr = this.products.oxphos
			bad_arr = this.bad_products.oxphos // copies
		}
		else if (t == 1){
			arr = this.products.translate
			bad_arr = this.bad_products.translate // copies
		}
		else {
			arr = this.products.replicate
			bad_arr = this.bad_products.replicate // copies
		}

		searchloop  : while (true){ // while no position is empty of proteins
			let bad_pos = [] // record positions of bad proteins
			for (let j = 0; j<arr.length; j++){
				let all_j = arr[j] + bad_arr[j]
				if (all_j == 0){ break searchloop}
				if (this.C.random() < bad_arr[j]/all_j){
					bad_arr[j]--
					bad_pos.push(j) 
				}
				else { arr[j]--	}
			}
			if (bad_pos.length == 0){ 
				if (t == 0) {
					this.oxphos_cplx++ 
				}
				else if (t == 1){
					this.translate_cplx++ 
				}
				else {
					this.replicate_cplx++ 
				}
			}

			this.complexes.push(new ProteicComplex(this.conf, this.C, t, bad_pos))
			if ( t == 0)  { this.total_oxphos++ }
		}
		// Recording changes
		if (t == 0){
			this.products.arr = [...arr, ...this.products.translate, ...this.products.replicate]
			this.bad_products.arr = [...bad_arr, ...this.bad_products.translate, ...this.bad_products.replicate]
		}
		else if (t == 1){
			this.products.arr = [...this.products.oxphos, ...arr, ...this.products.replicate]
			this.bad_products.arr = [...this.bad_products.oxphos, ...bad_arr, ...this.bad_products.replicate]
		}
		else {
			this.products.arr = [...this.products.oxphos, ...this.products.translate, ...arr]
			this.bad_products.arr = [...this.bad_products.oxphos, ...this.bad_products.translate, ...bad_arr]
		}
	}
	/**
	 * Makes assemblies
	 */
	makeAssemblies(){
		this.assemble(0) // assemble oxphos
		this.assemble(1) // assemble translate
		this.assemble(2) // assemble replicate

		// Both good and bad assemblies make ros, so the total number of assemblies (minimum of summed arrays) is total ros
		this.oxphos = this.oxphos_cplx / (this.vol / 100) * this.conf["OXPHOS_PER_100VOL"]
		this.ros = this.total_oxphos / (this.vol / 100) * this.conf["OXPHOS_PER_100VOL"]

		// this is queues over 5 timesteps for the oxphos_avg visualization
		this.oxphos_q.push(this.oxphos)
		this.oxphos_q = this.oxphos_q.slice(-5)
	}


	/** take average of last 5 oxphos calculations */ 
	get oxphos_avg() {
		return this.oxphos_q.reduce((t, e) => t + e) / 5
	}

	/** shuffle array in place */
	shuffle(array) {
		for (let i = array.length - 1; i > 0; i--) {
			const j = Math.floor(this.C.random() * (i + 1));
			[array[i], array[j]] = [array[j], array[i]]
		}
	}

	/** return the sum of two arrays at every index
     * rewritten to function because i don't like the js notation ;)
     */
	sum_arr(arr1, arr2){
		return arr1.map(function (num, idx) {
			return num + arr2[idx]
		})
	}

	/**
     * Output state of this object
     * @returns {Object} containing the state of this object at this moment for writing to file
     */
	stateDct(){
		let mito = {}
		mito["time"] = this.C.time
		mito["V"] = this.V
		mito["id"] = this.id
		mito["host"] = this.host
		mito["vol"] = this.vol
		mito["n DNA"] = this.DNA.length
		mito["oxphos"] = this.oxphos
		mito["ros"] = this.ros
		mito["oxphos_avg"] = this.oxphos_avg
		mito["translate"] = this.translate_cplx
		mito["replicate"] = this.replicate_cplx
		mito["replisomes"] = this.n_replisomes
		mito["type"] = "mito"
		mito["time of birth"] = this.C.time_of_birth
		mito["products"] = this.products.arr
		mito["bad products"] = this.bad_products.arr
		// mito['products at bad host DNA'] = this.debug_hostbad_printer()
		let sumdna = new Array(this.conf["N_OXPHOS"]+this.conf["N_TRANSLATE"]+this.conf["N_REPLICATE"]).fill(0)
		for (let dna of this.DNA){
			sumdna = this.sum_arr(sumdna, dna.quality)
		}
		mito["sum dna"] = sumdna.slice(0,10)
		mito["unmut"] = this.unmutated/this.DNA.length
		return mito
	}
    
	/**
	 * Writer for mitochondrion- could maybe be moved to CPM.Cell?
	 * takes anobject and appends it to an output file as JSON dictionary/object 
	 * @param {String} logpath - output path
	 * @param {Object} dct - output object
	 */
	write(logpath, dct){
		if (!this.fs){
			this.fs = require("fs")
		}
		if (!this.fs.existsSync(logpath)){
			let deathstr = ""
			for (let key in dct){
				deathstr += key + ";"
			}
			deathstr += "\n"
			this.fs.appendFileSync(logpath, deathstr)
		}
		let deathstr = ""
		for (let key in dct){
			if (key == "evolvables"){
				for (let key2 in dct[key]){
					deathstr += dct[key][key2]+";"
				}
			}
			else {
				deathstr += dct[key]+";"
			}
		}
		deathstr += "\n"
		this.fs.appendFileSync(logpath, deathstr)
	}  
}

export default Mitochondrion