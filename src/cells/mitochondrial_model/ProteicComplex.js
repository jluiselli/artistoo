class ProteicComplex {

	/* eslint-disable */ 
	constructor (conf, C, t, bad_pos){
        // this.C = C
        this.conf = conf
        this.C = C
        this.t = t //To be initialized !
        this.l = -1
        this.start = -1
        if (this.t == 0){
            this.l = this.conf["N_OXPHOS"]
            this.start = 0
        }
        else if (this.t == 1){
            this.l = this.conf["N_TRANSLATE"]
            this.start = this.conf["N_OXPHOS"]
        }
        else {
            this.l = this.conf["N_REPLICATE"]
            this.start = this.conf["N_OXPHOS"] + this.conf["N_TRANSLATE"]
        }
        // 0 is oxpos, 1 is translation, 2 is replication
        // -1 is non init
        this.bad_pos = bad_pos // position of the bad proteins
        this.deleted = false
    }

    deprecate(chance){
        let deleted_p = []
        let k = this.binomial(this.l, chance)
        while (k > 0){
            this.deleted = true
            let prot = this.C.ran(0,this.l-1)
            while (deleted_p.includes(prot)){
                prot = this.C.ran(0,this.l-1)
            }
            deleted_p.push(prot)
            k--
        }
        return deleted_p
    }

    mutate(chance){
        let mutables = this.l - this.bad_pos.length
        let mutated = []
        if (mutables == 0){
            return []
        }
        let mutations = this.binomial(mutables, chance)
        while (mutations > 0){
            let mutated_prot = this.C.ran(0,this.l-1)
            while (this.bad_pos.includes(mutated_prot)){
                mutated_prot = this.C.ran(0,this.l-1)
            }
            this.bad_pos.push(mutated_prot)
            mutated.push(mutated_prot)
            mutations--
        }
        return mutated
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

export default ProteicComplex