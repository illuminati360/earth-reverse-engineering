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

dirs=($dirs)
octants=($octants)
results=""
for i in "${!dirs[@]}"; do
    dir=${dirs[$i]}
    octant=${octants[$i]}
    output=/root/AltSpaceMREs/public/gltf/$octant
    cd $dir

    inputs="model.2.obj"

    size=$(stat -c%s model.2.obj)
    test $size -gt 3000000 && \
    test ! -f "model.2.0.obj" && \
        python /root/earth-reverse-engineering/exporter/objsplit.py model.2.obj ./

    test -f "model.2.0.obj" && inputs=$(ls model.2.*.obj)

    inputs=($inputs)
    for input in ${inputs[@]}; do
        n=$(echo $input | cut -d'.' -f3)
        if test "$n" != "0" && test "$n" != "obj"; then
            result=$output.$n.glb
        else
            result=$output.glb
        fi
        results=$results" "$result
        test ! -f $result && \
            /root/.nvm/versions/node/v14.16.1/bin/node /root/.nvm/versions/node/v14.16.1/lib/node_modules/obj2gltf/bin/obj2gltf.js --unlit -b -i $input -o $result >&2
        test ! -f $result && \
            cp $wd/empty.glb $result
    done
    cd $wd
done

echo $results