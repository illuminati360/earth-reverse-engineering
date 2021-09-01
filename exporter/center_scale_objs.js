"use strict";

// centers and scales all *.obj and saves results as *.2.obj
// can also keep 3d viewers from jittering

const fs = require('fs');
const readline = require('readline');
const path = require('path');
const OBJ_DIR = './downloaded_files/obj';
const SCALE = 10;

const [ lat, lon ] = process.argv.slice(2,4);
const subdirs = process.argv.slice(4);
const h = 6371*1000;

const DegreesToRadians = Math.PI / 180;

const offset_x = h * Math.cos(lat * DegreesToRadians) * Math.cos(lon * DegreesToRadians);
const offset_y = h * Math.cos(lat * DegreesToRadians) * Math.sin(lon * DegreesToRadians);
const offset_z = h * Math.sin(lat * DegreesToRadians);

let min_x = Infinity, max_x = -Infinity;
let min_y = Infinity, max_y = -Infinity;
let min_z = Infinity, max_z = -Infinity;

async function run(){
	await scanObjs(subdirs.map(x=>`${x}/model.obj`));
	const center_x = (max_x + min_x) / 2;
	const center_y = (max_y + min_y) / 2;
	const center_z = (max_z + min_z) / 2;
	const distance_x = Math.abs(max_x - min_x);
	const distance_y = Math.abs(max_y - min_y);
	const distance_z = Math.abs(max_z - min_z);
	const max_distance = Math.max(distance_x, distance_y, distance_z);
	console.log([max_distance, center_x, center_y, center_z, offset_x, offset_y, offset_z].join(','));

	for (let i of subdirs) {
		if (!fs.statSync(i).isDirectory()) continue;

		for (let j of fs.readdirSync(i)) {
			j = path.resolve(i, j);
			if (!/model.obj$/.test(j)) continue;
			if (!fs.statSync(j).isFile()) continue;

			await scaleMoveObj(j, `${j.match(/(.*)\.obj$/)[1]}.2.obj`);
		}
	}
}

async function scanObjs(files) {

	return Promise.all(files.map(file_in=>{
		return new Promise((resolve, reject)=>{
			const io = readline.createInterface({
				input: fs.createReadStream(file_in),
				terminal: false,
			});

			io.on('line', line => {
				if (!/^v /.test(line))
					return;
				let [x, y, z] = line.split(' ').slice(1).map(parseFloat);
				min_x = Math.min(x, min_x);
				min_y = Math.min(y, min_y);
				min_z = Math.min(z, min_z);
				max_x = Math.max(x, max_x);
				max_y = Math.max(y, max_y);
				max_z = Math.max(z, max_z);
			});

			io.on('close', () => {
				resolve();
			});
		});
	}));
}

async function scaleMoveObj(file_in, file_out) {
	if (fs.existsSync(file_out)) {
		fs.unlinkSync(file_out);
	}

	const center_x = (max_x + min_x) / 2;
	const center_y = (max_y + min_y) / 2;
	const center_z = (max_z + min_z) / 2;
	const distance_x = Math.abs(max_x - min_x);
	const distance_y = Math.abs(max_y - min_y);
	const distance_z = Math.abs(max_z - min_z);
	const max_distance = Math.max(distance_x, distance_y, distance_z);

	return new Promise((resolve, reject)=>{
		const io = readline.createInterface({
			input: fs.createReadStream(file_in),
			output: fs.createWriteStream(file_out),
		});

		io.on('line', line => {
			if (!/^v /.test(line))
				return io.output.write(`${line}\n`);
			let [x, y, z] = line.split(' ').slice(1).map(parseFloat);
			x = (x - offset_x) / max_distance * SCALE;
			y = (y - offset_y) / max_distance * SCALE;
			z = (z - offset_z) / max_distance * SCALE;
			io.output.write(`v ${x} ${y} ${z}\n`);
		}).on('close', () => {
			// console.error(`done. saved as ${file_out}`);
			resolve();
		});
	});

}

(async function program() {
	await run();
})().then(() => {
	process.exit(0);
}).catch(e => {
	console.error(e);
	process.exit(1);
});