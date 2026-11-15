"""Build the inside-ai-data-center stop models: blender -b -P build.py -- --stop 3|4|all

For each stop: compose (stops/sN_*.py), validate (lib.validate, spec 6.4), save the .blend and a raw GLB under
build/inside_ai_dc/, and write a sidecar meta JSON for post.mjs.
"""
import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import lib  # noqa: E402

STOPS = {3: ('stops.s3_rack', 's3-rack'), 4: ('stops.s4_tray', 's4-tray')}


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    which = argv[argv.index('--stop') + 1] if '--stop' in argv else 'all'
    stops = sorted(STOPS) if which == 'all' else [int(which)]
    raw = os.path.join(lib.BUILD, 'raw')
    os.makedirs(raw, exist_ok=True)
    for n in stops:
        mod_name, file_id = STOPS[n]
        mod = importlib.import_module(mod_name)
        spec = mod.build()
        stats = lib.validate(spec)
        import bpy
        if '_scratch' in bpy.data.meshes:
            bpy.data.meshes.remove(bpy.data.meshes['_scratch'])
        lib.save_blend(os.path.join(lib.BUILD, file_id + '.blend'))
        path = os.path.join(raw, file_id + '.glb')
        lib.export(path)
        scene = bpy.context.scene
        extra = {'stop': n, 'file': file_id + '.glb', 'required': spec['required'],
                 'metresPerUnit': scene['metresPerUnit'],
                 'parts': sorted(o.name for o in scene.objects if 'tier' in o.keys() and not o.name.startswith('i.')),
                 'tiers': {o.name: o['tier'] for o in scene.objects if 'tier' in o.keys() and not o.name.startswith('i.')},
                 'anchors': sorted(o.name[7:] for o in scene.objects if o.name.startswith('anchor:'))}
        lib.write_meta(os.path.join(raw, file_id + '.meta.json'), stats, extra)


main()
