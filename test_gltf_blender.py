"""test_gltf_blender.py -- feed our .glb to REAL blender, verify, render.

needs the blender python module:  pip install bpy
(or run this file inside blender's scripting tab -- same code works.)

what it proves:
1. blender's gltf importer accepts our file (structure is spec-valid)
2. engine z-up coords come back exactly (zup_root x blender's own conversion = identity)
3. lights/camera/materials/vertex colors/extras all arrive
4. cycles renders it -> gltf_out/blender_render.png
"""

import os
import math

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gltf_out')
GLB = os.path.join(OUT_DIR, 'demo_scene.glb')


def ensure_glb():
	if not os.path.exists(GLB):
		os.makedirs(OUT_DIR, exist_ok=True)
		from test_gltf import make_demo_scene
		make_demo_scene().save(GLB)


def main():
	try:
		import bpy
	except ImportError:
		print('bpy not installed. pip install bpy, or run inside blender. skip.')
		return

	ensure_glb()
	print('blender', bpy.app.version_string)

	#--- clean scene, import
	bpy.ops.wm.read_factory_settings(use_empty=True)
	bpy.ops.import_scene.gltf(filepath=GLB)

	objs = bpy.context.scene.objects
	by_name = {o.name: o for o in objs}
	meshes = [o for o in objs if o.type == 'MESH']
	lights = [o for o in objs if o.type == 'LIGHT']
	cams = [o for o in objs if o.type == 'CAMERA']
	print(f'imported: {len(objs)} objects / {len(meshes)} meshes, {len(lights)} lights, {len(cams)} cameras')

	#--- 1. counts
	assert len(lights) == 3, [o.name for o in lights]
	assert len(cams) == 1
	kinds = sorted(o.data.type for o in lights)
	assert kinds == ['POINT','SPOT','SUN'], kinds

	#--- 2. engine coords restored? leader unit4 was at (-2.9, 0, 0) z-up.
	unit4 = by_name['unit4']
	wpos = unit4.matrix_world.translation
	assert abs(wpos.x - -2.9) < 1e-4 and abs(wpos.y - 0) < 1e-4 and abs(wpos.z - 0) < 1e-4, tuple(wpos)
	print(f'leader world pos in blender: ({wpos.x:.3f}, {wpos.y:.3f}, {wpos.z:.3f})  == engine coords. z-up restored.')

	#--- 3. extras -> custom properties
	assert unit4['hp'] == 100, dict(unit4)
	assert unit4['simulate_physics'] == True
	assert list(unit4['speed']) == [0,1,0]
	print('extras arrived as custom properties:', {'hp':unit4['hp'], 'speed':list(unit4['speed'])})

	#--- 4. materials / vertex color
	obelisk = by_name['obelisk']
	assert len(obelisk.data.color_attributes) >= 1, 'vertex color missing'
	glass = [m for m in bpy.data.materials if 'glass' in m.name][0]
	bsdf = [n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED'][0]
	assert bsdf.inputs['Alpha'].default_value < 0.5, 'opacity not carried'
	print('vertex colors + alpha material ok')

	#--- 5. camera fov
	cam = cams[0]
	angle_y = cam.data.angle_y
	assert abs(math.degrees(angle_y) - 70) < 0.5, math.degrees(angle_y)
	print(f'camera vertical fov: {math.degrees(angle_y):.2f} deg (sent 70)')

	#--- 6. points primitive: data arrives (as loose verts), rendering is another story
	sparks = by_name.get('sparks')
	if sparks:
		print(f'POINTS primitive: {len(sparks.data.vertices)} loose vertices imported (cycles will not draw them)')

	#--- render with cycles cpu
	scene = bpy.context.scene
	scene.camera = cam
	scene.render.engine = 'CYCLES'
	scene.cycles.device = 'CPU'
	scene.cycles.samples = 64
	scene.render.resolution_x = 830
	scene.render.resolution_y = 500   # ratio 1.66, same as vector.Camera
	# gltf carries no environment light (core spec). tiny gray world so the void isn't pure black.
	world = bpy.data.worlds.new('world')
	world.use_nodes = True
	bg = world.node_tree.nodes['Background']
	bg.inputs[0].default_value = (0.02,0.02,0.025,1)
	scene.world = world

	fpath = os.path.join(OUT_DIR,'blender_render.png')
	scene.render.filepath = fpath
	bpy.ops.render.render(write_still=True)
	print('rendered:', fpath, f'({os.path.getsize(fpath)/1024:.0f} KB)')

	#--- 7. reverse direction: blender-authored scene -> our reader (artist workflow)
	bpy.ops.wm.read_factory_settings()  # default cube + light + camera, made by blender
	back = os.path.join(OUT_DIR,'_blender_authored.glb')
	# NOTE blender does NOT export cameras/lights by default. flags needed:
	bpy.ops.export_scene.gltf(filepath=back, export_cameras=True, export_lights=True)

	import gltf
	s = gltf.load(back)
	cube = s['meshes'][0]['primitives'][0]['attrs']
	assert len(cube['position']) == 24*3, len(cube['position'])   # blender cube: 24 split verts
	assert 'normal' in cube and 'uv' in cube and 'index' in cube
	assert len(s['lights']) == 1 and len(s['cameras']) == 1
	# engine-ready: this attrs dict can go straight into vao.VAO(attrs)
	print(f"blender-authored glb read back: {len(cube['position'])//3} verts, "
		f"{len(cube['index'])//3} tris, lights/cam ok -> attrs dict ready for VAO")
	os.remove(back)


if __name__ == '__main__':
	main()
