#!/bin/bash
test $# -lt 3 && exit
cd /root/earth-reverse-engineering/exporter
octant_n_box=$(node lat_long_to_octant.js $1 $2 $3)
octants=$(echo $octant_n_box | cut -d' ' -f1 | sed 's/,/ /g')
box=$(echo $octant_n_box | cut -d' ' -f2)
echo $octants
wd=$(pwd)
dirs=''
for octant in ${octants[@]}; do
    output=/root/AltSpaceMREs/public/gltf/$octant.glb
    test -f $output && continue
    
    dir=$(node dump_obj.js $octant $3)
    dirs=$dirs' '$dir
    # gltf-transform weld --tolerance 0.01 model.glb $output
done

node center_scale_objs.js $dirs
for dir in ${dirs[@]}; do
    cd $dir
    output=/root/AltSpaceMREs/public/gltf/$(basename $dir | cut -d'-' -f1).glb
    /root/.nvm/versions/node/v14.16.1/bin/node /root/.nvm/versions/node/v14.16.1/lib/node_modules/obj2gltf/bin/obj2gltf.js --unlit -b -i model.2.obj -o $output >&2
    cd $wd
done