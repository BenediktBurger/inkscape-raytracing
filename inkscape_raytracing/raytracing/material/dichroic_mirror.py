from typing import List

import numpy

from ..ray import Ray
from ..shade import ShadeRec
from .optic_material import OpticMaterial


class DichroicMirror(OpticMaterial):
    """Material reflecting beams that hit it"""

    def __init__(self, reflection_rule: str) -> None:
        super().__init__()
        self.reflection_rule = reflection_rule[1:]

    def __repr__(self):
        return "DichroicMirror()"

    def generated_beams(self, ray: Ray, shade: ShadeRec) -> List[Ray]:
        wavelength = ray.wavelength
        # HACK eval should be used with caution! REGEX?
        reflect = eval(self.reflection_rule)
        if reflect:
            o, d = shade.local_hit_point, ray.direction
            n = shade.normal
            reflected_ray = Ray(o, d - 2 * numpy.dot(d, n) * n)
            return [reflected_ray]
        else:
            return [Ray(shade.local_hit_point, direction=ray.direction)]
