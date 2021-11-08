from xsequence.lattice import Lattice
from xsequence.conversion_utils import conv_utils
import xdeps, math

madx_lattice = conv_utils.create_cpymad_from_file("FCCee_h.seq", 120)
lat = Lattice.from_cpymad(madx_lattice, 'l000013')

lat.params['energy'] = 120
lat.line = lat.sequence._get_line()
plat = lat.to_pyat()

variables = {}

manager = xdeps.DepManager()
vref = manager.ref(variables,'v')
mref = manager.ref(math,'m')
sref = manager.ref(lat.sequence,'s')

lat.xdeps_manager =manager
lat.vref = vref
lat.mref = mref
lat.sref = sref

