"use strict"

import SuperCell from "../SuperCell.js" 
import nDNA from "./nDNA.js"


class HostCell extends SuperCell {

	/* eslint-disable */ 
	constructor (conf, kind, id, C) {
		super(conf, kind, id, C)
		this.V = conf["INIT_HOST_V"]
		for (let evolvable in conf['evolvables']){
			this[evolvable] = conf[evolvable]
		}
		
		this.total_oxphos = 0
		this.DNA = new nDNA(conf, C) 
		this.cytosol = new Array(this.conf["N_OXPHOS"]+this.conf["N_TRANSLATE"]+this.conf["N_REPLICATE"]).fill(0)
		
		this.fission_events = 0
		this.fusion_events = 0
	}

	birth(parent, partition){
		super.birth(parent, partition)
		this.V = parent.V * partition
        parent.V *= (1-partition)
		this.DNA = new nDNA(this.conf, this.C, parent.DNA)
		for (const [ix, product] of parent.cytosol.entries()){
            for (let i = 0; i < product; i ++){
                if (this.C.random() < partition){
                    parent.cytosol[ix]--
                    this.cytosol[ix]++
                }
            }
		}  
		
		for (const evolvable in this.conf['evolvables']){
			this[evolvable] = parent.cellParameter(evolvable)
			this[evolvable] += this.conf['evolvables'][evolvable] * this.rand_normal()
		}

		// console.log(this.stateDct())
		this.write("divisions.txt", {"daughter":this.stateDct(), "parent":parent.stateDct()})
	}

	update(){
		
		if (this.nSubcells === 0 ){
			// console.log(this.V, this.vol)
			if (this.canShrink()){
				this.V -= this.cellParameter("HOST_SHRINK")
			}
			return
		}
		this.total_oxphos = 0

		let cells = [], volcumsum = []
		let mito_vol = 0
		for (let mito of this.subcells()){
			cells.push(mito) //need to link id in a structured format to pick from volcumsum
			mito_vol += mito.vol
			volcumsum.push(mito_vol)
			mito.update()
			this.total_oxphos += mito.oxphos
		}
		
		
		let new_products = (this.total_oxphos*this.cellParameter("rep")) - (this.total_oxphos*this.total_oxphos*this.cellParameter("rep2"))
		volcumsum = volcumsum.map(function(item) {return item/ mito_vol})
		for (let i = 0; i < new_products; i++){
			let ix = this.DNA.trues[Math.floor(this.C.random() * this.DNA.trues.length)]
			let which = volcumsum.findIndex(element => this.C.random()  < element )
			cells[which].proteinbuffer.push({"which":ix, "good" : true}) //currently all nDNA is good, watch out for this when starting host mutation!
		}


		let dV = 0
		dV += this.total_oxphos *this.cellParameter("HOST_V_PER_OXPHOS")
		dV -= this.cellParameter("HOST_SHRINK")
		dV = Math.min(this.cellParameter("HOST_GROWTH_MAX"), dV)
		// if (dV > 0 && this.canGrow() && mito_vol/(this.vol + mito_vol) > this.conf["PREF_FRACTION_MITO_PER_HOST"] ){
		if (dV > 0 && this.canGrow() ){
            this.V += dV
        }
        if (dV < 0 && this.canShrink()){
            this.V += dV
		}
		if (dV < 0 && !this.canShrink()){
			for (let mito of this.subcells()){
				mito.V += (mito.vol/mito_vol) * dV *this.conf["FACTOR_HOSTSHRINK_OVERFLOW"]
			}
		}

		
		for (let mito of this.subcells()){
			mito.importAndProduce()
		}
		for (const [ix, product] of this.cytosol.entries()){
			for (let i = 0 ; i < product;i++){
				if( this.C.random() < this.cellParameter("HOST_DEPRECATION")){
					this.cytosol[ix]--
				}
			}
		}
	}


	
	tryIncrement(){
        return (this.C.random() < (this.vol/this.sum))
	}
	
	get sum(){
		return this.cytosol.reduce((t, e) => t + e)
	}

	get total_vol(){
		let vol = this.vol
		for (let subcell of this.subcells()){
			vol += subcell.vol
		}
		return vol
	}

	death(){
		/* eslint-disable */
		super.death()
		for (let mito of this.subcells()){
			this.write("debug.log", {"message": "Host died with extant subcells, please mind the balance in your model", "cell" : this.stateDct()})
			mito.V = -50 // if this is necessary coul
		}
		this.write("./deaths.txt", this.stateDct()) 
	}

	shuffle(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(this.C.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
	}
	
	// Standard Normal variate using Box-Muller transform.
	rand_normal() {
		let u = 0, v = 0;
		while(u === 0) u = this.C.random(); //Converting [0,1) to (0,1)
		while(v === 0) v = this.C.random();
		return Math.sqrt( -2.0 * Math.log( u ) ) * Math.cos( 2.0 * Math.PI * v );
	}

	stateDct() {
		let dct = {}
		dct["time"] = this.C.time
		dct["id"] = this.id
        dct["V"] = this.V
		dct["vol"] = this.vol
		dct["parent"] = this.parentId
		dct["time of birth"] = this.time_of_birth

		// host specific
		dct["type"] = "host"
		dct["n mito"] = this.nSubcells
		dct["total_oxphos"] = this.total_oxphos
		dct["cytosolsum"] = this.sum
		dct['total_vol'] = this.total_vol
		dct["fission events"] = this.fission_events
		dct["fusion events"] = this.fusion_events
		dct['evolvables'] = {}
		for (const evolvable in this.conf.evolvables){
			dct['evolvables'][evolvable] = this[evolvable]
		}
		return dct
	}

	write(logpath, dct){
        let objstring = JSON.stringify(dct) + '\n'
		if( typeof window !== "undefined" && typeof window.document !== "undefined" ){
        } else {
            if (!this.fs){
                this.fs = require('fs')
            }    
            this.fs.appendFileSync(logpath, objstring)
		}   
	}
}

export default HostCell