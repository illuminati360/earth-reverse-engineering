"use strict"

/**************************** config ****************************/
const PLANET = 'earth';
const URL_PREFIX = `https://kh.google.com/rt/${PLANET}/`;
const MAX_LEVEL = 18;
/****************************************************************/

const utils = require('./lib/utils')({
	URL_PREFIX, DUMP_JSON_DIR: null, DUMP_RAW_DIR: null, DUMP_JSON: false, DUMP_RAW: false
});

const latLongToOctant = require('./lib/convert-lat-long-to-octant')(utils);

/***************************** main *****************************/
async function run() {

	// let [lat, lon] = [process.argv[2], process.argv[3]];
	let [lat, lon, level] = [process.argv[2], process.argv[3], process.argv[4]];

	if ([lat, lon].includes(undefined)) {
		const invoc = `node ${require('path').basename(__filename)}`;
		console.error(`Usage:`);
		console.error(`  ${invoc} [latitude] [longitude]`);
		console.error(`  ${invoc} 37.420806884765625 -122.08419799804688`);
		process.exit(1);
	}

	[lat, lon] = [parseFloat(lat), parseFloat(lon)];
	const foundOctants = await latLongToOctant(lat, lon, MAX_LEVEL);

	// console.log(lat + ', ' + lon);
	// console.log('-------------');

	// for (let octantLevel in foundOctants) {
	const keys = Object.keys(foundOctants).sort((a,b)=>parseInt(a)-parseInt(b));
	for (let i=0; i<keys.length; i++) {
		let octantLevel = keys[i];
		let octants = foundOctants[octantLevel].octants;
		let box = foundOctants[octantLevel].box;
		// console.log("Octant Level:", octantLevel);
		// console.log(box);
		for (let j = 0; j < octants.length; j++) {
			// console.log("    " + octants[j]);
			// console.log("    " + octants[j]);
		}
		if (octantLevel==level || i >= keys.length-1){
			console.log(octants.join(','), [box.n, box.s, box.w, box.e].join(','));
			break;
		}
	}
}

/****************************************************************/
(async function program() {
	await run();
})().then(() => {
	process.exit(0);
}).catch(e => {
	console.error(e);
	process.exit(1);
});
