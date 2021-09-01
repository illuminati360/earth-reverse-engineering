#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Split an OBJ file into separate files

Ignores polygon groups, parameter space vertices.
The individual files are named as the object they contain. The material file
(.mtl) is not split with the objects.

Run: 
    $ objsplit.py /input/dir/file.obj /output/dir
"""

import re
import os.path as p
import sys
from contextlib import contextmanager
from functools import reduce

def main(file_in, dir_out):

    v_pat = re.compile(r"^v\s[\s\S]*")  # vertex
    vn_pat = re.compile(r"^vn\s[\s\S]*")  # vertex normal
    vt_pat = re.compile(r"^vt\s[\s\S]*")  # vertex texture coordinate
    f_pat = re.compile(r"^f\s[\s\S]*")  # face
    o_pat = re.compile(r"^o\s[\s\S]*")  # named object
    ml_pat = re.compile(r"^mtllib[\s\S]*")  # .mtl file
    mu_pat = re.compile(r"^usemtl[\s\S]*")  # material to use
    s_pat = re.compile(r"^s\s[\s\S]*")  # shading
    vertices = ['None']  # because OBJ has 1-based indexing
    v_normals = ['None']  # because OBJ has 1-based indexing
    vts = ['None']
    objects = {}
    faces = []
    mtllib = None
    usemtl = None
    prev_usemtl = None
    shade = None
    o_id = None

    count = 0
    with open(file_in, 'r') as f_in:
        for line in f_in:
            v = v_pat.match(line)
            o = o_pat.match(line)
            f = f_pat.match(line)
            vn = vn_pat.match(line)
            vt = vt_pat.match(line)
            ml = ml_pat.match(line)
            mu = mu_pat.match(line)
            s = s_pat.match(line)

            if v:
                vertices.append(v.group())
                count += 1
            elif vn:
                v_normals.append(vn.group())
            elif vt:
                vts.append(vt.group())
            elif o:
                if o_id:
                    objects[o_id] = {'faces': faces,
                                     'usemtl': prev_usemtl,
                                     's': shade,
                                     'count': count
                                     }
                    o_id = o.group()
                    faces = []
                    count = 0
                else:
                    o_id = o.group()
            elif f:
                faces.append(f.group())
            elif mu:
                prev_usemtl = usemtl
                usemtl = mu.group()
            elif s:
                shade = s.group()
            elif ml:
                mtllib = ml.group()
            else:
                # ignore vertex texture coordinates, polygon groups, parameter
                # space vertices
                pass

        if o_id:
            objects[o_id] = {'faces': faces,
                             'usemtl': usemtl,
                             's': shade,
                             'count': count
                             }
        else:
            sys.exit("Cannot split an OBJ without named objects in it!")
    
    if len(vertices) < 100*1000:
        exit()

    vcount = 0
    objs = []
    part = 0
    for i, o_id in enumerate(objects.keys()):
        faces = reduce(lambda a,c: a+c.split(' '), list(map(lambda x: x.strip().split(' ',1)[1], objects[o_id]['faces'])), [])
        f_vertices = sorted(map(lambda x: x.split('/')[0], faces))
        f_vts = sorted(map(lambda x: x.split('/')[1], faces))
        f_vnormals = sorted(map(lambda x: x.split('/')[2], faces))

        objects[o_id]['vertices'] = f_vertices
        objects[o_id]['vnormals'] = f_vnormals
        objects[o_id]['vts'] = f_vts
        objects[o_id]['faces'] = faces

        objs.append(o_id)
        if vcount + objects[o_id]['count'] > 100*1000 or i == len(objects.keys())-1:
            f_vertices = reduce(lambda a,c: a+objects[c]['vertices'], objs, [])
            f_vts = reduce(lambda a,c: a+objects[c]['vnormals'], objs, [])
            f_vnormals = reduce(lambda a,c: a+objects[c]['vts'], objs, [])
            # vertex mapping to a sequence starting with 1
            v_map = {str(v): str(e) for e, v in enumerate(f_vertices, start=1)}
            vn_map = {str(vn): str(e) for e, vn in enumerate(f_vnormals, start=1)}
            vt_map = {str(vt): str(e) for e, vt in enumerate(f_vts, start=1)}

            for obj in objs:
                faces = objects[obj]['faces']
                faces_mapped = []
                for i in range(0,len(faces),3):
                    f0 = faces[i].split('/')
                    f0 = v_map[f0[0]]+'/'+vt_map[f0[1]]+'/'+vn_map[f0[2]]
                    f1 = faces[i+1].split('/')
                    f1 = v_map[f1[0]]+'/'+vt_map[f1[1]]+'/'+vn_map[f1[2]]
                    f2 = faces[i+2].split('/')
                    f2 = v_map[f2[0]]+'/'+vt_map[f2[1]]+'/'+vn_map[f2[2]]
                    faces_mapped.append('f '+f0+' '+f1+' '+f2+'\n')
                objects[obj]['faces'] = faces_mapped
                objects[obj]['part'] = part

            part += 1
            vcount = 0
            objs = []

        vcount += objects[o_id]['count']

    prev_part = -1
    f_out = None
    for o_id in objects.keys():
        # fname = o_id.split()[1].strip()
        part = objects[o_id]['part']
        if (part != prev_part):
            fname = p.basename(file_in).replace('.obj','.') + str(part)
            file_out = p.join(dir_out, fname + ".obj")
            f_out = open(file_out, 'w', newline=None)
            if mtllib:
                f_out.write(mtllib)

        prev_part = part
        f_out.write(o_id)

        if objects[o_id]['usemtl']:
            f_out.write(objects[o_id]['usemtl'])

        for vertex in objects[o_id]['vertices']:
            f_out.write(vertices[int(vertex)])
        for uv in objects[o_id]['vts']:
            f_out.write(vts[int(uv)])

        for normal in objects[o_id]['vnormals']:
            f_out.write(v_normals[int(normal)])

        f_out.write(''.join(objects[o_id]['faces']))

if __name__ == '__main__':
    file_in = sys.argv[1]
    dir_out = sys.argv[2]
    main(file_in, dir_out)