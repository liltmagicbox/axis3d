from math import cos,sin, pi


"""
a cylinder , and cone.
is came form , radius, height, stack. slice->slices
radius a,b, so it be cone.

make_cylinder( radius2= 0)
 to cone.
"""


EPS = 0.0001 #1e-5


#========for test
def plot3d(X,Y,Z):
	import matplotlib.pyplot as plt
	fig = plt.figure()#figsize=(4, 6))
	ax = fig.add_subplot(111, projection='3d')
	#===========
	ax.plot(X,Y,Z, 'bo-')
	plt.show()




#======================================

def make_ring(slices, radius, z):
	"z up ring "
	coords = []
	d_angle = 2*pi/slices
	for i in range(slices):
		#print(i, d_angle*i*180/pi )
		th = d_angle*i
		x = cos(th) * radius
		y = sin(th) * radius
		#z = altitude
		coords.append( (x,y,z) )
	return coords


#===========================

def make_cylinder_points( radius=1, height=2, slices=8, stack=4 ):
	points = []
	
	for i in range(stack+1):
		z =  i* height/stack
		coords = make_ring(slices, radius, z)
		points.extend(coords)
	
	points.append( (0,0,height))
	points.append( (0,0,0))
	return points



def make_cone_points( radius=1, height=2, slices=8, stack=4 , radius2 = 0 ):
	"the top shall be a point, if radius2 < EPS."
	points = []

	d_radius = (radius-radius2)/stack
	for i in range(stack+1):
		i_radius = radius-d_radius*i
		if i_radius < EPS:
			continue
		
		z =  i* height/stack
		coords = make_ring(slices, i_radius, z)
		points.extend(coords)
	
	points.append( (0,0,height))
	points.append( (0,0,0))
	return points

#======================================


def make_cylinder( radius=1, height=2, slices=8, stack=4, radius2 = None):
	"returns points / indices"
	if radius2 is None:
		radius2 = radius
	is_cone = radius2 < EPS
	
	points = make_cone_points(radius, height, slices, stack, radius2)
	begin = len(points)-1
	end = len(points)-2

	indices = []
	#===base
	for i in range(slices):
		tri = (i, (i+1)%slices ,begin)
		#print(tri,'tri',i)
		indices.append(tri)

	#wall
	for j in range(stack):
		offset = slices * j		
		for i in range(slices):
			#==for cone
			if j == stack-1 and is_cone:#last upper
				up = slices
				tri = (offset+i, offset+(i+1)%slices , end)
				#print(tri,'tri',i)
				indices.append(tri)
				continue

			#===normal wall
			up = slices
			tri = (offset+i, offset+(i+1)%slices , offset+(i+1)%slices+ up)
			#print(tri,'tri',i)
			indices.append(tri)
			
			#tri2
			tri = (offset+i, offset+(i+1)%slices+ up,  offset+i+ up)
			#print(tri,'tri',i)
			indices.append(tri)


	if is_cone:
		return points, indices

	#===hat
	offset = slices * stack
	for i in range(slices):
		tri = (offset+i, offset+(i+1)%slices ,end)
		#print(tri,'tri',i)
		indices.append(tri)
	
	return points, indices



#================ cone




# def make_cone( radius=1, height=2, slices=8, stack=4 ):
# 	radius2 = 0
# 	return make_cylinder( radius, height, slices, stack, radius2)


#==sphere

def make_sphere_points(radius=1, slices=4, stack=4):
	for i in range(stack):
		ring = make_ring(slices,radius,z)


def make_ring(slices, radius, z):
	"z up ring "
	coords = []
	d_angle = 2*pi/slices
	for i in range(slices):
		#print(i, d_angle*i*180/pi )
		th = d_angle*i
		x = cos(th) * radius
		y = sin(th) * radius
		#z = altitude
		coords.append( (x,y,z) )
	return coords




#========cube

# def make_cube_points(width=1, height=1, depth=1):
# 	"tuple is mem-stuck. list append 1-4-8-15..slow."
# 	x = width/2
# 	y = height/2
# 	z = depth/2

# 	end = (0,0,-z)
# 	begin = (0,0,z)

# 	p1 = (x,0,z)
# 	p2 = (x,y,z)
# 	p3 = (0,y,z)
# 	p4 = (-x,y,z)
# 	p5 = (-x,0,z)
# 	p6 = (-x,-y,z)
# 	p7 = (0,-y,z)
# 	p8 = (x,-y,z)

# 	p01 = (x,0,0)
# 	p02 = (x,y,0)
# 	p03 = (0,y,0)
# 	p04 = (-x,y,0)
# 	p05 = (-x,0,0)
# 	p06 = (-x,-y,0)
# 	p07 = (0,-y,0)
# 	p08 = (x,-y,0)


# 	p11 = (x,0,-z)
# 	p22 = (x,y,-z)
# 	p33 = (0,y,-z)
# 	p44= (-x,y,-z)
# 	p55 = (-x,0,-z)
# 	p66 = (-x,-y,-z)
# 	p77 = (0,-y,-z)
# 	p88 = (x,-y,-z)
# 	return [p1,p2,p3,p4,p5,p6,p7,p8, p01,p02,p03,p04,p05,p06,p07,p08, p11,p22,p33,p44,p55,p66,p77,p88, end,begin]

def make_cube_points(width=1, height=1, depth=1):
	"tuple is mem-stuck. list append 1-4-8-15..slow."
	x = width/2
	y = height/2
	z = depth/2

	p1 = (x,y,z)
	p2 = (-x,y,z)
	p3 = (-x,-y,z)
	p4 = (x,-y,z)

	p5 = (x,y,-z)
	p6= (-x,y,-z)
	p7 = (-x,-y,-z)
	p8 = (x,-y,-z)
	return [p1,p2,p3,p4,p5,p6,p7,p8]

def make_cube(width=1, height=1, depth=1):
	points = make_cube_points(width, height, depth)
	#front
	t1 = (0,1,2)
	t2 = (2,3,0)
	#bottom
	t3 = (3,2,6)
	t4 = (3,6,7)

	#back
	t5 = (7,6,4)
	t6 = (4,6,5)
	#top
	t7 = (4,5,1)
	t8 = (4,1,0)	

	#right
	t9 = (0,3,7)
	t10 = (0,7,4)
	#left
	t11 = (1,5,6)
	t12 = (1,6,2)
	indices = [t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12]
	return points, indices






#================== test


_tests = []
#=================================



def test_make_ring():
	"_make_ring 1st created."
	from matplotlib import pyplot as plt	
	c = make_ring(8, 1,0)
	
	X = [i[0] for i in c]
	Y = [i[1] for i in c]
	plt.plot(X,Y,'ro-')
	plt.show()
_tests.append(test_make_ring)


def test_make_rings():
	X,Y,Z = [],[],[]
	for i in range(4):
		c = make_ring(8, 1, i)
		x = [i[0] for i in c]
		y = [i[1] for i in c]
		z = [i[2] for i in c]
		X.extend(x)
		Y.extend(y)
		Z.extend(z)
	
	plot3d(X,Y,Z)

_tests.append(test_make_rings)


def test_make_cylinder_points():
	points = make_cylinder_points()

	X = [i[0] for i in points]
	Y = [i[1] for i in points]
	Z = [i[2] for i in points]

	plot3d(X,Y,Z)
_tests.append(test_make_cylinder_points)





def test_make_cone_points():
	points = make_cone_points(radius2 = 0.2, stack = 9)

	X = [i[0] for i in points]
	Y = [i[1] for i in points]
	Z = [i[2] for i in points]

	plot3d(X,Y,Z)
_tests.append(test_make_cone_points)





def test_make_cylinder():
	points,indices = make_cylinder()
	
	X = []
	Y = []
	Z = []
	for tri in indices:
		for i in tri:
			xyz = points[i]
			X.append(xyz[0])
			Y.append(xyz[1])
			Z.append(xyz[2])
	plot3d(X,Y,Z)
_tests.append(test_make_cylinder)


def test_make_cone():
	points,indices = make_cylinder(radius2 = 0)
	
	X = []
	Y = []
	Z = []
	for tri in indices:
		for i in tri:
			xyz = points[i]
			X.append(xyz[0])
			Y.append(xyz[1])
			Z.append(xyz[2])
	plot3d(X,Y,Z)
_tests.append(test_make_cone)






def test_make_cube_points():
	points = make_cube_points()
	
	X = []
	Y = []
	Z = []
	for xyz in points:
		X.append(xyz[0])
		Y.append(xyz[1])
		Z.append(xyz[2])
	plot3d(X,Y,Z)
_tests.append(test_make_cube_points)




def main():
	for test in _tests:
		test()


if __name__ == '__main__':
	main()

