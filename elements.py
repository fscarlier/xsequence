import numpy as np


class Element(object):
    """Base of pyat elements"""

    REQUIRED_ATTRIBUTES = ['FamName']

    _entrance_fields = ['T1', 'R1']
    _exit_fields = ['T2', 'R2']

    def __init__(self, family_name, **kwargs):
        self.FamName = family_name
        self.Length = kwargs.pop('Length', 0.0)
        self.Position = kwargs.pop('Position', 0.0)
        self.PassMethod = kwargs.pop('PassMethod', 'IdentityPass')
        self.update(kwargs)

    def __setattr__(self, key, value):
        try:
            super(Element, self).__setattr__(
                key, self._conversions.get(key, _nop)(value))
        except Exception as exc:
            exc.args = ('In element {0}, parameter {1}: {2}'.format(
                self.FamName, key, exc),)
            raise

    def __str__(self):
        first3 = ['FamName', 'Length', 'PassMethod']
        attrs = dict(self.items())
        keywords = ['\t{0} : {1!s}'.format(k, attrs.pop(k)) for k in first3]
        keywords += ['\t{0} : {1!s}'.format(k, v) for k, v in attrs.items()]
        return '\n'.join((self.__class__.__name__ + ':', '\n'.join(keywords)))

    def __repr__(self):
        attrs = dict(self.items())
        arguments = [attrs.pop(k, getattr(self, k)) for k in
                     self.REQUIRED_ATTRIBUTES]
        defelem = self.__class__(*arguments)
        keywords = ['{0!r}'.format(arg) for arg in arguments]
        keywords += ['{0}={1!r}'.format(k, v) for k, v in sorted(attrs.items())
                     if not numpy.array_equal(v, getattr(defelem, k, None))]
        args = re.sub('\n\s*', ' ', ', '.join(keywords))
        return '{0}({1})'.format(self.__class__.__name__, args)

    def equals(self, other):
        """Whether an element is equivalent to another.

        This implementation was found to be too slow for the generic
        __eq__ method when comparing lattices.

        """
        return repr(self) == repr(other)

    def divide(self, frac):
        """split the element in len(frac) pieces whose length
        is frac[i]*self.Length

        arguments:
            frac            length of each slice expressed as a fraction of the
                            initial length. sum(frac) may differ from 1.

        Return a list of elements equivalent to the original.

        Example:

        >>> Drift('dr', 0.5).divide([0.2, 0.6, 0.2])
        [Drift('dr', 0.1), Drift('dr', 0.3), Drift('dr', 0.1)]
        """
        # Bx default, the element is indivisible
        return [self]

    def update(self, *args, **kwargs):
        """Update the element attributes with the given arguments

        update(**kwargs)
        update(mapping, **kwargs)
        update(iterable, **kwargs)
        """
        attrs = dict(*args, **kwargs)
        for (key, value) in attrs.items():
            setattr(self, key, value)

    def copy(self):
        """Return a shallow copy of the element"""
        return copy.copy(self)

    def deepcopy(self):
        """Return a deep copy of the element"""
        return copy.deepcopy(self)

    def items(self):
        """Iterates through the data members including slots and properties"""
        # Get attributes
        for k, v in vars(self).items():
            yield k, v
        # Get slots and properties
        for k, v in getmembers(self.__class__, isdatadescriptor):
            if not k.startswith('_'):
                yield k, getattr(self, k)


class Element:
    """
    Base element class  

    Attributes
    ----------
    name : string
        name of element
    length : float
        length of element

    Methods
    -------
    string
        a value in a string

    """

    def __init__(self, name, **kwargs):
        self.name = name
        self.length = kwargs.pop('length', 0.0)
        try: self.pos = kwargs.pop('pos')
        except: KeyError
        self.update(kwargs)

    def update(self, **kwargs):
        for (key, value) in kwargs.items():
            self.setattr(key, value)

    def __str__(self):
        args_dict = vars(self).items()
        args_str = [f'{k}={v}' for k,v in args_dict if k!= 'name']
        return f"{self.__class__.__name__}('{self.name}', {', '.join(args_str)})"

    def __repr__(self):
        args_dict = vars(self).items()
        args_str = [f'{k}={v}' for k,v in args_dict if k!= 'name']
        return f"{self.__class__.__name__}('{self.name}', {', '.join(args_str)})"



class Drift(Element):
    """
    Drift specifc element class

    Attributes
    ----------
    name : string
        name of element
    length : float
        length of element, cannot be 0.0

    Methods
    -------
    string
        a value in a string

    """
    def __init__(self, name, **kwargs):
        assert kwargs.pop('length') > 0.0
        super().__init__(name, **kwargs)


class Marker(Element):
    """
    Marker specifc element class
    
    Attributes
    ----------
    name : string
        name of element
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class Dipole(Element):   
    """
    Dipole specific element class
    
    Attributes
    ----------
    name : string
        name of element
    length : float
        arc_length of bending magnet
    chord_length : float
        straight line length from entry to exit (see rbends in MAD-X)
    angle : float
        bending angle of bend magnet
    bend_type : string
        'sbend' or 'rbend', see MAD-X documentation
    
    Methods
    -------
    _calc_arclength()
        Calculate arclength from angle and rbend r_length

    """
    def __init__(self, name, angle=0.0, bend_type='sbend', **kwargs):
        super().__init__(name, **kwargs)
        self.bend_type = bend_type
        self.angle = angle

        if self.bend_type == 'sbend':
            self.length = kwargs.pop('length', 0.0)
            self.chord_length = self._calc_chordlength() 
        elif self.bend_type == 'rbend':
            self.chord_length = kwargs.pop('chord_length', 0.0)
            self.length = self._calc_arclength() 
        self.e1 = kwargs.pop('e1', 0.0)
        self.e2 = kwargs.pop('e2', 0.0)
     
    def _calc_arclength(self) :
        """ Calculate arc length from angle and chord length """
        return (self.angle*self.chord_length)/(2*np.sin(self.angle/2.))

    def _calc_chordlength(self) :
        """ Calculate chord length from angle and arc length """
        return self.length*(2*np.sin(self.angle/2.))/self.angle


class SBend(Element):   
    """
    Dipole specific element class
    
    Attributes
    ----------
    name : string
        name of element
    length : float
        arc_length of bending magnet
    chord_length : float
        straight line length from entry to exit (see rbends in MAD-X)
    angle : float
        bending angle of bend magnet
    bend_type : string
        'sbend' or 'rbend', see MAD-X documentation
    
    Methods
    -------
    _calc_arclength()
        Calculate arclength from angle and rbend r_length

    """
    def __init__(self, name, angle=0.0, bend_type='sbend', **kwargs):
        super().__init__(name, **kwargs)
        self.bend_type = bend_type
        self.angle = angle

        if self.bend_type == 'sbend':
            self.length = kwargs.pop('length', 0.0)
            self.chord_length = self._calc_chordlength() 
        elif self.bend_type == 'rbend':
            self.chord_length = kwargs.pop('chord_length', 0.0)
            self.length = self._calc_arclength() 
        self.e1 = kwargs.pop('e1', 0.0)
        self.e2 = kwargs.pop('e2', 0.0)
     
    def _calc_arclength(self) :
        """ Calculate arc length from angle and chord length """
        return (self.angle*self.chord_length)/(2*np.sin(self.angle/2.))

    def _calc_chordlength(self) :
        """ Calculate chord length from angle and arc length """
        return self.length*(2*np.sin(self.angle/2.))/self.angle


class RBend(Element):   
    """
    Dipole specific element class
    
    Attributes
    ----------
    name : string
        name of element
    length : float
        arc_length of bending magnet
    chord_length : float
        straight line length from entry to exit (see rbends in MAD-X)
    angle : float
        bending angle of bend magnet
    bend_type : string
        'sbend' or 'rbend', see MAD-X documentation
    
    Methods
    -------
    _calc_arclength()
        Calculate arclength from angle and rbend r_length

    """
    def __init__(self, name, angle=0.0, bend_type='sbend', **kwargs):
        super().__init__(name, **kwargs)
        self.bend_type = bend_type
        self.angle = angle

        if self.bend_type == 'sbend':
            self.length = kwargs.pop('length', 0.0)
            self.chord_length = self._calc_chordlength() 
        elif self.bend_type == 'rbend':
            self.chord_length = kwargs.pop('chord_length', 0.0)
            self.length = self._calc_arclength() 
        self.e1 = kwargs.pop('e1', 0.0)
        self.e2 = kwargs.pop('e2', 0.0)
     
    def _calc_arclength(self) :
        """ Calculate arc length from angle and chord length """
        return (self.angle*self.chord_length)/(2*np.sin(self.angle/2.))

    def _calc_chordlength(self) :
        """ Calculate chord length from angle and arc length """
        return self.length*(2*np.sin(self.angle/2.))/self.angle


class Quadrupole(Element):
    """
    Quadrupole specifc element class
    
    Attributes
    ----------
    name : string
        name of element
    knl : float array
        normal magnetic strengths array to arbitrary order
    ksl : float array
        skew magnetic strengths array to arbitrary order
    
    Methods
    -------
    _calc_arclength()
        Calculate arclength from angle and rbend r_length

    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.knl = kwargs.pop('knl', [0.0, 0.0])
        self.ksl = kwargs.pop('ksl', [0.0, 0.0])


class Sextupole(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.knl = kwargs.pop('knl', [0.0, 0.0, 0.0])
        self.ksl = kwargs.pop('ksl', [0.0, 0.0, 0.0])


class Octupole(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class RFCavity(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.volt = kwargs.pop('volt', 0.0)
        self.freq = kwargs.pop('freq', 0.0)

class Solenoid(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ThinMultipole(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
    
    
class DipoleEdge(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ClosedOrbitCorrector(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class TransverseKicker(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class TravellingWaveCavity(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ThinRFMultipole(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class CrabCavity(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ACDipole(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ElectrostaticSeparator(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class BeamPositionMonitor(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class Instrument(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class Placeholder(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class Collimator(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class BeamBeam(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ArbitraryMatrixElement(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)




