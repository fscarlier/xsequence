import xsequence.lattice as lat
import xsequence.elements as xe
from xsequence.conversion_utils import conv_utils

madx_lattice = conv_utils.create_cpymad_from_file('../xsequence/tests/test_sequences/lattice.seq', 120)
xsequence_lattice = lat.Lattice.from_cpymad(madx_lattice, 'l000013')

elements, line =xsequence_lattice.to_elegant(filename='./fcc_ee.lte')

print(elements)
print(line)
