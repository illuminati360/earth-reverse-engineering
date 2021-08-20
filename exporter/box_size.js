function dist(lat1, lat2, lon1, lon2){
	const φ1 = lat1 * Math.PI/180, φ2 = lat2 * Math.PI/180, Δλ = (lon2-lon1) * Math.PI/180, R = 6371e3;
	const d = Math.acos( Math.sin(φ1)*Math.sin(φ2) + Math.cos(φ1)*Math.cos(φ2) * Math.cos(Δλ) ) * R;
	return d;
}

async function run() {
	let [lat1, lat2, lon1, lon2] = process.argv[2].split(',').map(x=>parseFloat(x));
	console.log(lat1, lat2, lon1, lon2)
	let width = dist(lat1, lat1, lon1, lon2);
	let height = dist(lat1, lat2, lon1, lon1);
	console.log(width, height);
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