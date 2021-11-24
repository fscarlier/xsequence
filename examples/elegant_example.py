from xsequence.lattice import Lattice
import xsequence.elements as xe

# Create elements
q1 = xe.Quadrupole('q1', length=1, k1=0.2, location=1)
q2 = xe.Quadrupole('q2', length=1, k1=-0.2, location=3)
q3 = xe.Quadrupole('q3', length=1, k1=0.2, location=5)

element_dict = {'q1':q1, 'q2':q2, 'q3':q3}
lat = Lattice('lat_name', element_dict, key='sequence')

# Create elements
d0 = xe.Drift('d0', length=1)
q1 = xe.Quadrupole('q1', length=1, k1=0.2)
d1 = xe.Drift('d1', length=1)
q2 = xe.Quadrupole('q2', length=1, k1=-0.2)
d2 = xe.Drift('d1', length=1)
q3 = xe.Quadrupole('q3', length=1, k1=0.2)

element_dict = {'d0':d0, 'q1':q1, 'd1':d1, 
                'q2':q2, 'd2':d2, 'q3':q3}
lat = Lattice('lat_name', element_dict, key='line')

elements, line =lat.to_elegant(filename='./example.lte')
