import math

class personal_calc:
    def __init__(self):
        pass

    def square(self, lenght):
        area = lenght * lenght
        perimeter = lenght * 4
        print("area of square ", area)
        print("perimeter of square ", perimeter)

    def rectangle(self, lenght, breadth):
        area = lenght * breadth
        perimeter = 2 * (lenght + breadth)
        print("\narea of rectangle ", area)
        print("perimeter of rectangle ", perimeter)

    def circle(self, radius):
        area = math.pi * radius * radius
        diameter = radius * radius
        perimeter = 2 * math.pi * radius
        circumference = 2 * math.pi * radius
        print("\narea of circle ", area)
        print("perimeter of circle ", perimeter)
        print("circumference of circle ", circumference)
        print('Diameter of circle', diameter)
    
    def rhombus(self, diagonal_1, diagonal_2, length):
        area = (diagonal_1 * diagonal_2) / 2
        perimeter = 4 * length
        print("\narea of rhombus ", area)
        print("perimeter of rhombus ", perimeter)

    def parallelogram(self, length, breadth):
        area = length * breadth
        perimeter = 2 * (length + breadth)
        print("\narea of parallelogram ", area)
        print("perimeter of parallelogram ", perimeter)

    def trapezium(self, parallel_1, parallel_2, side_1, side_2, height):
        area = (parallel_1 + parallel_2) / 2 * height
        perimeter = parallel_1 + parallel_2 + side_1 + side_2
        print("\narea of trepezium ", area)
        print("perimeter of trepezium ", perimeter)

    def cube(self, length):
        area = 6 * length * length
        volume = length * length * length
        curved_surface_area = 4 * length * length
        print("\narea of cube ", area)
        print("volume of cube ", volume)
        print("curved surface area of cube ", curved_surface_area)

    def cuboid(self, length, breadth, height):
        area = 2 (length*breadth + breadth*height + height*length)
        volume = length * breadth * height
        curved_surface_area = 2 * (length*height + breadth*height)
        print("\narea of cuboid ", area)
        print("volume of cuboid ", volume)
        print("curved surface area of cuboid ", curved_surface_area)

    def cone(self, length, radius):
        slant_height = math.sqrt(length**2 + radius**2)
        area = math.pi * radius * (radius + slant_height)
        volume = (1/3) * math.pi * radius**2 * length
        curved_surface_area = math.pi * radius * slant_height
        total_surface_area = math.pi * radius (length + radius)
        print("\narea of cone ", area)
        print("volume of cone ", volume)
        print("curved surface area of cone ", curved_surface_area)
        print("total surface area of cone ", total_surface_area)

    def sphere(self, radius):
        area = 4 * math.pi * radius**2
        volume = (4/3) * math.pi * radius**3
        volume_semi_sphere = (2/3) * math.pi * radius**2
        curved_surface_area = 2 * math.pi *radius**2
        total_surface_area = 3 * math.pi * radius**2
        print("\narea of sphere ", area)
        print("volume of sphere ", volume)
        print("volume of semi sphere ", volume_semi_sphere)
        print("curved surface area of sphere ", curved_surface_area)
        print("total surface area of sphere ", total_surface_area)

    def cylinder(self, radius, height):
        area = 2 * math.pi * radius (height * radius)
        curved_surface_area = 2 * math.pi * radius * height
        volume = math.pi * radius**2 * height
        print("\narea of cylinder ", area)
        print("curved surface area of cylinder ", curved_surface_area)
        print("volume of cylinder ", volume)

    def right_angled(self, base, height):
        c = math.sqrt(base**2 + height**2)
        perimeter = base + height + c
        area = 0.5 * base * height
        print("\narea of right angled triangle ", area)
        print("perimeter of right angled triangle ", perimeter)

    def isosceles(self, base, side):
        side_1 = side
        perimeter = base + side + side_1
        s = perimeter / 2
        area = math.sqrt(s * (s - base) * (s - side) * (s - side_1))
        print("\narea of isosceles triangle ", area)
        print("perimeter of isosceles triangle ", perimeter)

    def equilateral(self, side):
        perimeter = 3 * side
        area = math.sqrt(3) / 4 * side**2
        print("\narea of equilateral triangle ", area)
        print("perimeter of equilateral triangle ", perimeter)

    def scalene(self, side_1, side_2, side_3):
        perimeter = side_1 + side_2 + side_3
        s = perimeter / 2
        area = math.sqrt(s * (s - side_1) * (s - side_2) * (s - side_3))
        print("\narea of scalene triangle ", area)
        print("perimeter of scalene triangle ", perimeter)

    def triangle(self, side_1, side_2, side_3):
        perimeter = side_1 + side_2 + side_3
        s = perimeter / 2
        area = math.sqrt(s * (s - side_1) * (s - side_2) * (s - side_3))
        print("\narea of triangle ", area)
        print("perimeter of triangle ", perimeter)