
/* eslint-disable no-unused-vars*/
class Cell {
	/** 
    individualParams
    parentId
    conf
    kind
    */
    
	constructor (conf, kind, id, mt, parent){
		this.individualParams = []
		this.parentId = 0
		this.id = id
		this.conf = conf
		this.kind = kind
		this.mt = mt 
		if (parent instanceof Cell){ // copy on birth
			this.parentId = parent.id
		} 
	}

	getParam(param){
		if (!(this.individualParams.includes(param))){
			return this.conf[param][this.kind]
		} else {
			return this.getIndividualParam(param)
		}
	}

	getIndividualParam(param){
		throw("Implement changed way to get" + param + " constraint parameter per individual, or remove this from " + typeof this + " Cell class's indivualParams." )
	}

	// getColor(){
	// 	return this.conf['CELLCOLOR'][this.kind]
	// }
	
}



export default Cell







