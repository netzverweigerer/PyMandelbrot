# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 23:55:50 2019

@author: Mauro
"""

#==============================================================================
# Constants
#==============================================================================

matlib_colormaps = ['viridis', 'plasma', 'inferno', 'magma', 'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds', 'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu', 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn', 'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink', 'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia', 'hot', 'afmhot', 'gist_heat', 'copper','Diverging', 'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu','RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic', 'Pastel1', 'Pastel2', 'Paired', 'Accent', 'Dark2', 'Set1', 'Set2', 'Set3', 'tab10', 'tab20', 'tab20b', 'tab20c', 'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern', 'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg', 'hsv', 'gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'gist_ncar']

available_colormaps = ["red", "blue", "black", "yellow"] + matlib_colormaps
available_modes = ["module", "phase", "imaginary", "real", "iteration"]
        


#==============================================================================
# Imports
#==============================================================================

# pyimports
import cmath

# matliplot/numpy
#  side note, these are unnecessary, used for colormap and save image
import matplotlib
import matplotlib.image as mpimg
import numpy as np

# user imports
import Matrix
import Color

#==============================================================================
# Linearization calss
#==============================================================================

class Linspace:
    '''Allows to space in equal step between two numbers'''
    
    def __init__(self, minv, maxv, nsteps):
        self.minv = minv
        self.maxv = maxv
        self.nsteps = nsteps
    
    def get(self, n):
        return (self.maxv - self.minv) / self.nsteps * n + self.minv

#==============================================================================
# Mandelbrot result object
#==============================================================================

class MandelResult:
    ''' the result of the mandelbrot function is stored in a value and a 
    boolean variable which tells if the number is in the set or not
    the operator overload allows the normalization and sorting of said values
    '''
    
    def __init__(self, res, in_set):
        self.res = res
        self.in_set = in_set

    def __lt__(self, other):
        return self.res < other.res
            
    def __le__(self, other):
        return self.res <= other.res
    
    def __eq__(self, other):
        return self.res == other.res
    
    def __ne__(self, other):
        return self.res != other.res
    
    def __gt__(self, other):
        return self.res >= other.res
    
    def __ge__(self, other):
        return self.res > other.res

    def __sub__(self, other):
        r = self.res - other.res
        return MandelResult(r, self.in_set)

    def __truediv__(self, other):
        r = self.res / other.res
        return MandelResult(r, self.in_set)

#==============================================================================
# A class to store the boundaries
#==============================================================================

class Boundaries:
    ''' class that manages the boundaries of the graph'''
    
    def __init__(self, width, height, minx, maxx, miny, maxy):
        self.linx = Linspace(minx, maxx, width)
        self.liny = Linspace(miny, maxy, height)
    
    def get_width(self):
        return self.linx.nsteps
    
    def get_height(self):
        return self.liny.nsteps

#==============================================================================
# Mandelbrot class
#==============================================================================

class Mandelbrot:
    ''' class that manages the mandelbrot core calculation.
    boundaries - the boundaries of the graph
    max_iteration - the maximal number of iterations, higher values leads to 
                    higher precision
    mode - can be "real", "imaginary", "phase", "module" or "iteration" and 
           determines how the last number of the iteration gets treated
    colormap - various color maps available in the matlab.cmap library and some
               custom colormaps
    '''
    
    def __init__(self, boundaries, max_iteration, mode, colormap):
        
        # placeholder to unclutter the code
        self.width = boundaries.get_width()
        self.height = boundaries.get_height()
        
        self.max_iteration = max_iteration
        self.colormap = colormap
        
        # matrixes used in the calculations
        self.color_matrix = None
        self.mandel_solution = None
        
        # create the input matrix
        input_matrix = Matrix.Matrix(self.width, self.height)
 
        for i in range(input_matrix.width):
            for j in range(input_matrix.height):
                re = boundaries.linx.get(i)
                im = boundaries.liny.get(j)
                input_matrix.set(i, j, complex(re, im))
        
        # calculate the mandelbrot and store the solution in the
        # mandel_solution variable
        print("calculating mandelbrot...")
        
        self.mandel_solution = Matrix.Matrix(self.width, self.height)
        for i in range(input_matrix.width):
            for j in range(input_matrix.height):
                # get the input
                c = input_matrix.get(i, j)
                
                # complex result of the iterations
                mr = self.calc_mandelbrot(c, mode);

                # structure that holds the in/out set value
                self.mandel_solution.set(i, j, mr)
        print("end calculation.")
    
    def value_mode(self, operation, value):
        ''' selects one of the possible outcomes, the lambda encoding allows
        to exectue only the operation selected
        '''
        
        operations = {}
        operations["module"] =lambda: abs(value)
        # normalized phase 0 to 1
        operations["phase"] = lambda:(cmath.phase(value)  + cmath.pi ) / (2 * cmath.pi)
        operations["imaginary"] =lambda: value.imag
        operations["real"] = lambda: value.real
        
        return operations[operation]()
        
    def calc_mandelbrot(self, c, mode):
        z = complex(0, 0)
        
        in_set = True
        i = 0
        for i in range(self.max_iteration):
            z = z * z + c
            if abs(z) > 2:
                in_set = False
                break

        if mode == "iteration":
            val = i
        else:
            val = self.value_mode(mode, z)        
        
        mr = MandelResult(val, in_set)
        return mr
    
    def get_color_matrix(self):
        ''' middle man function to create the color matrix only once '''
        if self.color_matrix is None:
            self.color_matrix = self.convert_to_color_matrix()
        return self.color_matrix

    def convert_to_color_matrix(self):
        ''' converts the solution matrix in a serie of "Color" elements
        '''
        print("converting color map...")
        bgcolor = Color.Color(0, 0, 0)
        color_matrix = Matrix.Matrix(self.width, self.height, bgcolor)
        
        self.mandel_solution.normalize01()
        
        for i in range(self.mandel_solution.width):
            for j in range(self.mandel_solution.height):  
                value = self.mandel_solution.get(i, j).res
                # if is not in the mandelbrot then use a color map
                # else paint it black
                if not self.mandel_solution.get(i, j).in_set:
                    color = self.color_function(self.colormap, value)
                else:
                    color = self.color_function("black", value)
                color_matrix.set(i, j, color)
        
        return color_matrix
    
    def color_function(self, method, value):
        ''' This function transforms the normalized from 0 to 1 value of the 
        of the mandelbrot solution and maps it to different color maps
        '''
        
        if method == "red":
            v = int(255 * value)
            color = Color.Color(255, 255 - v, 255 - v)
            return color
        
        elif method == 'blue':
            v = int(255 * value)
            color = Color.Color(255 - v, 255 - v, 255)
            return color  
        
        elif method == "black":
            return Color.Color(0, 0, 0)
        
        elif method == "yellow":
            v = int( value * 255 )
            color = Color.Color(255, v, 0)
            return color
        
        else:
            cmap = matplotlib.cm.get_cmap(method)
            cmap_value = cmap(value)
            val = lambda i : int(cmap_value[i] * 255)
            color = Color.Color(val(0), val(1), val(2))
            return color

    def save_image(self, filename):
        ''' saves the color matrix into a picture given the filename'''
        print("saving image...")

        color_matrix = self.get_color_matrix()
        
        arr = np.zeros([self.height, self.width, 3], np.uint8)
        
        for i in range(self.width):
            for j in range(self.height):
                color = color_matrix.get(i,j).get_limited()
                
                arr[j, i, 0] = color[0]
                arr[j, i, 1] = color[1]
                arr[j, i, 2] = color[2]   
        mpimg.imsave(filename, arr)

    

    
    