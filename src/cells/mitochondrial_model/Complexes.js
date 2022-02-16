class Complexes {

	/* eslint-disable */ 
	constructor (conf, C, type, bad_pos) {
        // this.C = C
        this.conf = conf
        this.C = C
        this.type = type //To be initialized !
        this.length = -1
        this.start = -1
        if (this.type == 0){
            this.length = this.conf["N_OXPHOS"]
            this.start = 0
        }
        else if (this.type == 1){
            this.length = this.conf["N_TRANSLATE"]
            this.start = this.conf["N_OXPHOS"]
        }
        else {
            this.length = this.conf["N_REPLICATE"]
            this.start = this.conf["N_OXPHOS"] + this.conf["N_TRANSLATE"]
        }
        // 0 is oxpos, 1 is translation, 2 is replication
        // -1 is non init
        this.bad_pos = [] // position of the bad proteins
        this.deleted = false
    }


    deprecate(chance){
        let deleted_p = []
        let k = this.binomial(this.length, chance)
        while (k > 0){
            this.deleted = true
            let prot = this.C.ran(0,this.length-1)
            while (prot in deleted_p){
                prot = this.C.ran(0,this.length-1)
            }
            deleted_p.push(prot)
            k--
        }
        return deleted_p
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

export default Complexes