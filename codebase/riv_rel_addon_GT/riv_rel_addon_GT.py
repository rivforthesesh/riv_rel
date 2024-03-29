# HUGE thanks to scumbumbo
# https://modthesims.info/showthread.php?t=616866

import services
import clubs.club_tuning
import sims4.resources
from sims4.tuning.instance_manager import InstanceManager
from sims4.resources import Types
from functools import wraps


def inject(target_function, new_function):
    @wraps(target_function)
    def _inject(*args, **kwargs):
        return new_function(target_function, *args, **kwargs)

    return _inject


def inject_to(target_object, target_function_name):
    def _inject_to(new_function):
        target_function = getattr(target_object, target_function_name)
        setattr(target_object, target_function_name, inject(target_function, new_function))
        return new_function

    return _inject_to


fam_ids = {'A': 0x8ffadecb, 'B': 0x8ffadec8, 'C': 0x8ffadec9, 'D': 0x8ffadece,
           'E': 0x8ffadecf, 'F': 0x8ffadecc, 'G': 0x8ffadecd, 'H': 0x8ffadec2}
inc_ids = {'A': 0x92c573ef, 'B': 0x92c573ec, 'C': 0x92c573ed, 'D': 0x92c573ea,
           'E': 0x92c573eb, 'F': 0x92c573e8, 'G': 0x92c573e9, 'H': 0x92c573e6}
fams = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']


# Note - This function should not be called prior to all trait tuning being
#        loaded into the game. It can be used any time after that.
#        Probably easiest to just use the method of injecting to the
#        load_data_into_class_instances method of the InstanceManager as
#        demonstrated in this example.
def add_trait_to_club_traits_list(trait_instance_id):
    # Get the tuned instance of the trait we want to add
    instance_manager = services.get_instance_manager(Types.TRAIT)
    key = sims4.resources.get_resource_key(trait_instance_id, Types.TRAIT)
    trait_tuning_instance = instance_manager.get(key)

    if trait_tuning_instance:
        # Get the frozenset that has the current trait list available for clubs
        club_trait_tuning = clubs.club_tuning.ClubTunables.CLUB_TRAITS

        # Convert that to a list
        club_trait_list = list(club_trait_tuning)

        # Add the desired trait to the list
        club_trait_list.append(trait_tuning_instance)

        # Convert back to a frozenset, and overwrite the CLUB_TRAITS tuning
        club_trait_tuning = frozenset(club_trait_list)
        clubs.club_tuning.ClubTunables.CLUB_TRAITS = club_trait_tuning


@inject_to(InstanceManager, 'load_data_into_class_instances')
def _load_club_trait_tuning(original, self):
    original(self)
    if self.TYPE == Types.TRAIT:
        for fam_id in fams:
            add_trait_to_club_traits_list(fam_ids[fam_id])
            add_trait_to_club_traits_list(inc_ids[fam_id])
