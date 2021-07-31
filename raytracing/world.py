"""
Module to describe and interact with a scene composed of various optical
objects
"""

import warnings
from typing import Optional, List, NamedTuple, Iterable, Tuple

from .geometry import GeometricObject
from .material import OpticMaterial, BeamDump
from .ray import Ray
from .shade import ShadeRec


class OpticalObject(NamedTuple):
    geometry: GeometricObject
    material: OpticMaterial


class World:
    """Stores a scene and computes the interaction with a ray"""

    def __init__(self, list_: Optional[List[OpticalObject]] = None,
                 recursion_depth: Optional[int] = 500):
        if list_ is None:
            list_ = []
        self._objects = list(list_)
        # default recursion depth can be changed, but should not exceed
        # system recursion limit.
        self._max_recursion_depth = recursion_depth

    def add_object(self, obj: OpticalObject):
        self._objects.append(obj)

    def __iter__(self) -> Iterable[OpticalObject]:
        return iter(self._objects)

    @property
    def num_objects(self) -> int:
        return len(self._objects)

    def first_hit(self, ray: Ray) -> Tuple[ShadeRec, OpticMaterial]:
        """
        Returns the information about the first collision of the beam
        with an object.

        :return: A shade for the collision geometric information and the
        material of the object hit.
        """
        result = ShadeRec()
        material = BeamDump()
        for obj in self:
            shade = obj.geometry.hit(ray)
            if Ray.min_travel < shade.travel_dist < result.travel_dist:
                result = shade
                material = obj.material
        return result, material

    def propagate_beams(self, seed):
        return self._propagate_beams([[seed]], 0)

    def _propagate_beams(self, beams: List[List[Ray]], depth) \
            -> List[List[Ray]]:
        """Computes the propagation of beams in the system

        :return: List of all the beam paths generated by these seeds.
            It is stored as
            [path0[Ray0, Ray1, ...], path1[...], ...].
            Each path is a list of successive rays having each traveled a
            given distance.
        :raise: warning if recursion depth hits a limit.
        """

        if depth >= self._max_recursion_depth:
            err_msg = f"Maximal recursion depth exceeded (" \
                      f"{self._max_recursion_depth}). It is  likely that " \
                      f"not all beams have been rendered."
            warnings.warn(err_msg)
            return beams
        else:
            new_beams = list()
            for index, beam in enumerate(beams):
                ray = beam[-1]
                if ray.travel <= 0:
                    shade, material = self.first_hit(ray)
                    new_seeds = material.generated_beams(ray, shade)
                    beams[index][-1] = Ray(ray.origin, ray.direction,
                                           shade.travel_dist)
                    if len(new_seeds) == 0:
                        new_beams.append(beams[index])
                    for seed in new_seeds:
                        generated_beams = self._propagate_beams([[seed]],
                                                                depth + 1)
                        for new_beam in generated_beams:
                            new_beams.append(beams[index] + new_beam)
            return new_beams
