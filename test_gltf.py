"""test_gltf.py -- gltf.py roundtrip + a demo scene from our own geometry.

make_demo_scene() builds 'squad on a pad' out of cylinder.py primitives,
in engine coords (z-up, meters), and exports gltf_out/demo_scene.glb.
drag that file into blender / unreal(5.x) / https://gltf-viewer.donmccurdy.com
and it should just show up.
"""

import os
import math

import gltf
from gltf import Gltf, calc_normals, look_at_quat
from cylinder import make_cylinder

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gltf_out')


#=============== scene build helpers

def cyl_attrs(radius=1, height=2, slices=8, stack=4, radius2=None, color=None):
	"cylinder.py output -> attrs dict. color: single (r,g,b) painted per vertex, or fn(x,y,z)."
	points, indices = make_cylinder(radius, height, slices, stack, radius2)
	attrs = {'position': points, 'index': indices}
	if color is not None:
		if callable(color):
			attrs['color'] = [ color(x,y,z) for x,y,z in points ]
		else:
			attrs['color'] = [ color for _ in points ]
	calc_normals(attrs)
	return attrs


def make_demo_scene():
	g = Gltf(name='axis3d_demo')  # up='+Z' default: engine coords go in as-is

	#--- materials
	mat_pad = g.add_material(name='pad', color=0x39424e, roughness=0.9)
	mat_red = g.add_material(name='squad_red', color=0xc84040, roughness=0.7)
	mat_blue = g.add_material(name='squad_blue', color=0x3f6fc8, roughness=0.7)
	mat_hat = g.add_material(name='hat', color=0xe0d8c8, roughness=0.5, metallic=0.3)
	mat_vcol = g.add_material(name='obelisk_vcol', color=0xffffff, roughness=0.4)  # x COLOR_0
	mat_glass = g.add_material(name='marker_glass', color=0x60ffa0, opacity=0.35, double_sided=True)
	mat_spark = g.add_material(name='spark', color=0xffcc40, emissive=0xffcc40)

	#--- meshes
	mesh_pad = g.add_mesh(cyl_attrs(10, 0.25, slices=48, stack=1), material=mat_pad, name='pad')
	mesh_body_r = g.add_mesh(cyl_attrs(0.35, 1.2, slices=12, stack=2), material=mat_red, name='body_red')
	mesh_body_b = g.add_mesh(cyl_attrs(0.35, 1.2, slices=12, stack=2), material=mat_blue, name='body_blue')
	mesh_hat = g.add_mesh(cyl_attrs(0.45, 0.5, slices=12, stack=2, radius2=0), material=mat_hat, name='hat_cone')

	def height_color(x,y,z):
		t = z/3.0
		return (0.2+0.8*t, 0.2, 1.0-0.8*t)  # blue->red by height
	mesh_obelisk = g.add_mesh(cyl_attrs(0.8, 3.0, slices=24, stack=8, radius2=0.05, color=height_color),
		material=mat_vcol, name='obelisk')
	mesh_marker = g.add_mesh(cyl_attrs(0.9, 0.05, slices=24, stack=1), material=mat_glass, name='marker')

	# a POINTS primitive: sparks. (blender: loose verts / UE: ignored. see report)
	sparks = {'position': [ ( 2.2*math.cos(i), 2.2*math.sin(i), 3.5+0.3*math.sin(3*i) ) for i in [k*0.7 for k in range(9)] ]}
	mesh_sparks = g.add_mesh(sparks, material=mat_spark, name='sparks', mode=gltf.POINTS)

	#--- nodes: pad + obelisk center
	g.add_node(name='pad', mesh=mesh_pad, pos=(0,0,-0.25))
	g.add_node(name='obelisk', mesh=mesh_obelisk, pos=(0,0,0))
	g.add_node(name='sparks', mesh=mesh_sparks)

	#--- squad: 3x3 units, unit = parent node + body/hat children (tests hierarchy)
	for i in range(3):
		for jj in range(3):
			n = i*3+jj
			x = -4.5 + i*1.6
			y = -2.0 + jj*2.0
			facing = math.atan2(-y, -x)  # face center
			leader = (n == 4)
			extras = None
			if leader:
				extras = {'speed':[0,1,0], 'simulate_physics':True, 'hp':100}
			unit = g.add_node(name=f'unit{n}', pos=(x,y,0), rot=(0,0,facing), extras=extras)
			body = mesh_body_r if i == 0 else mesh_body_b
			g.add_node(name=f'unit{n}_body', mesh=body, parent=unit)
			g.add_node(name=f'unit{n}_hat', mesh=mesh_hat, pos=(0,0,1.2), parent=unit)
			if leader:
				g.add_node(name='leader_marker', mesh=mesh_marker, pos=(0,0,2.2), parent=unit)

	#--- lights. photometric units: sun=lux, point/spot=candela (see gltf.add_light doc)
	sun = g.add_light('sun', color=(1,0.98,0.9), intensity=1800.0, name='sun')
	g.add_node(name='sun', light=sun, pos=(10,-6,12), rot=look_at_quat((10,-6,12),(0,0,0)))
	lamp = g.add_light('point', color=(1,0.6,0.3), intensity=800.0, name='lamp')
	g.add_node(name='lamp', light=lamp, pos=(0,0,4.2))
	spot = g.add_light('spot', color=(0.6,0.8,1), intensity=2500.0, outer_angle=0.5, name='spot')
	g.add_node(name='spot', light=spot, pos=(-4,4,6), rot=look_at_quat((-4,4,6),(-3.7,-0.5,0)))

	#--- camera, same numbers as vector.Camera defaults
	cam = g.add_camera(fov=70, ratio=1.66, near=0.01, far=1000)
	campos = (6.0,-6.0,3.8)
	g.add_node(name='cam', camera=cam, pos=campos, rot=look_at_quat(campos,(0,0,1.0)))

	return g


#=============== tests
_tests = []

def test_roundtrip_minimal():
	g = Gltf()
	mat = g.add_material(color=0xff8800, roughness=0.5)
	attrs = {'position':[0,0,0, 1,0,0, 0,1,0], 'uv':[0,0, 1,0, 0,1], 'index':[0,1,2]}
	mesh = g.add_mesh(attrs, material=mat, name='tri')
	g.add_node(mesh=mesh, name='tri', pos=(1,2,3), rot=(0.1,0.2,0.3), scale=(2,2,2))
	fpath = os.path.join(OUT_DIR,'_minimal.glb')
	g.save(fpath)

	s = gltf.load(fpath)
	prim = s['meshes'][0]['primitives'][0]
	assert prim['attrs']['position'] == [0,0,0, 1,0,0, 0,1,0]
	assert prim['attrs']['uv'] == [0,0, 1,0, 0,1]
	assert prim['attrs']['index'] == [0,1,2]
	c = s['materials'][0]['color']
	assert abs(c[0]-1.0)<0.01 and abs(c[1]-0x88/255)<0.01
	node = [n for n in s['nodes'] if n.get('mesh') == 0][0]
	assert node['pos'] == (1,2,3)
	assert all( abs(a-b)<1e-6 for a,b in zip(node['rot'],(0.1,0.2,0.3)) )
	assert node['scale'] == (2,2,2)
	os.remove(fpath)
	print('roundtrip minimal: ok')
_tests.append(test_roundtrip_minimal)


def test_roundtrip_gltf_text():
	"same via .gltf (json + base64 buffer)"
	g = Gltf()
	mesh = g.add_mesh({'position':[0,0,0, 1,0,0, 0,1,0], 'index':[0,1,2]})
	g.add_node(mesh=mesh)
	fpath = os.path.join(OUT_DIR,'_minimal.gltf')
	g.save(fpath)
	s = gltf.load(fpath)
	assert s['meshes'][0]['primitives'][0]['attrs']['position'] == [0,0,0, 1,0,0, 0,1,0]
	os.remove(fpath)
	print('roundtrip .gltf text: ok')
_tests.append(test_roundtrip_gltf_text)


def test_demo_scene():
	g = make_demo_scene()
	glb = os.path.join(OUT_DIR,'demo_scene.glb')
	g.save(glb)
	size = os.path.getsize(glb)

	s = gltf.load(glb)
	#--- geometry survived byte-exact?
	src = cyl_attrs(0.35, 1.2, slices=12, stack=2)
	src_flat = []
	for p in src['position']:
		src_flat.extend(p)
	body = [m for m in s['meshes'] if m['name']=='body_red'][0]
	got = body['primitives'][0]['attrs']['position']
	assert len(got) == len(src_flat)
	assert all( abs(a-b) < 1e-6 for a,b in zip(got, src_flat) ), 'positions differ'
	src_idx = []
	for tri in src['index']:
		src_idx.extend(tri)
	assert body['primitives'][0]['attrs']['index'] == src_idx

	#--- scene content
	assert len(s['cameras']) == 1
	assert abs(s['cameras'][0]['fov'] - 70) < 1e-3
	kinds = sorted(l['kind'] for l in s['lights'])
	assert kinds == ['directional','point','spot'], kinds
	units = [n for n in s['nodes'] if n['name'].startswith('unit') and 'children' in n]
	assert len(units) == 9
	leader = [n for n in s['nodes'] if n.get('extras')][0]
	assert leader['extras']['hp'] == 100
	assert leader['extras']['simulate_physics'] == True
	vcol = [m for m in s['meshes'] if m['name']=='obelisk'][0]
	assert 'color' in vcol['primitives'][0]['attrs']
	print(f'demo scene: ok  ({size/1024:.1f} KB, {len(s["nodes"])} nodes, {len(s["meshes"])} meshes)')
_tests.append(test_demo_scene)


def test_third_party_parse():
	"independent readers agree? (skipped if not installed)"
	glb = os.path.join(OUT_DIR,'demo_scene.glb')
	if not os.path.exists(glb):
		make_demo_scene().save(glb)
	try:
		import pygltflib
	except ImportError:
		print('third party: pygltflib not installed, skip')
		return
	f = pygltflib.GLTF2().load(glb)
	assert f.asset.version == '2.0'
	assert len(f.meshes) == 7
	assert len(f.extensions['KHR_lights_punctual']['lights']) == 3
	try:
		import trimesh
	except ImportError:
		print('third party: pygltflib ok. trimesh not installed, skip')
		return
	t = trimesh.load(glb)
	tri_meshes = [geo for geo in t.geometry.values() if hasattr(geo,'faces')]
	assert len(tri_meshes) >= 6
	print(f'third party: pygltflib + trimesh ok ({len(t.geometry)} geometries)')
_tests.append(test_third_party_parse)


def main():
	os.makedirs(OUT_DIR, exist_ok=True)
	for test in _tests:
		test()
	# leave the demo files around for viewing
	g = make_demo_scene()
	g.save(os.path.join(OUT_DIR,'demo_scene.glb'))
	g2 = make_demo_scene()
	g2.save(os.path.join(OUT_DIR,'demo_scene.gltf'))
	print('wrote', os.path.join(OUT_DIR,'demo_scene.glb'))


if __name__ == '__main__':
	main()
