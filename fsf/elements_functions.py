import element_dataclasses as ed


def teapot_slicing(position: ed.ElementPosition, num_slices: int):
    delta = position.length*(1/(2*num_slices + 2))
    separation = position.length*(num_slices/(num_slices**2 - 1))
    thin_positions =  [position.start+delta]
    for i in range(num_slices-1):
        thin_positions.append(thin_positions[-1] + separation)
    return thin_positions 
    
def slice_element(self, num_slices=1, method='teapot'):
    try: num_slices = self.int_steps
    except: AttributeError

    if self.length == 0:
        return [self]

    def _make_slices_multipoles(self, num_slices, knl_sliced=[0], ksl_sliced=[0]):
        thin_positions = self.teapot_slicing(num_slices)
        rad_length = self.length/num_slices
        seq = []
        for idx, thin_pos in enumerate(thin_positions):
            seq.append(ThinMultipole(f'{self.name}_{idx}', position=thin_pos, 
                                                                rad_length=rad_length, 
                                                                knl=knl_sliced, 
                                                                ksl=ksl_sliced))
        return seq

    def _make_slices_solenoid(self, num_slices, ksi_sliced):
        thin_positions = self.teapot_slicing(num_slices)
        rad_length = self.length/num_slices
        seq = []
        for idx, thin_pos in enumerate(thin_positions):
            seq.append(ThinSolenoid(f'{self.name}_{idx}', position=thin_pos, 
                                                            ksi=ksi_sliced, 
                                                            rad_length=rad_length))
        return seq

    if isinstance(self, Sbend):
        if num_slices == 1:
            seq = [ThinMultipole(self.name, position=getattr(self, 'position', 0), knl=[self.angle])]
        if method == 'teapot' and num_slices > 1:
            knl_sliced = [self.angle/num_slices]
            seq = _make_slices_multipoles(self, num_slices, knl_sliced=knl_sliced)
        
        h = self.angle/self.length
        seq.insert(0, DipoleEdge(f'{self.name}_edge_entrance', side='entrance', h=h, e1=self.e1, position=self.start))
        seq.append(DipoleEdge(f'{self.name}_edge_exit', h=h, side='exit', e1=self.e2, position=self.end))
        return seq
        
    if isinstance(self, Multipole):
        if num_slices == 1:
            return [ThinMultipole(self.name, position=getattr(self, 'position', 0), knl=self.knl, ksl=self.ksl)]
        elif method == 'teapot' and num_slices > 1:
            knl_sliced = self.knl/num_slices
            ksl_sliced = self.ksl/num_slices
            return _make_slices_multipoles(self, num_slices, knl_sliced=knl_sliced, ksl_sliced=ksl_sliced)
                
    if isinstance(self, Solenoid):
        if num_slices == 1:
            return [ThinSolenoid(self.name, position=getattr(self, 'position', 0), ksi=self.ksi)]
        elif method == 'teapot' and num_slices > 1:
            delta, distance = self.teapot_slicing(num_slices)
            ksi_sliced = self.ksi/num_slices
            return _make_slices_solenoid(self, num_slices, ksi_sliced)
