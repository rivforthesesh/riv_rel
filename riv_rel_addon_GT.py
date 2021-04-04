# uncompyle6 version 3.7.3
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.0 (v3.7.0:1bf9cc5093, Jun 27 2018, 04:59:51) [MSC v.1914 64 bit (AMD64)]
# Embedded file name: D:\Users\River\Documents\Electronic Arts\The Sims 4\Mods (bts, unused, extra apps)\--- MINE ---\riv_rel\to compile\riv_rel_addon_GT.py
# Compiled at: 2020-12-13 21:34:13
# Size of source mod 2**32: 2173 bytes
import services, clubs.club_tuning, sims4.resources
from sims4.tuning.instance_manager import InstanceManager
from sims4.resources import Types
from injector import inject_to
fam_ids = {'A':2415582923, 
 'B':2415582920,  'C':2415582921,  'D':2415582926,  'E':2415582927, 
 'F':2415582924,  'G':2415582925,  'H':2415582914}
inc_ids = {'A':2462413807,  'B':2462413804,  'C':2462413805,  'D':2462413802,  'E':2462413803, 
 'F':2462413800,  'G':2462413801,  'H':2462413798}
fams = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

def add_trait_to_club_traits_list(trait_instance_id):
    instance_manager = services.get_instance_manager(Types.TRAIT)
    key = sims4.resources.get_resource_key(trait_instance_id, Types.TRAIT)
    trait_tuning_instance = instance_manager.get(key)
    if trait_tuning_instance:
        club_trait_tuning = clubs.club_tuning.ClubTunables.CLUB_TRAITS
        club_trait_list = list(club_trait_tuning)
        club_trait_list.append(trait_tuning_instance)
        club_trait_tuning = frozenset(club_trait_list)
        clubs.club_tuning.ClubTunables.CLUB_TRAITS = club_trait_tuning


@inject_to(InstanceManager, 'load_data_into_class_instances')
def _load_club_trait_tuning(original, self):
    original(self)
    if self.TYPE == Types.TRAIT:
        for id in fams:
            add_trait_to_club_traits_list(fam_ids[id])
            add_trait_to_club_traits_list(inc_ids[id])
# okay decompiling riv_rel_addon_GT.pyc
