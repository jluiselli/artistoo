"use strict"

import SubCell from "../SubCell.js" 
import DNA from "./DNA.js" 

class Mitochondrion extends SubCell {

	/* eslint-disable */ 
    constructor (conf, kind, id, C) {
		super(conf, kind, id, C)
        
		this.DNA = new Array(this.conf["N_INIT_DNA"]).fill(new DNA(this.conf, this.C));

        // this.oxphos = this.conf["INIT_OXPHOS"]
        this.V = this.conf["INIT_MITO_V"]

        this.products = new Array(this.conf["N_OXPHOS"]+this.conf["N_TRANSLATE"]+this.conf["N_REPLICATE"]).fill(0)
        for (let i = 0 ; i < this.products.length; i++){
            if (i < this.conf["N_OXPHOS"] ){
                this.products[i] = this.conf["INIT_OXPHOS"]
            } else if (i < this.conf["N_TRANSLATE"]){
                this.products[i] = this.conf["INIT_TRANSLATE"]
            } else {
                this.products[i] = this.conf["INIT_REPLICATE"]
            }
        }
	}
	
	clear(){
        this.DNA = []
        this.products = new Array(this.conf["N_OXPHOS"]+this.conf["N_TRANSLATE"]+this.conf["N_REPLICATE"]).fill(0)
	}

    birth(parent, partition = 0.5){
        super.birth(parent)
		this.clear()
		this.divideProducts(parent.products, this.products, partition)
	   
		let new_parent = []
        for (let dna of parent.DNA){
            if (this.C.random() < partition){
				this.DNA.push(dna)
            } else {
                new_parent.push(dna)
            }   
		}
		parent.DNA = new_parent
		
		this.V = parent.V * partition
        parent.V *= 1-partition
    }

    /* eslint-disable*/
    update(){
        let dV = 0
        dV += this.oxphos * this.conf["MITO_V_PER_OXPHOS"]
        if (this.oxphos < this.conf["MITOPHAGY_THRESHOLD"]) {
            dV -= this.conf["MITOPHAGY_SHRINK"]   
        }
        dV-=this.conf["MITO_SHRINK"]
        dV = Math.min(this.conf["MITO_GROWTH_MAX"], dV)
        if (Math.abs(this.V - this.vol) < 10){
            this.V += dV
        }
        this.repAndTranslate()
        this.deprecateProducts()
	}

   
    divideProducts(parent_arr, child_arr, partition){
        for (const [ix, product] of parent_arr.entries()){
            for (let i = 0; i < product; i ++){
                if (this.C.random() < partition){
                    parent_arr[ix]--
                    child_arr[ix]++
                }
            }
        }  
    }

    deprecateProducts(){
        for (const [ix, product] of this.products.entries()){
            this.products[ix] -= this.binomial(product, this.conf['deprecation_rate'])
        }
        for (let i = 0; i < this.DNA.length; i++){
            if (this.C.random() < this.conf["dna_deprecation_rate"]){
                this.DNA.splice(i, 1)
            }
        }
    }

    fuse(partner) {
        this.products = this.products.map(function (num, idx) {
            return num + partner.products[idx];
        })
        this.DNA = [...this.DNA, ...partner.DNA]
        this.V += partner.V
    }

    heteroplasmy(){
        // compute heteroplasmy
        if (this.DNA.length == 0){
            return NaN
        }
        let all_proteins = new DNA(this.conf, this.C).sumQuality()
        let heteroplasmy = 0
        for (let dna of this.DNA){
            heteroplasmy += (all_proteins - dna.sumQuality() )/all_proteins
            // console.log(all_proteins - dna.sumQuality() )
        }
        return 1 - (heteroplasmy/this.DNA.length)
    }

    tryIncrement(){
        // console.log(this.sum, this.vol, this.vol/this.sum)
        return (this.C.random() < (this.vol/this.sum))
    }

    // should be refactored away
    get sum(){
        return this.products.reduce((t, e) => t + e)
    }

    /**
     * @return {Number}
     */
    get vol(){
        return this.C.getVolume(this.id)
    }

    repAndTranslate() {
        if (this.DNA.length == 0 ){ return }
       
        // takes bottleneck as rate
        let replicate_attempts = Math.min.apply(Math, this.replication_products), translate_attempts = Math.min.apply(Math, this.translate_products)
        // replication and translation machinery try to find DNA to execute on

        while ((replicate_attempts + translate_attempts) > 0){
            let ix = Math.floor(this.C.random() * this.DNA.length)
            if (this.C.random() < replicate_attempts/(replicate_attempts + translate_attempts)){
                if (this.DNA[ix].notBusy()){ this.DNA[ix].replicateFlag = true}
                replicate_attempts--
            } else {
                if (this.DNA[ix].notBusy()){this.DNA[ix].translateFlag = true}
                translate_attempts-- 
            }
        }

        for (let dna of this.DNA){
            if (dna.translateFlag){
                if (this.C.random() < this.conf['translation_rate']){
                    for (const [ix, val] of dna.quality.entries()){
                        if (val &&  this.tryIncrement()){
                           this.products[ix] += val
                        }
                    } 
                    // this.products = this.products.map(function (num, idx) {
                    //     return num + dna.quality[idx];
                    // })
                }
                dna.translateFlag = false
            } else if (dna.replicateFlag) { 
                // if (this.C.random() < this.conf['replication_rate'] && this.tryIncrement()){
                if (this.C.random() < this.conf['replication_rate']){
                    this.DNA.push(new DNA(this.conf, this.C, dna))
                }
                dna.replicateFlag = false
            }
        }
    }

    get oxphos_products() {
        return this.products.slice(0, this.conf["N_OXPHOS"])
    }
    get translate_products() {
        return this.products.slice(this.conf["N_OXPHOS"], this.conf["N_OXPHOS"] + this.conf["N_TRANSLATE"])
    }
    get replication_products() {
        return this.products.slice(this.conf["N_OXPHOS"] + this.conf["N_TRANSLATE"] )
    }
    get replicate_products(){
        return this.replication_products()
    }
    get oxphos(){
        return Math.min.apply(Math, this.oxphos_products)
    }
    
    /* eslint-disable */
    binomial(n, p){
        let log_q = Math.log(1.0-p), k = 0, sum = 0
        for (;;){
            sum += Math.log(this.C.random())/(n-k)
            if (sum < log_q){
                return k
            }
            k++
        }
    }
}

export default Mitochondrion