#!/bin/bash
test $# -lt 3 && exit
cd /root/earth-reverse-engineering/exporter
octant=$(node lat_long_to_octant.js $1 $2 $3)
node dump_obj.js $octant $3
dir=$(node dump_obj.js $octant $3)
node center_scale_obj.js
cd $dir
obj2gltf -i model.2.obj -o /root/AltSpaceMREs/public/gltf/$1,$2,$3.gltf