#!/bin/bash
test $# -lt 3 && exit
cd /root/earth-reverse-engineering/exporter
octant_n_box=$(node lat_long_to_octant.js $1 $2 $3)
octants=$(echo $octant_n_box | cut -d' ' -f1 | sed 's/,/ /g')
box=$(echo $octant_n_box | cut -d' ' -f2)
wd=$(pwd)
dirs=''
for octant in ${octants[@]}; do
    dir=$(node dump_obj.js $octant $3)
    dirs=$dirs' '$dir
done

node center_scale_objs.js $( python octant_to_latlon.py $(echo $octants | cut -d' ' -f1) ) $dirs
echo $box
echo $octants

dirs=($dirs)
octants=($octants)
for i in "${!dirs[@]}"; do
    dir=${dirs[$i]}
    octant=${octants[$i]}
    output=/root/AltSpaceMREs/public/gltf/$octant.glb
    cd $dir
    test ! -f $output && \
        /root/.nvm/versions/node/v14.16.1/bin/node /root/.nvm/versions/node/v14.16.1/lib/node_modules/obj2gltf/bin/obj2gltf.js --unlit -b -i model.2.obj -o $output >&2
    test ! -f $output && \
        cp $wd/empty.glb $output
    # gltf-transform weld --tolerance 0.01 model.glb $output
    cd $wd
done