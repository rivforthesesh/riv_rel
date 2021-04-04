from server_commands.argument_helpers import SimInfoParam
# from relationships.relationship_service import RelationshipService
# from server_commands.genealogy_commands import get_family_relationship_bit
# from sims.sim_info import get_sim_instance, get_name_data
from sims.sim_info import SimInfo
import services, sims4.commands, sims.sim_info_types, sims.sim_info_manager, server_commands.relationship_commands
from relationships.relationship import Relationship
from relationships.relationship_bit import RelationshipBit
from relationships.relationship_tracker import RelationshipTracker
from typing import List, Dict
from functools import wraps
import sims4.resources
from sims4.resources import Types, get_resource_key
from sims4.tuning.instance_manager import InstanceManager
import random
from distributor.shared_messages import IconInfoData
from sims4.collections import make_immutable_slots_class
from sims4.localization import LocalizationHelperTuning, _create_localized_string
from ui.ui_dialog import UiDialogResponse, ButtonType, CommandArgType
from ui.ui_dialog_notification import UiDialogNotification
import json
import date_and_time

# replacing the code stolen from sim info with frankk's input
# https://discordapp.com/channels/605863047654801428/624442188335415320/760257300002504756
import os
from pathlib import Path

# services, sims4.commands:
#   @sims4.commands.Command
#   command_type=sims4.commands.CommandType.Live
#   output = sims4.commands.CheatOutput(_connection)
# sims.sim_info_manager:
#   get_sim_info_by_name
# find out what specifically we need from sims.sim_info

# commands break if sim has spaces in their first/last names (e.g. Rhona Pine I)
# overcome with Rhona "Pine I"

# returns the player's locale (for translation stuff)
#@sims4.commands.Command('riv_get_locale', command_type=sims4.commands.CommandType.Live)
#def riv_get_locale(_connection=None):
#    output = sims4.commands.CheatOutput(_connection)
#    output(services.get_locale())

# riv_sim_list and riv_rel_dict will be used if riv_sim_list is not empty!
# for now, sim_x and sim_y in commands MUST be sims that exist in the game

# range(a,b)   = [a, b) \cap ZZ
# range(a,b+1) = [a, b] \cap ZZ

### RivSim, RivSimList

class RivSim:
    def __init__(self, sim_x): # will only be created in game, so current time will be readily available
        # creates RivSim from Dict (in json)
        # this code assumes that the keys exist, so make sure you're importing the right thing!
        if isinstance(sim_x, Dict):
            self.sim_id = str(sim_x['sim_id']) # should be a string anyway
            self.first_name = sim_x['first_name']
            self.last_name = sim_x['last_name']
            self.is_female = sim_x['is_female']
            self.is_culled = sim_x['is_culled']
            self.time = sim_x['time']
        # creates RivSim from SimInfoParam (in game)
        else: # elif isinstance(sim_x, SimInfoParam):
            self.sim_id = str(sim_x.sim_id) # bc json keys need to be strings
            self.first_name = sim_x.first_name
            self.last_name = sim_x.last_name
            self.is_female = sim_x.is_female
            self.is_culled = False
            self.time = services.time_service().sim_now.absolute_ticks() # might have an error

    def to_dict(self):
        return {
            'sim_id': self.sim_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_female': self.is_female,
            'is_culled': self.is_culled,
            'time': self.time
        }

    # for marking a sim as culled; do this if the sim cannot be found
    def cull(self):
        self.is_culled = True

    # for updating a sim in the file if that sim exists with different details
    def update_info(self, new_first_name, new_last_name, new_gender, new_time):
        self.first_name = new_first_name
        self.last_name = new_last_name
        self.is_female = new_gender
        self.time = new_time

class RivSimList:
    sims = []

    # loads in list of sims from .json
    def load_sims(self, file_name_extra: str):
        # clears sims if they exist
        if self.sims:
            self.sims = []

# from os import sep as os_separator         # at top of file
# file_name = 'riv_rel_' + file_name_extra + '.json'  # e.g. riv_rel_pine.json
# scriptFullPath = normpath(__file__)
# fileparts = scriptFullPath.split(os_separator)
# if 1 < len(fileparts):
#   outputFullPath = '{}'.format(os_separator).join(fileparts[:len(fileparts) - 2]) + '{}{}'.format(os_separator, file_name)
# with open(outputFullPath, 'r') as json_file:
#   temp_sims = json.load(json_file)

        file_dir = Path(__file__).resolve().parent.parent
        file_name = 'riv_rel_' + file_name_extra + '.json'  # e.g. riv_rel_pine.json
        file_path = os.path.join(file_dir, file_name)

        # https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
        with open(file_path, 'r') as json_file:
            temp_sims = json.load(json_file)
        for sim in temp_sims:
            self.sims.append(RivSim(sim))
        return self.sims

    def update_sims(self, file_name_extra: str):
        pass # still need to do this!!!

    def clear_sims(self):
        self.sims = []

class RivRelDict:
    rels = {}

    # loads in dict of rels from .json
    def load_rels(self, file_name_extra: str):
        # clears rels if they exist
        if self.rels:
            self.rels = []

        file_dir = Path(__file__).resolve().parent.parent
        file_name = 'riv_relparents_' + file_name_extra + '.json'  # e.g. riv_rel_pine.json
        file_path = os.path.join(file_dir, file_name)

        # https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
        with open(file_path, 'r') as json_file:
            self.rels = json.load(json_file)
        return self.rels

    def update_rels(self, file_name_extra: str):
        pass # still need to do this!!!

    def clear_rels(self):
        self.rels = {}

# this is within class Zone in simulation/zone.py
#
#     def on_households_and_sim_infos_loaded(self):
#         self._set_zone_state(zone_types.ZoneState.HOUSEHOLDS_AND_SIM_INFOS_LOADED)
#         object_preference_tracker = services.object_preference_tracker()
#         if object_preference_tracker is not None:
#             object_preference_tracker.convert_existing_preferences()
#
# maybe use for replacing code to run on zone spin up as in
# https://medium.com/swlh/the-sims-4-modern-python-modding-project-1-random-pitch-2371b79c0bcc

# creates empty lists
# this will store sims as RivSims and rels as a dict with sim_id: [parent_id1, parent_id2]
riv_sim_list = RivSimList()
riv_rel_dict = RivRelDict()

## input: two sims. output: list of relbits
@sims4.commands.Command('riv_show_relbits', command_type=sims4.commands.CommandType.Live)
def console_show_relbits(sim_x: SimInfoParam, sim_y: SimInfoParam, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    relbits = services.relationship_service().get_all_bits(sim_x.sim_id, sim_y.sim_id)
    output(str(relbits))

## input: a sim ID as Int or String. output: the corresponding RivSim in mem
def get_rivsim_from_id(sim_id):
    if isinstance(sim_id, int): # if the ID is an integer
        return get_rivsim_from_id(str(sim_id)) # calls the function again but with sim_id as string
    else:
        for rivsim in riv_sim_list.sims: # for all rivsims
            if rivsim.sim_id == sim_id: # if it has the same ID
                return rivsim # then this is the rivsim we want

## input: a sim as SimInfoParam or RivSim. output: the corresponding RivSim in mem
def get_rivsim_from_sim(sim_z):
    if isinstance(sim_z, RivSim): # if this is a rivsim
        return sim_z # then just return the rivsim
    else: # this will be a SimInfoParam
        return get_rivsim_from_id(str(sim_z.sim_id)) # so we get rivsim from the id

## input: a sim. output: list of their parents
def get_parents(sim_x):
    sim_parents = []

    if riv_sim_list.sims: # using list in mem
        rivsim_x = get_rivsim_from_sim(sim_x) # rivsim_x is the entry for sim_x in riv_sim_list.sims
        x_id = rivsim_x.sim_id # and this is the ID as a string
        for y_id in riv_rel_dict.rels.get(x_id): # for each y_id in the list of sim_x's parents
                # {x_id: [y_id,...]}
            rivsim_y = get_rivsim_from_id(y_id) # get rivsim_y as a rivsim
            sim_parents.append(rivsim_y) # then add rivsim_y to the list

    else: # using sims in game
        manager = services.get_instance_manager(Types.RELATIONSHIP_BIT)
        parent_relbit = manager.get(0x2269)
        for sim_y in services.sim_info_manager().get_all():
            if sim_x.relationship_tracker.has_bit(sim_y.sim_id, parent_relbit):
                sim_parents.append(sim_y)

    return sim_parents

## the above as a console command
@sims4.commands.Command('riv_get_parents', command_type=sims4.commands.CommandType.Live)
def console_get_parents(sim_x: SimInfoParam, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    sim_parents = get_parents(sim_x)
    output('DEBUG: ' + str(sim_parents))
    if not sim_parents:
        output('{}\'s parents not found'.format(sim_x.first_name))
    else:
        for sim_y in sim_parents:
            output('{} {} is {}\'s parent'.format(sim_y.first_name, sim_y.last_name, sim_x.first_name))

# input: a sim. output: dictionary of their ancestors sim_z with values (gens back, via child of sim_z)
# note the values are lists!!
# look into defaultdict later to rework adding items to the list
def get_ancestors(sim_x):
    ancestors = {} # stores ancestors as {sim_z: [(n, sim_zx), (n, sim_zx)]} where
        # sim_z is n generations back from sim_x
        # sim_zx child of sim_z and ancestor of sim_x
    queue = [] # stores sims to check
    templist = [] # because appending items to lists in dicts does not work well

    if riv_sim_list.sims: # using list in mem
        sim_x = get_rivsim_from_sim(sim_x) # rivsim_x is the entry for sim_x in riv_sim_list.sims

    for sim_z in get_parents(sim_x):
        queue.append((sim_z,1,sim_x))
    while queue:
        tuple_znzx = queue[0] # gets first (sim_z, n, sim_zx)
        sim_z = tuple_znzx[0]
        n = tuple_znzx[1]
        sim_zx = tuple_znzx[2]
        queue.pop(0) # removes first item (tuple_znzx) from the queue
        for parent in get_parents(sim_z):
            queue.append((parent, n+1, sim_z)) # adds parents of sim_z to the queue
        if sim_z in ancestors.keys():
            temp_list = ancestors[sim_z]
            temp_list.append((n,sim_zx))
            ancestors[sim_z] = temp_list
            temp_list = []
        else:
            ancestors[sim_z] = [(n, sim_zx)]  # adds sim_z: [(n, sim_zx)] to the dictionary
    return ancestors # dictionary of sim_z: (n, sim_zx) for sim_z ancestor, n gens back, via sim_zx

# the above as a console command. redundant except for debugging
@sims4.commands.Command('riv_get_ancestors', command_type=sims4.commands.CommandType.Live)
def console_get_ancestors(sim_x: SimInfoParam, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    x_ancestors = get_ancestors(sim_x)
    if not x_ancestors:
        output('{}\'s ancestors not found'.format(sim_x.first_name))
    else:
        for sim_y in x_ancestors.keys():
            for sim_z in x_ancestors[sim_y]:
                output('{} {} is {} {}\'s ancestor, {} generations back'.format(sim_y.first_name, sim_y.last_name, sim_x.first_name, sim_x.last_name, sim_z[0]))

# input: two sims and ancestors. output: None if there is no direct relation, generational difference if there is
def get_direct_rel(sim_x: SimInfoParam, sim_y: SimInfoParam, x_ancestors: Dict, y_ancestors: Dict):
    xy_direct_rel = []

    if riv_sim_list.sims: # if using riv_sim_list, we want to use RivSims (bc these rels might not rely on a connection)
        sim_x = get_rivsim_from_sim(sim_x)
        sim_y = get_rivsim_from_sim(sim_y)

    if sim_x.sim_id == sim_y.sim_id: # same sim
        xy_direct_rel.append(0)
    if sim_y in x_ancestors.keys(): # sim_y is a direct ancestor of sim_x
        for sim_z in x_ancestors[sim_y]:
            xy_direct_rel.append(sim_z[0]) # gets each n from {sim_y: [sim_z = (n, sim_yx), (n, sim_yx), ...]}
    if sim_x in y_ancestors.keys(): # sim_x is a direct ancestor of sim_y
        for sim_z in y_ancestors[sim_x]:
            xy_direct_rel.append(-sim_z[0]) # gets each -n from {sim_x: [sim_z = (n, sim_xy), (n, sim_xy), ...]}

    return xy_direct_rel
# ... -1 => sim_x parent of sim_y, 0 => sim_x is sim_y, 1 => sim_x child of sim_y, ...

# input: two sims. output: None if there is no direct relation, generational difference if there is
def get_direct_relation(sim_x: SimInfoParam, sim_y: SimInfoParam):
    return get_direct_rel(sim_x, sim_y, get_ancestors(sim_x), get_ancestors(sim_y))

# input: a number and two sims. output: sim_x's relation to sim_y
# gens = xy_direct_rel
# gender bit is for compatibility with inlaw rels
def format_direct_rel_gender(gens: List, sim_x: SimInfoParam, sim_y: SimInfoParam, gender: int):
    gens_str = []
    for n in gens:
        rel_str = ''
        if abs(n) > 1:
            if abs(n) > 2:
                rel_str += 'great'
                if abs(n) > 3:
                    rel_str += '(x' + str(abs(n) - 2) + ')'
                rel_str += '-'
            rel_str += 'grand'
        if n > 0:
            if gender:
                rel_str += 'daughter'
            else:
                rel_str += 'son'
        elif n < 0:
            if gender:
                rel_str += 'mother'
            else:
                rel_str += 'father'
        elif n == 0:
            rel_str = 'self'
        gens_str.append(rel_str)
    return gens_str

def format_direct_rel(gens: List, sim_x: SimInfoParam, sim_y: SimInfoParam):
    return format_direct_rel_gender(gens, sim_x, sim_y, sim_x.is_female)

# direct relation as a console command
@sims4.commands.Command('riv_get_direct_rel', command_type=sims4.commands.CommandType.Live)
def console_get_direct_rel(sim_x: SimInfoParam, sim_y: SimInfoParam, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    if sim_x is not None:
        if sim_y is not None:
            xy_direct_rel = get_direct_relation(sim_x,sim_y)
            if not xy_direct_rel: # there is no direct relation, list is empty
                output('no direct rel found between {} and {}'.format(sim_x.first_name, sim_y.first_name))
            else:
                xy_direct_rel_str = format_direct_rel(xy_direct_rel, sim_x, sim_y)
                for xy_rel in xy_direct_rel_str:
                    output('{} {} is {} {}\'s {}.'.format(sim_x.first_name, sim_x.last_name, sim_y.first_name, sim_y.last_name, xy_rel))

## input: two sims. output: the strength of their siblinghood
# 0 if not sibs, 0.5 if half-sibs, 1 if full sibs (or undetermined bc parents don't exist)
def get_sib_strength(sim_x: SimInfoParam, sim_y: SimInfoParam):
    x_parents = get_parents(sim_x)
    y_parents = get_parents(sim_y)
    z_parents = [value for value in x_parents if value in y_parents] # intersection of list
    if riv_sim_list.sims: # if using riv_sim_list
        if len(z_parents) == 2:  # two shared parents
            return 1  # if x and y share two parents, they are full siblings.
        elif len(z_parents) == 1:  # one shared parent
            if len(x_parents) == 1 and len(y_parents) == 1:
                return 1  # if x and y only have one parent and it is the same sim, ASSUME they are full siblings
            return 0.5  # if x has one parent and y has two parents, sharing one, they are half siblings
            # if x and y each have two parents and only share one, they are half siblings
        else:  # no shared parents
            if len(x_parents) == 0 and len(y_parents) == 0:
                return 1  # if they have the sibling rel bit and neither has parents, ASSUME they are full siblings
            return 0.5  # x or y may or may not have parents, x and y have sibling rel bit
    else:
        manager = services.get_instance_manager(Types.RELATIONSHIP_BIT)
        sibling_relbit = manager.get(0x2262)
        if sim_x.relationship_tracker.has_bit(sim_y.sim_id, sibling_relbit):
            if len(z_parents) == 2: # two shared parents
                return 1 # if x and y share two parents, they are full siblings.
            elif len(z_parents) == 1: # one shared parent
                if len(x_parents) == 1 and len(y_parents) == 1:
                    return 1 # if x and y only have one parent and it is the same sim, ASSUME they are full siblings
                return 0.5 # if x has one parent and y has two parents, sharing one, they are half siblings
                # if x and y each have two parents and only share one, they are half siblings
            else: # no shared parents
                if len(x_parents) == 0 and len(y_parents) == 0:
                    return 1 # if they have the sibling rel bit and neither has parents, ASSUME they are full siblings
                return 0.5 # x or y may or may not have parents, x and y have sibling rel bit
        return 0

## the above as a console command
@sims4.commands.Command('riv_get_sib_strength', command_type=sims4.commands.CommandType.Live)
def console_get_sib_strength(sim_x: SimInfoParam, sim_y: SimInfoParam, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    sib_strength = get_sib_strength(sim_x, sim_y)
    if sim_x == sim_y:
        output('{} is {}.'.format(sim_x.first_name, sim_y.first_name))
    elif sib_strength == 1:
        output('{} and {} are full siblings.'.format(sim_x.first_name, sim_y.first_name))
    elif sib_strength == 0.5:
        output('{} and {} are half-siblings.'.format(sim_x.first_name, sim_y.first_name))
    elif sib_strength == 0:
        output('{} and {} are not siblings.'.format(sim_x.first_name, sim_y.first_name))
    else:
        output('something went wrong')

# input: two sims and ancestors. output: None if there is no indirect relation, list if there is
def get_indirect_rel(sim_x: SimInfoParam, sim_y: SimInfoParam, x_ancestors: Dict, y_ancestors: Dict):
    # list is empty if it's the same sim
    if sim_x == sim_y:
        return []

    xy_ancestors = [value for value in x_ancestors.keys() if value in y_ancestors.keys()] # intersection of list

    # get list of shared ancestors [(sim_z, nx, ny, sim_zx, sim_zy)]
        # where sim_zx =/= sim_zy are siblings, children of sim_z, ancestors of x,y resp; nx, ny gens back
    xy_rels = [] # dumps all shared ancestors with needed info
    for sim_z in xy_ancestors: # {sim_z: [(n, sim_zx),...],...}
        for sim_xz in x_ancestors[sim_z]: # x_ancestors[sim_z] = [sim_xz,...], sim_xz = (n, sim_zx)
            for sim_yz in y_ancestors[sim_z]:
                nx = sim_xz[0]
                ny = sim_yz[0]
                sim_zx = sim_xz[1]
                sim_zy = sim_yz[1]
                if not sim_zx == sim_zy:
                    xy_rels.append((sim_z, nx, ny, sim_zx, sim_zy))

    # case handling siblings where both parents exist
    xy_indirect_rels = [] # will be the output
    to_remove = [] # to be removed from xy_rels
    for rel_one in xy_rels:
        for rel_two in xy_rels:
            if not rel_one[0] == rel_two[0]:
                if rel_one[1:] == rel_two[1:]: # i.e. (nx, ny, sim_zx, sim_zy) is the same
                    # this indicates these are the parents
                    if rel_one[0].sim_id < rel_two[0].sim_id: # ensures we don't have (sim1, sim2,...), (sim2, sim1,...) for parents
                        to_add = (rel_one[0], rel_two[0], rel_one[1], rel_one[2], 1)
                        if not to_add in xy_indirect_rels: # removes duplicates
                            xy_indirect_rels.append(to_add)
                            if not rel_one in to_remove:
                                to_remove.append(rel_one)
                            if not rel_two in to_remove:
                                to_remove.append(rel_two)

    # remove rels handled above
    for rel in to_remove:
        if rel in xy_rels:
            xy_rels.remove(rel)

    # case handling the ones that are from one shared parent
    for rel in xy_rels:
        to_add = (rel[0], rel[0], rel[1], rel[2], get_sib_strength(rel[3], rel[4]))
        if not to_add in xy_indirect_rels:
            xy_indirect_rels.append(to_add)

    # case handling filled gaps by indirect relations
    # i.e. there exists a close indirect relation between sim_xx and sim_yy where
        # sim_xx is an ancestor of only sim_x
        # sim_yy is an ancestor of only sim_y
        # sim_xx has no parent who is an ancestor of sim_x and sim_y

    if not riv_sim_list.sims: # only bother with this if using only sims in game
        xx = [] # list of sims who are x or ancestors of x and not y
        yy = [] # list of sims who are y or ancestors of y and not x
        x_ancestors[sim_x] = [(0, sim_x)] # here it helps to have the sim's self
        y_ancestors[sim_y] = [(0, sim_y)] # trust me it'll be useful later
        for sim_xx in x_ancestors.keys():
            if not sim_xx in y_ancestors.keys():
                xx.append(sim_xx)
        for sim_yy in y_ancestors.keys():
            if not sim_yy in x_ancestors.keys():
                yy.append(sim_yy)

        # x (has an ancestor who) is a close indirect relative of y('s ancestor), but these share no ancestor who is an ancestor of x AND y
        manager = services.get_instance_manager(Types.RELATIONSHIP_BIT)
        sibling_relbit = manager.get(0x2262)
        cousin_relbit = manager.get(0x227A)
        pibling_relbit = manager.get(0x227D)
        nibling_relbit = manager.get(0x2705)
        for sim_xx in xx:
            for sim_yy in yy:

                # sim_xx and sim_yy siblings, with no parent who is an ancestor of x and y
                if sim_xx.relationship_tracker.has_bit(sim_yy.sim_id, sibling_relbit):
                    zz_parents = [value for value in get_parents(sim_xx) if value in get_parents(sim_yy)]  # parents shared by sim_xx and sim_yy
                    if not [value for value in zz_parents if value in xy_ancestors]: # if sim_xx and sim_yy have no parents that are ancestors of sim_x and sim_y
                        for sim_xz in x_ancestors[sim_xx]:  # x_ancestors[sim_xx] = [sim_xz,...], sim_xz = (n, sim) where sim_xx is n gens back from sim_x via sim
                            for sim_yz in y_ancestors[sim_yy]: # y_ancestors[sim_yy] = [sim_yz,...], sim_yz = (n, sim) where sim_yy is n gens back from sim_x via sim
                                nx = sim_xz[0]
                                ny = sim_yz[0]
                                to_add = (sim_xx, sim_yy, nx + 1, ny + 1, get_sib_strength(sim_xx, sim_yy)) # connections are sibs (sharing parents), so gen + 1
                                if not to_add in xy_indirect_rels:
                                    xy_indirect_rels.append(to_add)

                # sim_yy pibling of sim_xx, and there are no siblings to check
                elif sim_xx.relationship_tracker.has_bit(sim_yy.sim_id, pibling_relbit):
                    for sim_xxx in get_parents(sim_xx):
                        if sim_xxx.relationship_tracker.has_bit(sim_yy.sim_id, sibling_relbit):
                            # this case will already by covered by sib case, using yy's parent = xx's sib
                            break
                    else:
                        for sim_xz in x_ancestors[sim_xx]:  # x_ancestors[sim_xx] = [sim_xz,...], sim_xz = (n, sim) where sim_xx is n gens back from sim_x via sim
                            for sim_yz in y_ancestors[sim_yy]:  # y_ancestors[sim_yy] = [sim_yz,...], sim_yz = (n, sim) where sim_yy is n gens back from sim_x via sim
                                nx = sim_xz[0]
                                ny = sim_yz[0]
                                to_add = (sim_xx, sim_yy, nx + 2, ny + 1, 1)  # connections are nibling + pibling, so an extra 2, 1 to joining point. assume missing parent of xx is yy's full sib
                                if not to_add in xy_indirect_rels:
                                    xy_indirect_rels.append(to_add)

                # sim_xx nibling of sim_yy, and there are no siblings to check
                elif sim_xx.relationship_tracker.has_bit(sim_yy.sim_id, nibling_relbit):
                    for sim_yyy in get_parents(sim_yy):
                        if sim_yyy.relationship_tracker.has_bit(sim_xx.sim_id, sibling_relbit):
                            # this case will already by covered by sib case, using xx's parent = yy's sib
                            break
                    else:
                        for sim_xz in x_ancestors[sim_xx]:  # x_ancestors[sim_xx] = [sim_xz,...], sim_xz = (n, sim) where sim_xx is n gens back from sim_x via sim
                            for sim_yz in y_ancestors[sim_yy]:  # y_ancestors[sim_yy] = [sim_yz,...], sim_yz = (n, sim) where sim_yy is n gens back from sim_x via sim
                                nx = sim_xz[0]
                                ny = sim_yz[0]
                                to_add = (sim_xx, sim_yy, nx + 1, ny + 2, 1)  # connections are pibling + nibling, so an extra 1, 2 to joining point. assume missing parent of yy is xx's full sib
                                if not to_add in xy_indirect_rels:
                                    xy_indirect_rels.append(to_add)

                # sim_xx and sim_yy first cousins, and there are no siblings to check (between sim_xx+parents AND sim_yy+parents)
                elif sim_xx.relationship_tracker.has_bit(sim_yy.sim_id, cousin_relbit):
                    for sim_xxx, sim_yyy in get_pairs_yield(get_parents(sim_xx) + [sim_xx], get_parents(sim_yy) + [sim_yy]):
                        if sim_xxx.relationship_tracker.has_bit(sim_yyy.sim_id, sibling_relbit):
                            # this case will already be covered by sib cases above
                            break
                        if sim_xxx.relationship_tracker.has_bit(sim_yy.sim_id, nibling_relbit):
                            # handled by nibling case
                            break
                        if sim_yyy.relationship_tracker.has_bit(sim_xx.sim_id, nibling_relbit):
                            # handled by pibling case
                            break
                    else:  # sim_xx and sim_yy are first cousins, but have no parents who are siblings
                        for sim_xz in x_ancestors[sim_xx]:  # x_ancestors[sim_xx] = [sim_xz,...], sim_xz = (n, sim) where sim_xx is n gens back from sim_x via sim
                            for sim_yz in y_ancestors[sim_yy]:  # y_ancestors[sim_yy] = [sim_yz,...], sim_yz = (n, sim) where sim_yy is n gens back from sim_x via sim
                                nx = sim_xz[0]
                                ny = sim_yz[0]
                                to_add = (sim_xx, sim_yy, nx + 2, ny + 2, 1)  # connections are cousins (sharing grandparents), so gen + 2. assume missing parents would be full sibs
                                if not to_add in xy_indirect_rels:
                                    xy_indirect_rels.append(to_add)

    return xy_indirect_rels # [(sim_z, sim_w, nx, ny, sib_strength)]
                                # where sim_z and sim_w are parents/sibs/relations to link, sim_z = sim_w if half-
    # sim_x and sim_y are connected nx and ny gens back respectively, via sim_z and sim_w

# input: two sims. output: None if there is no indirect relation, list if there is
def get_indirect_relation(sim_x: SimInfoParam, sim_y: SimInfoParam):
    return get_indirect_rel(sim_x, sim_y, get_ancestors(sim_x), get_ancestors(sim_y))

# input: two sims and the list of indirect rels. output: formatted version
# nb. expected list is the output from get_indirect_rel: [(sim_z, sim_w, nx, ny, sib_strength),...]
# the gender bit is for making in-law stuff easier
def format_indirect_rel_gender(xy_indirect_rels: List, sim_x: SimInfoParam, sim_y: SimInfoParam, gender: int):
    rels_via = []
    for boi in xy_indirect_rels:
        sim_z = boi[0]
        sim_w = boi[1]
        nx = boi[2]
        ny = boi[3]
        if nx <= 0 or ny <= 0: # filtering out any Problems
            continue
        sib_strength = boi[4]
        nth = min([nx, ny]) - 1 # nth cousin
        nce = nx - ny # n times removed
        rel_str = ''
        if sib_strength == 0.5:
            rel_str = 'half '
        if nth == 0: # pibling/sibling/nibling
            if abs(nce) > 1:
                if abs(nce) > 2:
                    rel_str += 'great'
                    if abs(nce) > 3:
                        rel_str += '(x' + str(abs(nce) - 2) + ')'
                    rel_str += '-'
                rel_str += 'grand'
            if nce < 0:
                if gender:
                    rel_str += 'aunt'
                else:
                    rel_str += 'uncle'
            elif nce == 0:
                if gender:
                    rel_str += 'sister'
                else:
                    rel_str += 'brother'
            elif nce > 0:
                if gender:
                    rel_str += 'niece'
                else:
                    rel_str += 'nephew'
        else: # cousin
            nce = abs(nce)
            if nth == 1:
                rel_str += 'first '
            elif nth == 2:
                rel_str += 'second '
            elif nth == 3:
                rel_str += 'third '
            else:
                rel_str += str(nth) + 'th '
            rel_str += 'cousin'
            if nce > 0:
                if nce == 1:
                    rel_str += ' once '
                elif nce == 2:
                    rel_str += ' twice '
                else:
                    rel_str += ' ' + str(nce) + ' times '
                rel_str += 'removed'
        rels_via.append((rel_str, sim_z, sim_w))
    return rels_via # [(str, sim_z, sim_w)]

# the above just using sim_x's gender
def format_indirect_rel(xy_indirect_rels: List, sim_x: SimInfoParam, sim_y: SimInfoParam):
    return format_indirect_rel_gender(xy_indirect_rels, sim_x, sim_y, sim_x.is_female)

# indirect relation as a console command
@sims4.commands.Command('riv_get_indirect_rel', command_type=sims4.commands.CommandType.Live)
def console_get_indirect_rel(sim_x: SimInfoParam, sim_y: SimInfoParam, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    rels_via = format_indirect_rel(get_indirect_relation(sim_x,sim_y), sim_x, sim_y)
    # we now have a list (relation, via this person)
    if sim_x is not None:
        if sim_y is not None:
            if rels_via:
                for rel_via in rels_via:
                    if rel_via[1] == rel_via[2]: # via one sim
                        output('{} {} is {} {}\'s {} (relation found via {} {})'.format(sim_x.first_name, sim_x.last_name, sim_y.first_name, sim_y.last_name, rel_via[0], rel_via[1].first_name, rel_via[1].last_name))
                    else:
                        sim_z = rel_via[1]
                        sim_w = rel_via[2] # via two sims
                        output('{} {} is {} {}\'s {} (relation found via {} {} and {} {})'.format(sim_x.first_name, sim_x.last_name, sim_y.first_name, sim_y.last_name, rel_via[0], sim_z.first_name, sim_z.last_name, sim_w.first_name, sim_w.last_name))
            else:
                output('no indirect rel found between {} and {}'.format(sim_x.first_name, sim_y.first_name))

# gets inlaw relations
# NOTE this can *only* be done with sims in the game
# if sim_x or sim_y are culled then we assume they have no spouse
# if not culled, we make sure it's using the sim and not the RivSim
def get_inlaw_rel(sim_x, sim_y, x_ancestors, y_ancestors):
    x_spouse = []
    y_spouse = []
    xy_inlaw_rels = []
    temp_rels = [] # has the list of in/direct rels of x/y's spouse
    manager = services.get_instance_manager(Types.RELATIONSHIP_BIT)
    spouse_relbit = manager.get(0x3DCE)
    # gets list of spouses for each of sim_x and sim_y
    try:
        # SPAGHETTI
        if riv_sim_list.sims: # if using RivSims
            if isinstance(sim_x, RivSim):
                x_culled = sim_x.is_culled
            else: # sim_x is a sim
                x_culled = False
            if isinstance(sim_y, RivSim):
                y_culled = sim_y.is_culled
            else: # sim_y is a sim
                y_culled = False
            if not x_culled: # uses actual sim for spouse if needed and doable
                ssim_x = services.sim_info_manager().get(int(sim_x.sim_id)).sim_info
            if not y_culled: # uses actual sim for spouse if needed and doable
                ssim_y = services.sim_info_manager().get(int(sim_y.sim_id)).sim_info
        else: # these will defo be non-culled sims
            x_culled = False
            y_culled = False
            ssim_x = sim_x
            ssim_y = sim_y

        # we now have sims in game where possible, and whether the sim has been culled
        # if the sim is culled then we just assume they have no spouse

        for sim_z in services.sim_info_manager().get_all():
            if not x_culled: # sim_x is still in the game, and ssim_x has its sim info
                if ssim_x.relationship_tracker.has_bit(sim_z.sim_id, spouse_relbit):
                    x_spouse.append(sim_z)
            if not y_culled: # sim_y is still in the game, and ssim_y has its sim info
                if ssim_y.relationship_tracker.has_bit(sim_z.sim_id, spouse_relbit):
                    y_spouse.append(sim_z)
    except:
        xy_inlaw_rels.append((-1, 'error in getting spouse lists'))
    # check if sim_x is married to sim_y
    try:
        if sim_x in y_spouse:
            if sim_y in x_spouse: # just checks nothing is weird
                xy_inlaw_rels.append((0,)) # the comma is needed to make this a tuple
    except:
        xy_inlaw_rels.append((-1, 'error in checking if sims are married'))

    # http://www.genetic-genealogy.co.uk/supp/NonGenetictRelationships.html
    # check if sim_x is related to sim_y's spouse
    try:
        # x is related to y's spouse (type a on site above)
        for sim_s in y_spouse:
            s_ancestors = get_ancestors(sim_s)
            # direct rel is a list of integers with generational difference
            temp_rels = get_direct_rel(sim_x, sim_s, x_ancestors, s_ancestors)
            if temp_rels:
                for rel in temp_rels:
                    if rel < 0: # if x is y's spouse's ancestor (e.g. mother-in-law)
                        xy_inlaw_rels.append((1, rel, sim_x, sim_s))
                temp_rels = []
            # indirect rel is a list of (sim_z, sim_w, nx, ny, sib_strength)
            temp_rels = get_indirect_rel(sim_x, sim_s, x_ancestors, s_ancestors)
            if temp_rels:
                for rel in temp_rels:
                    xy_inlaw_rels.append((2, rel, sim_x, sim_s))
                temp_rels = []
    except:
        xy_inlaw_rels.append((-1,'error in checking if sim_x is related to sim_y\'s spouse'))
    # check if sim_y is related to sim_x's spouse
    try:
        # x is the spouse of y's relative / y is related to x's spouse (type b on site above)
        for sim_s in x_spouse:
            s_ancestors = get_ancestors(sim_s)
            # direct rel is a list of integers with generational difference
            temp_rels = get_direct_rel(sim_s, sim_y, s_ancestors, y_ancestors)
            if temp_rels:
                for rel in temp_rels:
                    if rel > 0: # if x is the spouse of y's descendant (e.g. son-in-law)
                        xy_inlaw_rels.append((1, rel, sim_y, sim_s))
                temp_rels = []
            # indirect rel is a list of (sim_z, sim_w, nx, ny, sib_strength)
            temp_rels = get_indirect_rel(sim_s, sim_y, s_ancestors, y_ancestors)
            if temp_rels:
                for rel in temp_rels:
                    xy_inlaw_rels.append((2, rel, sim_y, sim_s))
                temp_rels = []
    except:
        xy_inlaw_rels.append((-1,'error in checking if sim_y is related to sim_x\'s spouse'))
    return xy_inlaw_rels
    # list [(0), (1, drel, sim_t, sim_s), (2, irel, sim_t, sim_s)] where
        # sim_s is the spouse of sim_t = sim_x or sim_y
        # drel = n describing the direct-in-law relationship between sim_x and sim_y
        # irel = (sim_z, sim_w, nx, ny, sib_strength) describing the indirect-in-law relationship

def get_inlaw_relation(sim_x: SimInfoParam, sim_y: SimInfoParam):
    return get_inlaw_rel(sim_x, sim_y, get_ancestors(sim_x), get_ancestors(sim_y))

def format_inlaw_rel(xy_inlaw_rels: List, sim_x: SimInfoParam, sim_y: SimInfoParam):
    inlaw_rels = [] # this will have the strings and via
    for rel in xy_inlaw_rels:
        try:
            if rel[0] == 0: # spouse
                try:
                    if sim_x.is_female:
                        inlaw_rels.append(('wife', 0))
                    else:
                        inlaw_rels.append(('husband', 0))
                except:
                    inlaw_rels.append(('error in adding/appending spouse relation', 1))
            elif rel[0] == 1: # direct-rel-in-law
                try:
                    for drel in format_direct_rel_gender([rel[1]], rel[2], rel[3], sim_x.is_female): # = [str,...]
                        try:
                            inlaw_rels.append((drel + ' in law', rel[3]))
                        except:
                            inlaw_rels.append(('error in appending direct-rel-in-law', 1))
                except:
                    inlaw_rels.append(('error in adding direct-rel-in-law', 1))
            elif rel[0] == 2: # indirect rel-in-law
                try:
                    for irel in format_indirect_rel_gender([rel[1]], rel[2], rel[3], sim_x.is_female): # = [(str, sim_z, sim_w),...]
                       try:
                            inlaw_rels.append((irel[0] + ' in law', rel[3]))
                       except:
                           inlaw_rels.append(('error in appending indirect-rel-in-law', 1))
                except:
                    inlaw_rels.append(('error in adding indirect-rel-in-law', 1))
            elif rel[0] == -1: # error
                inlaw_rels.append((rel[1], 1))
        except:
            inlaw_rels.append(('error in formatting inlaw rels', 1))
    return inlaw_rels # [(string, sim)] where sim is the spouse related to sim_x or sim_y, or is 0 if spouse

def get_pairs_yield(a: List, b: List):
    for x in a:
        for y in b:
            yield x, y

def get_pairs_return(a: List, b: List):
    ab = []
    for x in a:
        for y in b:
            ab.append((x,y))
    return ab

### riv_rel interactions below

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

riv_rel_int_24508_SnippetId = 24508
riv_rel_int_24508_MixerId = (17552881007513514036,)
@inject_to(InstanceManager, 'load_data_into_class_instances')
def riv_rel_int_AddMixer_24508(original, self):
    original(self)
    if self.TYPE == Types.SNIPPET:
        key = sims4.resources.get_resource_key(riv_rel_int_24508_SnippetId, Types.SNIPPET)
        snippet_tuning = self._tuned_classes.get(key)
        if snippet_tuning is None:
            return
        for m_id in riv_rel_int_24508_MixerId:
            affordance_manager = services.affordance_manager()
            key = sims4.resources.get_resource_key(m_id, Types.INTERACTION)
            mixer_tuning = affordance_manager.get(key)
            if mixer_tuning is None:
                return
            if mixer_tuning in snippet_tuning.value:
                return
            snippet_tuning.value = snippet_tuning.value + (mixer_tuning, )

riv_rel_int_163702_SnippetId = 163702
riv_rel_int_163702_MixerId = (17552881007513514036,)
@inject_to(InstanceManager, 'load_data_into_class_instances')
def riv_rel_int_AddMixer_163702(original, self):
    original(self)
    if self.TYPE == Types.SNIPPET:
        key = sims4.resources.get_resource_key(riv_rel_int_163702_SnippetId, Types.SNIPPET)
        snippet_tuning = self._tuned_classes.get(key)
        if snippet_tuning is None:
            return
        for m_id in riv_rel_int_163702_MixerId:
            affordance_manager = services.affordance_manager()
            key = sims4.resources.get_resource_key(m_id, Types.INTERACTION)
            mixer_tuning = affordance_manager.get(key)
            if mixer_tuning is None:
                return
            if mixer_tuning in snippet_tuning.value:
                return
            snippet_tuning.value = snippet_tuning.value + (mixer_tuning, )

# attempt for notification:
def scumbumbo_show_notification(sim_x: SimInfoParam, sim_y: SimInfoParam, text: str): #, title=None):
    # We need the client to get the active sim for the icon
    client = services.client_manager().get_first_client()
    localized_title = lambda **_: LocalizationHelperTuning.get_raw_text(sim_x.first_name + ' to ' + sim_y.first_name)
    #localized_text = lambda **_: _create_localized_string(0x054DDA26, text) this is {0.String}
    localized_text = lambda **_: LocalizationHelperTuning.get_raw_text(text)

    # For the primary icon we'll use the Sim's icon (a sim_info, or just the active_sim)
    primary_icon = lambda _: IconInfoData(obj_instance=sim_x) # IF THIS BREAKS go back to client.active_sim

    # For a secondary (not normally used) icon
    # First we need to get a resource key setup for the UI to find it, then we can create the IconInfoData from that
    # using an icon_resource argument.
    sprout_plant_icon_key = get_resource_key(0x9993999E26D6CB56, Types.PNG)
    secondary_icon = lambda _: IconInfoData(icon_resource=sprout_plant_icon_key)

    # ===================
    # == Visual Styles ==
    # ===================
    #   Green for defaults (urgency=DEFAULT, information_level=PLAYER, visual_type=INFORMATION)
    #   Orange for urgency = URGENT
    #   Blue for information_level = SIM
    #   Purple for visual_type = SPECIAL_MOMENT & information_level = SIM
    #   Dark "chat bubble" from Sim's icon information_level = SPEECH
    urgency = UiDialogNotification.UiDialogNotificationUrgency.DEFAULT
    information_level = UiDialogNotification.UiDialogNotificationLevel.PLAYER
    visual_type = UiDialogNotification.UiDialogNotificationVisualType.INFORMATION

    # =============
    # == FINALLY ==
    # =============
    # Prepare and show the notification.  The TunableFactory() is basically allowing us to fill in the
    # blanks that normally would have been specified in a UiDialogNotification XML tuning.
    # had client.active_sim at the start??
    notification = UiDialogNotification.TunableFactory().default(client.active_sim, text=localized_text, title=localized_title, icon=primary_icon, secondary_icon=secondary_icon, urgency=urgency, information_level=information_level, visual_type=visual_type)
    notification.show_dialog()

# input: two sims and their ancestors; output: a tuple of lists with bio rels first, non-bio rels second.
# these lists have ONLY the strings and not the via part
def get_str_list(sim_x, sim_y, x_ancestors, y_ancestors):
    bio_rels = []
    non_bio_rels = []

    # makes list of relations
    direct_rels = get_direct_rel(sim_x, sim_y, x_ancestors, y_ancestors)
    for rel in format_direct_rel(direct_rels, sim_x, sim_y):
        try:
            bio_rels.append(rel)
        except:
            bio_rels.append('[direct rel error]')
    indirect_rels = get_indirect_rel(sim_x, sim_y, x_ancestors, y_ancestors)
    for rel in format_indirect_rel(indirect_rels, sim_x, sim_y):
        try:
            bio_rels.append(rel[0])
        except:
            bio_rels.append('[indirect rel error]')
    inlaw_rels = get_inlaw_rel(sim_x, sim_y, x_ancestors, y_ancestors)
    for rel in format_inlaw_rel(inlaw_rels, sim_x, sim_y):
        try:
            non_bio_rels.append(rel[0])
        except:
            bio_rels.append('[inlaw rel error]')
    return (bio_rels, non_bio_rels)

# outputs a string with the prefix for relation multiplicity and a space after if it is a word
# show_single = 0 if you want 1 -> '', instead of 1 -> 'single'
def num_to_tuple(n: int, show_single: int):
    # https://cosmosdawn.net/forum/threads/if-1-single-2-double-n-tuple-n-tuples.2735/
    # n : tuple with n
    leq_ten_tuple = {1: 'single', 2: 'double', 3: 'triple',
               4: 'quadruple', 5: 'quintuple', 6: 'sextuple',
               7: 'septuple', 8: 'octuple', 9: 'nonuple'}
    # n : tuple with 10*n
    tens_tuple = {1: 'decuple', 2: 'viguple', 3: 'triguple', 4: 'quadraguple', 5: 'quinquaguple',
                  6: 'sexaguple', 7: 'septuaguple', 8: 'octoguple', 9: 'nonaguple', 10: 'centuple'}
    # n : prefix to tuple > 10
    prefix_tuple = {0: '', 1: 'un', 2: 'duo', 3: 'tre', 4: 'quattuor',
                    5: 'quin', 6: 'sex', 7: 'septen', 8: 'octo', 9: 'novem'}
    if n < 1:
        return 'not '
    elif n == 1 and show_single == 0: # doesn't show single when redundant
        return ''
    elif n < 10:
        return leq_ten_tuple[n] + ' '
    elif n <= 100:
        ones_bit = n % 10
        tens_bit = int((n - (n % 10))/10)
        # i.e. if n = ab (these are digits), ones_bit = b, tens_bit = a
        return prefix_tuple[ones_bit] + tens_tuple[tens_bit] + ' '
    else:
        return str(n) + '-tuple '

# input: lists of bio_rels and non_bio_rels as strings with repeats for multiplicity
# output: lists of bio_rels_fixed and non_bio_rels_fixed with multiplicity in strings
def combine_str_list(bio_rels: List, non_bio_rels: List):
    br_count_dict = {}
    nbr_count_dict = {}
    # counts the number of times each string shows up
    for rel in bio_rels:
        try:
            br_count_dict[rel] += 1 # adds 1 to multiplicity
        except:
            br_count_dict[rel] = 1
    # br_count_dict now has {rel: n} where n is the number of times rel shows up
    # do the same for nbr_count_dict
    for rel in non_bio_rels:
        try:
            nbr_count_dict[rel] += 1 # adds 1 to multiplicity
        except:
            nbr_count_dict[rel] = 1 # sets multiplicity to 1
    # nbr_count_dict now has {rel: n} where n is the number of times rel shows up

    bio_rels_fixed = []
    non_bio_rels_fixed = []
    # turns this into a list of strings
    for rel in br_count_dict.keys(): # key is the main part of the rel
        prefix = num_to_tuple(br_count_dict[rel], 0) # prefix is the 'n-tuple' bit
        bio_rels_fixed.append(prefix + rel)
    # turns this into a list of strings
    for rel in nbr_count_dict.keys(): # key is the main part of the rel
        prefix = num_to_tuple(nbr_count_dict[rel], 0) # prefix is the 'n-tuple' bit
        non_bio_rels_fixed.append(prefix + rel)
    return (bio_rels_fixed, non_bio_rels_fixed)

# input: type of string needed for the part of the notification right before "i'm your...". ends with a space
# output: string
def give_me_a_string(string_type):
    # string_types:
    # 0 = 00 = no rels
    # 1 = 01 = non bio (inlaw) only
    # 2 = 10 = bio only
    # 3 = 11 = bio and non bio
    strings_dict = {
        0: ['Nope, we aren\'t related.',
            'We aren\'t related at all.',
            'What gave you that idea? I\'m not related to you.'],
        1: ['I\'d hope we aren\'t related.',
            'We aren\'t related.',
            'We don\'t have any biological relation.'],
        2: ['Yeah, we\'re related.',
            'Of course we\'re related.'],
        3: ['Uh... we are related.',
            'Might as well start singing Sweet Home Appaloosa...',
            'This is a bit awkward.']
    }
    string_list = strings_dict[string_type]
    string_output = random.choice(string_list)
    # amend these if there are strong friendship/romantic relations
    return string_output + ' '

@sims4.commands.Command('riv_get_notif', command_type=sims4.commands.CommandType.Live)
def riv_get_notif(x_id: int, y_id: int, _connection=None):
    # sim_x = TargetSim/Object
    # sim_y = Actor
    # tried:
    # services.object_manager().get(x_id) # <- object_sim has no attribute is_female
    # services.object_manager().get(x_id).sim_info # appears to work
    # sim_x = services.sim_info_manager()._objects.get(x_id) # appears to work
    # services.sim_info_manager().get(x_id) # appears to work

    # gets sims and initialises empty lists
    sim_x = services.sim_info_manager().get(x_id).sim_info
    sim_y = services.sim_info_manager().get(y_id).sim_info
    notif_text = ''
    try:
        x_ancestors = get_ancestors(sim_x)
        y_ancestors = get_ancestors(sim_y)
    except:
        scumbumbo_show_notification(sim_x, sim_y, '[failed to get ancestors]')
        return

    # gets lists of strings for bio_rels and non_bio_rels
    rel_lists = get_str_list(sim_x, sim_y, x_ancestors, y_ancestors)
    bio_rels = rel_lists[0]
    non_bio_rels = rel_lists[1]

    # replaces these with strings that have multiplicity
    # (e.g. ['first cousin', 'first cousin'] -> {'first cousin': 2} -> ['double first cousin']
    rel_lists = combine_str_list(bio_rels, non_bio_rels)
    bio_rels = rel_lists[0]
    non_bio_rels = rel_lists[1]
    # rel_code tells you if they are non/bio rels

    # formats the notification
    if bio_rels:
        if non_bio_rels:
            rel_code = 3
        else:
            rel_code = 2
        notif_text = give_me_a_string(rel_code)
        notif_text += 'I\'m your ' + bio_rels[0]
        if len(bio_rels) == 2:  # a and b
            notif_text += ' and ' + bio_rels[1]
        elif len(bio_rels) > 2:  # a, b, c, and d
            for i in range(1, len(bio_rels) - 1):
                notif_text += ', ' + bio_rels[i]
            notif_text += ', and ' + bio_rels[len(bio_rels) - 1]
        notif_text += '. '
        if non_bio_rels:
            notif_text += 'I\'m also your ' + non_bio_rels[0]
            if len(non_bio_rels) == 2:  # a and b
                notif_text += ' and ' + non_bio_rels[1]
            elif len(non_bio_rels) > 2:  # a, b, c, and d
                for i in range(1, len(non_bio_rels) - 1):
                    notif_text += ', ' + non_bio_rels[i]
                notif_text += ', and ' + non_bio_rels[len(non_bio_rels) - 1]
            notif_text += '. '
    else:
        if non_bio_rels:
            rel_code = 1
            notif_text = give_me_a_string(rel_code)
            notif_text += 'I\'m your ' + non_bio_rels[0]
            if len(non_bio_rels) == 2:  # a and b
                notif_text += ' and ' + non_bio_rels[1]
            elif len(non_bio_rels) > 2:  # a, b, c, and d
                for i in range(1, len(non_bio_rels) - 1):
                    notif_text += ', ' + non_bio_rels[i]
                notif_text += ', and ' + non_bio_rels[len(non_bio_rels) - 1]
            notif_text += '. '
        else:
            rel_code = 0
            notif_text = give_me_a_string(rel_code)

    try:
        ### extra starting/ending strings
        manager = services.get_instance_manager(Types.RELATIONSHIP_BIT)
        if sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x3DB4)): # friendship-despised
            if rel_code == 0:
                notif_text = 'I\'m so glad we aren\'t related.'
                scumbumbo_show_notification(sim_x, sim_y, notif_text)
                return # bc we don't need to do anything else here
            else:
                notif_text = notif_text + ' Doesn\'t mean I want anything to do with you.'
        if sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x79EB)): # friendship-bff_BromanticPartner
            notif_text = 'Bro... ' + notif_text
        if sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x18961)): # relbit_Pregnancy_Birthparent
            notif_text = 'What? I gave birth to you! ' + notif_text
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x34CCE)):  # relationshipBit_Clone [RoM]
            notif_text = 'You managed to learn the Duplicato spell but you can\'t even recognise your own clone?'
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x1ABED)):  # relationshipBit_IsClone [GTW]
            notif_text = 'You managed to get your hands on a cloning machine but you can\'t recognise your own clone?'
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x3DDF)): # RomanticCombo_Soulmates
            if rel_code < 2: # not related
                notif_text = 'You\'re my soulmate! ' + notif_text
            elif rel_code < 4: # related, futureproofed for codes \geq 4
                notif_text = notif_text + ' I can\'t help being deeply in love with you, though.' # i mean, EW
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x18465)): # romantic-Promised = engaged teens
            notif_text = 'I\'ve already promised myself to you, so it\'s a bit late to ask... ' + notif_text
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x3DC8)): # romantic-Engaged
            notif_text = notif_text + ' ...we\'re still on for the wedding, right?'
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x3DCE)): # romantic-Married
            notif_text = 'Ah yes, the right time to double check is after we get married. ' + notif_text
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x17B82)): # romantic-HaveDoneWooHoo_Recently
            notif_text = 'We JUST woohooed! ' + notif_text
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x873B)): # romantic-HaveDoneWooHoo
            notif_text = 'We\'ve woohooed, and now you\'re asking? ' + notif_text
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x27A6)): # ShortTerm_RecentFirstKiss
            notif_text = 'We literally just had our first kiss. ' + notif_text
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x27A6)): # had first kiss
            notif_text = 'Maybe you should\'ve asked before we kissed? ' + notif_text
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x1F064)):  # romantic-ExchangedNumbers
            notif_text = 'Checking to see if you should keep my number? ' + notif_text
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x3DD9)):  # RomanticCombo_ItsAwkward
            notif_text = 'Things are already weird. ' + notif_text
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x3DDA)):  # RomanticCombo_ItsComplicated
            notif_text = 'This relationship is already complicated. ' + notif_text
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x3DDB)):  # RomanticCombo_ItsVeryAwkward
            notif_text = 'Everything\'s already really weird... ' + notif_text
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x3DDC)):  # RomanticCombo_ItsVeryComplicated
            notif_text = 'This relationship is already SUPER complicated! ' + notif_text
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x181C4)): #HaveBeenRomantic
            notif_text = 'We\'ve already been flirting... it\'s a little late to ask. ' + notif_text
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x1A36D)): # relationshipbit_CoWorkers
            notif_text = 'We work together. ' + notif_text
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x3DB0)): # friendship-acquaintances
            notif_text = 'Oh, right, you barely know me. ' + notif_text
    except:
        pass

    scumbumbo_show_notification(sim_x, sim_y, notif_text)

### save/load/clean json

def load_sims(file_name_extra: str):
    file_dir = Path(__file__).resolve().parent.parent
    file_name = 'riv_rel_' + file_name_extra + '.json'  # e.g. riv_rel_pine.json
    file_path = os.path.join(file_dir, file_name)

    # https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
    with open(file_path, 'r') as json_file:
        sims = json.load(json_file)
    return sims # is this a list??

# sims_input is a list of sims as SimInfoParam, Dict, or RivSim (can be mixed in list)
# file_name_extra is a str that fits in the * in riv_rel_*.json
def save_sims(sims_input: List, file_name_extra: str): #List<RivSim>
    sim_time = services.time_service().sim_now.absolute_ticks()
    file_dir = Path(__file__).resolve().parent.parent
    file_name = 'riv_rel_' + file_name_extra + '.json'  # e.g. riv_rel_pine.json
    file_path = os.path.join(file_dir, file_name)
    sims = [] # for output; each sim is a Dict here!
        # game_sims if file does not exist
        # UPDATED file_sims + new_sims (subset of game_sims) if file does exist
    game_sims = [] # sims from the game as RivSims
    for sim in sims_input:
        if isinstance(sim, RivSim):
            game_sims.append(sim)
        else:
            game_sims.append(RivSim(sim))

    if os.path.isfile(file_path):  # update file
        json_sims = load_sims(file_name_extra) #! should use list in mem
        file_sims = [] # sims from the file as RivSims
        for sim in json_sims:
            file_sims.append(RivSim(sim))
        new_sims = [] # sims from the game that are NOT in the file

        # add in game sims (append if sim not in file, update if in file AND needs updating)
        for sim_g in game_sims:
            sim_in_file = False  # initialise
            for sim_f in file_sims:
                if sim_g.sim_id == sim_f.sim_id: # if sim is in file and in game
                    sim_in_file = True
                    if sim_g.first_name == sim_f.first_name and sim_g.last_name == sim_f.last_name and sim_g.is_female == sim_f.is_female: # all details are the same
                        pass # no updates needed
                    elif sim_f.time < sim_time:
                        sim_f.update_info(sim_g.first_name, sim_g.last_name, sim_g.is_female, sim_time) # updates sim in file
            if not sim_in_file: # sim_g is in game and not in file
                new_sims.append(sim_g)

        # update to show if sims are culled (sim in file and not in game)
        for sim_f in file_sims: # sim is in file
            sim_in_game = False
            for sim_g in game_sims:
                if sim_f.sim_id == sim_g.sim_id: # if sim is in file and in game
                    sim_in_game = True
                    break # don't need to continue checking against sims in the file
            if not sim_in_game: # if sim is in file and not in game
                if not sim_f.is_culled: # and if sim isn't registered as culled
                    sim_f.cull() # then register sim as culled
            sims.append(sim_f.to_dict()) # put each sim_f in the output WHETHER CULLED OR NOT

        for sim_n in new_sims: # for sim that is in game and not in file
            sims.append(sim_n.to_dict()) # add to sims (list for file)

    else: # new file
        # makes a list of sims as dict
        for sim_g in game_sims:
            sims.append(sim_g.to_dict())
        # https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/

    with open(file_path, 'w') as json_file:
        json.dump(sims, json_file)

def clean_sims(file_name_extra: str):
    # we want to remove duplicate sim IDs by taking the MOST RECENT version
    dict_sims = load_sims(file_name_extra)

    # get list of RivSims
    sims = []
    for sim in dict_sims:
        sims.append(RivSim(sim))

    # get list of sims to be removed
    to_remove = []
    for sim_x in sims:
        for sim_y in sims:
            if sim_x.sim_id == sim_y.sim_id: # same sim
                if sim_x.time < sim_y.time: # sim_x is earlier
                    if not sim_x in to_remove: # sim_x isn't already flagged to remove
                        to_remove.append(sim_x)

    # remove these sims
    for sim in to_remove:
        sims.remove(sim)

    # make back into dicts for json
    output_sims = []
    for sim in sims:
        output_sims.append(sim.to_dict())

    file_dir = Path(__file__).resolve().parent.parent
    file_name = 'riv_rel_' + file_name_extra + '.json'  # e.g. riv_rel_pine.json
    file_path = os.path.join(file_dir, file_name)

    # replace info in file with cleaned one
    with open(file_path, 'w') as json_file:
        json.dump(output_sims, json_file)

    # do we also want to remove sims with no parents from riv_relparents?

# loads in dict of rels
def load_rels(file_name_extra: str):
    file_dir = Path(__file__).resolve().parent.parent
    file_name = 'riv_relparents_' + file_name_extra + '.json'  # e.g. riv_rel_pine.json
    file_path = os.path.join(file_dir, file_name)

    # https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
    with open(file_path, 'r') as json_file:
        rels = json.load(json_file) # use json.load if this doesn't work
    return rels # should be a dict

# saves parent rels as a dict { sim_id : [parent1_id, parent2_id], ... }
    # does all new rels if new file
    # adds in new rels if updating file, taking the union of lists where possible
def save_rels(game_sims: List, file_name_extra: str): #List<RivSim>
    file_dir = Path(__file__).resolve().parent.parent
    file_name = 'riv_relparents_' + file_name_extra + '.json'  # e.g. riv_relparents_pine.json
    file_path = os.path.join(file_dir, file_name)
    rels = {} # for output
    new_rels = {} # contains rels from the game

    # makes a list of parent rels in the game
    manager = services.get_instance_manager(Types.RELATIONSHIP_BIT)
    parent_relbit = manager.get(0x2269)
    for sim_x in game_sims:
        # get list of parents
        parents = []
        for sim_y in game_sims:
            if sim_x.relationship_tracker.has_bit(int(sim_y.sim_id), parent_relbit):
                parents.append(sim_y)
        # get list of parent IDs
        parents_id = []
        for parent in parents:
            parents_id.append(parent.sim_id)
        # add to dict
        new_rels[str(sim_x.sim_id)] = parents_id

    if os.path.isfile(file_path): # update file
        json_rels = load_rels(file_name_extra) # dict where key is a sim ID, value is list of parent IDs
        for sim in list(set(new_rels.keys()) | set(json_rels.keys())):
                # add union of parent lists to new file. either gets list if exists, or uses empty list
                rels[sim] = list(set(json_rels.get(sim,[])) | set(new_rels.get(sim,[])))
    else: # new file
        rels = new_rels

    # https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
    with open(file_path, 'w') as json_file:
        json.dump(rels, json_file)

# saves sims
@sims4.commands.Command('riv_save', command_type=sims4.commands.CommandType.Live)
def console_save_sims(file_name_extra: str, _connection=None):
    output = sims4.commands.CheatOutput(_connection)

    sim_time = services.time_service().sim_now
    abs_tick = sim_time.absolute_ticks()
    output('the current sim time is ' + str(sim_time))
    output('[this number appears at the end of sims that are not culled and were added/updated this time] abs_tick = ' + str(abs_tick))

    save_sims(services.sim_info_manager().get_all(), file_name_extra)
    output('saved sims.') #add debug info later
    save_rels(services.sim_info_manager().get_all(), file_name_extra)
    output('saved parent rels. \nto use these relations in riv_rel, type the following: riv_load ' + file_name_extra + '\n[riv_save: all done]') #add debug info later
    #output('added details from ' + str(len(sims)) + ' sims to file ' + 'riv_rel_' + file_name_extra + '.json')

# loads sims from file, or from mem if nothing is entered
@sims4.commands.Command('riv_load', command_type=sims4.commands.CommandType.Live)
def console_load_sims(file_name_extra: str, _connection=None):
    output = sims4.commands.CheatOutput(_connection)

    try:
        riv_sim_list.load_sims(file_name_extra)
        riv_rel_dict.load_rels(file_name_extra)
        # sims = load_sims(file_name_extra)
        output('loaded in parent rels and ' + str(len(riv_sim_list.sims)) + ' sim mini-infos. \nshowing a random sim and their parents:')
        # gets random sim and outputs them
        randsim = random.choice(riv_sim_list.sims)
        output(str(randsim.to_dict()))
        # gets their parent list
        randparents = riv_rel_dict.rels.get(randsim.sim_id, [])
        output(str(randparents))
        # gets parent names
        for parent in randparents:
            for sim in riv_sim_list.sims:
                if str(parent) == sim.sim_id:
                    output(sim.first_name + ' ' + sim.last_name)
                    break
    except:
        output('something went wrong while loading these sims and rels; please check that these files exist in the same folder as riv_rel.ts4script:')
        output('riv_rel_' + file_name_extra + '.json and riv_relparents_' + file_name_extra + '.json')
        output('if these files do exist then please let me (rivforthesesh / riv#4381) know; if you are able to provide your current save and/or the .json files, that would be helpful for finding the issue')

    output('[riv_load: all done]')

# shows which RivSims are in mem
@sims4.commands.Command('riv_mem', command_type=sims4.commands.CommandType.Live)
def console_mem_sims(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    sims = riv_sim_list.sims
    output('currently there are ' + str(len(sims)) + ' sim mini-infos in memory.')
    if sims:
        output('showing a random sim:')
        randsim = random.choice(sims)
        output(str(randsim))
        output(str(randsim.to_dict()))
    else:
        output('use riv_load xyz to load in sim info from riv_rel_xyz.json and riv_relparents_xyz.json')
    output('[riv_mem: all done]')

# cleans riv_rel_pine.json
@sims4.commands.Command('riv_clean', command_type=sims4.commands.CommandType.Live)
def console_clean_sims(file_name_extra: str, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    sims = load_sims(file_name_extra)
    old_n = len(sims)
    output('this file contains ' + str(old_n) + ' sim mini-infos. cleaning...')
    clean_sims(file_name_extra)
    sims = load_sims(file_name_extra)
    new_n = len(sims)
    output('after removing duplicates, this file contains ' + str(new_n) + ' sim mini-infos.')
    if old_n < new_n:
        output('if you\'re currently using this file, please run riv_update ' + file_name_extra)
    output('[riv_clean: all done]')

# clears sims and rels from mem
@sims4.commands.Command('riv_clear', command_type=sims4.commands.CommandType.Live)
def console_clear_sims(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    riv_sim_list.clear_sims()
    riv_rel_dict.clear_rels()
    output('[riv_clear: all done]')

# updates json files
@sims4.commands.Command('riv_update', command_type=sims4.commands.CommandType.Live)
def console_update_sims(file_name_extra: str, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    output('running save, clear, then load (updates sim/rel info in mem and .json file)...')
    console_save_sims(file_name_extra, _connection)
    console_clear_sims(_connection)
    console_load_sims(file_name_extra, _connection)
    output('[riv_update: all done]')

### SETTING FOUNDERS AND GROWING FAMILIES

try:
    founder_trait = services.get_instance_manager(Types.TRAIT).get(riv_reltraits_foundertrait.id)
except:
    founder_trait = None

# 0xABE35E7B8FA16459 GIVES NONE ^^^
# riv_reltraits_foundertrait.trait_id doesn't work either
# name is riv_reltraits_foundertrait
# change here if founder trait code changes; scope just makes sure this is in one place
# also add famA ... famH traits

# adds founder trait to sim named
# https://modthesims.info/t/603511
@sims4.commands.Command('riv_add_founder', command_type=sims4.commands.CommandType.Live)
def riv_addfounder(sim_x: SimInfoParam, _connection=None):
    output = sims4.commands.CheatOutput(_connection)

    if not founder_trait == None:
        # Check if our sim already has that trait
        if sim_x.has_trait(founder_trait):
            output(sim_x.first_name + ' is already the founder of a legacy.')
        else:
            # The sim doesn't have that trait, so add it
            sim_x.add_trait(founder_trait) # remove_trait removes it
            output(sim_x.first_name + ' is now the founder of a legacy. Set the family in the Actions menu or via the cheat command [INSERT CHEAT]')
            output('For everything to work properly, please make sure ' + sim_x.first_name + ' does NOT get culled (either by strengthening connection to the physical world on their grave or adding the never cull flag with MCCC).')
    else:
        output('Founder trait not found. (I haven\'t done this bit yet!)')

# removes founder trait from sim named
# https://modthesims.info/t/603511
@sims4.commands.Command('riv_remove_founder', command_type=sims4.commands.CommandType.Live)
def riv_removefounder(sim_x: SimInfoParam, _connection=None):
    output = sims4.commands.CheatOutput(_connection)

    if not founder_trait == None:
        if sim_x.has_trait(founder_trait):
            sim_x.remove_trait(founder_trait)
            output('removed founder trait from ' + sim_x.first_name)
        else:
            output(sim_x.first_name + ' is not a founder.')
    else:
        output('Founder trait not found. (I haven\'t done this bit yet!)')

# lists founders
@sims4.commands.Command('riv_founders', command_type=sims4.commands.CommandType.Live)
def riv_listfounders(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    founders = []

    if not founder_trait == None:
        output('to see if this works: ' + str(founder_trait))
        # find sims with the founder trait
        for sim_x in services.sim_info_manager().get_all():
            if sim_x.has_trait(founder_trait):
                founders.append(sim_x)
                output(sim_x.first_name + ' is the founder of a legacy.')
        if founders:
            output('founders in this save: ' + len(founders))
        else:
            output('there are no founders in this save.')
    else:
        output('Founder trait not found. (I haven\'t done this bit yet!)')

### RIV_REL (and riv_rel_rand, riv_rel_all, riv_help)

# gets direct, indirect, inlaw rel as a console command
@sims4.commands.Command('riv_rel', command_type=sims4.commands.CommandType.Live)
def riv_getrelation(sim_x: SimInfoParam, sim_y: SimInfoParam, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    found_rel = 0
    found_bio = 0
    if sim_x is not None:
        if sim_y is not None:
            if sim_x == sim_y:
                output('{} {} is {} {}'.format(sim_x.first_name, sim_x.last_name, sim_y.first_name, sim_y.last_name))
                found_rel += 1
                found_bio += 1
            else:
                x_ancestors = get_ancestors(sim_x)
                y_ancestors = get_ancestors(sim_y)

                # A L L
                # gets lists of strings for bio_rels and non_bio_rels
                rrel_lists = get_str_list(sim_x, sim_y, x_ancestors, y_ancestors)
                # replaces these with strings that have multiplicity
                # (e.g. ['first cousin', 'first cousin'] -> {'first cousin': 2} -> ['double first cousin']
                rel_lists = combine_str_list(rrel_lists[0], rrel_lists[1])
                rel_list = rel_lists[0] + rel_lists[1]
                # and then this list gets formatted
                if len(rel_list) > 0:
                    main_text = sim_x.first_name + ' is ' + sim_y.first_name + '\'s ' + rel_list[0]
                    if len(rel_list) == 2:  # a and b
                        main_text += ' and ' + rel_list[1]
                    elif len(rel_list) > 2:  # a, b, c, and d
                        for i in range(1, len(rel_list) - 1):
                            main_text += ', ' + rel_list[i]
                        main_text += ', and ' + rel_list[len(rel_list) - 1]
                else:
                    main_text = sim_x.first_name + ' and ' + sim_y.first_name + ' are not related'
                main_text += '. \nMore info:'
                output(main_text)

                # D I R E C T
                xy_direct_rel = get_direct_rel(sim_x, sim_y, x_ancestors, y_ancestors)
                if xy_direct_rel:  # there is a direct relation, list is not empty
                    xy_direct_rel_str = format_direct_rel(xy_direct_rel, sim_x, sim_y)
                    for xy_rel in xy_direct_rel_str:
                        try:
                            output('{} {} is {} {}\'s {}'.format(sim_x.first_name, sim_x.last_name, sim_y.first_name, sim_y.last_name, xy_rel))
                        except:
                            output('error in riv_rel, direct rel section')
                        found_rel += 1
                        found_bio += 1

                # I N D I R E C T
                xy_indirect_rel = get_indirect_rel(sim_x, sim_y, x_ancestors, y_ancestors)
                rels_via = format_indirect_rel(xy_indirect_rel, sim_x, sim_y)
                # we now have a list (relation, via this person)
                if rels_via:
                    for rel_via in rels_via:
                        try:
                            if rel_via[1] == rel_via[2]:  # via one sim
                                output('{} {} is {} {}\'s {} (relation found via {} {})'.format(sim_x.first_name, sim_x.last_name,sim_y.first_name,sim_y.last_name,rel_via[0],rel_via[1].first_name, rel_via[1].last_name))
                            else:
                                sim_z = rel_via[1]
                                sim_w = rel_via[2]  # via two sims
                                output( '{} {} is {} {}\'s {} (relation found via {} {} and {} {})'.format(sim_x.first_name, sim_x.last_name, sim_y.first_name, sim_y.last_name, rel_via[0], sim_z.first_name, sim_z.last_name, sim_w.first_name, sim_w.last_name))
                        except:
                            output('error in riv_rel, indirect rel section')
                        found_rel += 1
                        found_bio += 1

                # I N L A W
                xy_inlaw_rels = get_inlaw_rel(sim_x, sim_y, x_ancestors, y_ancestors)
                if xy_inlaw_rels:
                    # output(str(xy_inlaw_rels))
                    inlaw_str = format_inlaw_rel(xy_inlaw_rels, sim_x, sim_y)
                    for rel in inlaw_str:
                        try:
                            if rel[1] == 0:  # spouse
                                output('{} {} is {} {}\'s {}'.format(sim_x.first_name, sim_x.last_name, sim_y.first_name, sim_y.last_name, rel[0]))
                            elif rel[1] == 1:  # error
                                output(rel[0])
                            else:  # rel = (string, sim)
                                output('{} {} is {} {}\'s {} (relation found via {} {})'.format(sim_x.first_name, sim_x.last_name, sim_y.first_name, sim_y.last_name, rel[0], rel[1].first_name, rel[1].last_name))
                        except:
                            output('error in riv_rel, inlaw section')
                        found_rel += 1

    output('biological relations found: ' + str(found_bio))
    output('total relations found: ' + str(found_rel))

# checks against random sim
@sims4.commands.Command('riv_rel_rand', command_type=sims4.commands.CommandType.Live)
def riv_getrandomrel(sim_x: SimInfoParam, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    sim_y = random.choice(list(services.sim_info_manager()._objects.values()))
    output('relation with: {} {}'.format(sim_y.first_name, sim_y.last_name))
    riv_getrelation(sim_x, sim_y, _connection)

# checks against all sims in the game
@sims4.commands.Command('riv_rel_all', command_type=sims4.commands.CommandType.Live)
def riv_getallrels(sim_x: SimInfoParam, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    x_ancestors = get_ancestors(sim_x)
    relatives_found = 0
    for sim_y in services.sim_info_manager().get_all():
        if not sim_y == sim_x:
            rel_list = []
            y_ancestors = get_ancestors(sim_y)
            try:
                for rel in format_direct_rel(get_direct_rel(sim_x, sim_y, x_ancestors, y_ancestors), sim_x, sim_y):
                    rel_list.append(rel)
            except:
                rel_list.append('direct rel error')
            try:
                for rel in format_indirect_rel(get_indirect_rel(sim_x, sim_y, x_ancestors, y_ancestors), sim_x, sim_y):
                    rel_list.append(rel[0])
            except:
                rel_list.append('indirect rel error')
            try:
                for rel in format_inlaw_rel(get_inlaw_rel(sim_x, sim_y, x_ancestors, y_ancestors), sim_x, sim_y):
                    rel_list.append(rel[0])
            except:
                rel_list.append('inlaw error')
            if rel_list:
                output('{} {}: {}'.format(sim_y.first_name, sim_y.last_name, str(rel_list)))
                relatives_found += 1
    output('number of relatives found for ' + sim_x.first_name + ': ' + str(relatives_found))

# help
@sims4.commands.Command('riv_help', command_type=sims4.commands.CommandType.Live)
def console_help(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    # gen 2 (4 nov fix) for public ver, gen 3 (thank you for the support!) for early access ver
    output('riv_rel gen 3 early access (tysm for the support!) - biological and in-law relations, console commands, interaction, .json files')
    output('sims can be typed as firstname lastname (use "" if there is a space in the first/last name, e.g. J "Huntington III") or as the sim ID')
    output('if you find an error but you typed the names correctly, please send me (rivforthesesh / riv#4381) the error text and any relevant rels/files!')
    output('commands taking two sims: riv_rel, riv_get_sib_strength, riv_get_direct_rel, riv_get_indirect_rel, riv_show_relbits')
    output('commands taking one sim: riv_get_parents, riv_get_ancestors, riv_rel_all, riv_rel_rand')
    output('using .json files [replace xyz by whatever you want to create/use the files riv_rel_xyz.json and riv_relparents_xyz.json]:')
    output('riv_save xyz (save sim info to .json files), riv_load xyz (load sim info from .json files), riv_clean xyz (removes duplicates from .json file), riv_mem (shows no. mini sim-infos in memory), riv_clear (clears memory), riv_update xyz (runs save, clear, then load)')

# situation job?? for displaying relation on mouse-over

# rel bits (TARGET [TargetSim] is the XYZ of RECIPIENT [Actor])

# DIRECT
# 0x2268	RelationshipBit	family_grandparent
# 0x2269	RelationshipBit	family_parent
# 0x2265	RelationshipBit	family_son_daughter
# 0x2267	RelationshipBit	family_grandchild

# VIA SIBLINGS
# 0x2262	RelationshipBit	family_brother_sister
# 0x227A	RelationshipBit	family_cousin
# 0x227D	RelationshipBit	family_aunt_uncle
# 0x2705	RelationshipBit	family_niece_nephew

# BY MARRIAGE
# 0x2278	RelationshipBit	family_stepsibling
# 0x5FAA	RelationshipBit	family_husband_wife # doesn't seem to work??
# 0x3DCE    RelationshipBit romantic-Married

# BY LOCALITY
# 0x1261E	RelationshipBit	neighbor
# 0x1A36D	RelationshipBit	relationshipbit_CoWorkers

# CLONES
# 0x1ABED	RelationshipBit	relationshipBit_IsClone		[GTW]
# 0x34CCE	RelationshipBit	relationshipBit_Clone		[RoM]

###

# OTHER BIO
# 0x0000000000027875	RelationshipBit	familyRelationshipBitsAcquired_Grandparent_HighRel
# 0x0000000000027876	RelationshipBit	familyRelationshipBitsAcquired_Grandchild_HighRel
# 0x0000000000027877	RelationshipBit	familyRelationshipBitsAcquired_Grandparent_NeutralRel
# 0x0000000000027882	RelationshipBit	familyRelationshipBitsAcquired_Grandchild_NeutralRel
# 0x0000000000027883	RelationshipBit	familyRelationshipBitsAcquired_Grandparent_PoorRel
# 0x0000000000027884	RelationshipBit	familyRelationshipBitsAcquired_GrandChild_PoorRel
# 0x000000000002788A	RelationshipBit	familyRelationshipBitsAcquired_Sibling_HighRel_LowRival
# 0x000000000002788B	RelationshipBit	familyRelationshipBitsAcquired_Sibling_HighRel_HighRival
# 0x000000000002788C	RelationshipBit	familyRelationshipBitsAcquired_Sibling_NeutralRel_HighRival
# 0x000000000002788D	RelationshipBit	familyRelationshipBitsAcquired_Sibling_NeutralRel_LowRival
# 0x000000000002788E	RelationshipBit	familyRelationshipBitsAcquired_Sibling_PoorRel_HighRival
# 0x000000000002788F	RelationshipBit	familyRelationshipBitsAcquired_Sibling_PoorRel_LowRival
# 0x00000000000278B0	RelationshipBit	familyRelationshipBitsAcquired_Parent_HighRel_HighAuth
# 0x00000000000278B1	RelationshipBit	familyRelationshipBitsAcquired_Child_HighRel_HighAuth
# 0x00000000000278B2	RelationshipBit	familyRelationshipBitsAcquired_Parent_HighRel_LowAuth
# 0x00000000000278B3	RelationshipBit	familyRelationshipBitsAcquired_Child_HighRel_LowAuth
# 0x00000000000278B4	RelationshipBit	familyRelationshipBitsAcquired_Parent_MaxRel_HighAuth
# 0x00000000000278B5	RelationshipBit	familyRelationshipBitsAcquired_Child_MaxRel_HighAuth
# 0x00000000000278B6	RelationshipBit	familyRelationshipBitsAcquired_Parent_MaxRel_LowAuth
# 0x00000000000278B7	RelationshipBit	familyRelationshipBitsAcquired_Child_MaxRel_LowAuth
# 0x00000000000278B8	RelationshipBit	familyRelationshipBitsAcquired_Parent_NeutralRel_HighAuth
# 0x00000000000278B9	RelationshipBit	familyRelationshipBitsAcquired_Child_NeutralRel_HighAuth
# 0x00000000000278BA	RelationshipBit	familyRelationshipBitsAcquired_Parent_NeutralRel_LowAuth
# 0x00000000000278BB	RelationshipBit	familyRelationshipBitsAcquired_Child_NeutralRel_LowAuth
# 0x00000000000278BC	RelationshipBit	familyRelationshipBitsAcquired_Parent_PoorRel_HighAuth
# 0x00000000000278BD	RelationshipBit	familyRelationshipBitsAcquired_Child_PoorRel_HighAuth
# 0x00000000000278BE	RelationshipBit	familyRelationshipBitsAcquired_Parent_PoorRel_LowAuth
# 0x00000000000278BF	RelationshipBit	familyRelationshipBitsAcquired_Child_PoorRel_LowAuth

# FRIENDSHIP (positive)
# 0x3DB5	RelationshipBit	friendship-friend
# 0x3DB7	RelationshipBit	friendship-good_friends
# 0x3DB2	RelationshipBit	friendship-bff

# FRIENDSHIP (negative)
# 0x0000000000003DB9	RelationshipBit	friendship-nemesis
# 0x0000000000003DBA	RelationshipBit	friendship-disliked

# ROMANCE (negative)
# 0x3DC3	RelationshipBit	romantic-Broken_Up
# 0x3DC4	RelationshipBit	romantic-Broken_Up_Engaged
# 0x3DC6	RelationshipBit	romantic-Despised_Ex
# 0x3DC7	RelationshipBit	romantic-Divorced
# 0x3DC9	RelationshipBit	romantic-Frustrated_Ex
# 0x3DCB	RelationshipBit	romantic-GotColdFeet
# 0x3DCD	RelationshipBit	romantic-LeftAtTheAltar
# 0x99BC	RelationshipBit	romantic-LeaveAtTheAltar
# 0x3DD2	RelationshipBit	RomanticCombo_AwkwardFriends
# 0x3DD3	RelationshipBit	RomanticCombo_AwkwardLovers
# 0x3DD4	RelationshipBit	RomanticCombo_BadMatch
# 0x3DD6	RelationshipBit	RomanticCombo_EnemiesWithBenefits
# 0x3DE1	RelationshipBit	RomanticCombo_TerribleMatch
# 0x3DE2	RelationshipBit	RomanticCombo_TotalOpposites
# 0x3DE3	RelationshipBit	RomanticCombo_BadRomance
# 0x905D	RelationshipBit	romantic-HasBeenUnfaithful
# 0x9191	RelationshipBit	romantic_CheatedWith
# 0x17C34	RelationshipBit	ShortTerm_JustBrokeUpOrDivorced

# ROMANCE (positive)
# 0x3DCA	RelationshipBit	romantic-GettingMarried
# 0x3DD1	RelationshipBit	romantic-Significant_Other
# 0x3DD5	RelationshipBit	RomanticCombo_Lovebirds
# 0x3DDD	RelationshipBit	RomanticCombo_Lovers
# 0x3DDE	RelationshipBit	RomanticCombo_RomanticInterest
# 0x3DE0	RelationshipBit	RomanticCombo_Sweethearts
# 0x2DD3D	RelationshipBit	romance-Faithful

# ROMANCE (other)
# 0x18EC1	RelationshipBit	romantic-Widow
# 0x191FF	RelationshipBit	romantic-Widower
# 0x196E1	RelationshipBit	romantic_DeadSpouse

# MISC
# 0x27AB2	RelationshipBit	CT_notParent_CareGiver		[PH]
# 0x27AB3	RelationshipBit	CT_notParent_CareDependent	[PH]
# 0x1261E	RelationshipBit	neighbor
# 0x000000000000692B	RelationshipBit	relationshipBits_Mischief_PartnersInCrime
# 0x00000000000070EF	RelationshipBit	LoanRelationshipBits_Small
# 0x00000000000070F0	RelationshipBit	LoanRelationshipBits_Large

# ???
# 0x3DD7	RelationshipBit	RomanticCombo_Frenemies
# 0x3DD8	RelationshipBit	RomanticCombo_HotAndCold
# 0x0000000000003DB3	RelationshipBit	friendship-bff_Evil
# 0x0000000000003DB6	RelationshipBit	friendship-friend_Evil
# 0x0000000000003DB8	RelationshipBit	friendship-good_friends_Evil
# 0x0000000000003DC1	RelationshipBit	relationshipBits_Friendship_NeutralBit
# 0x0000000000003DC2	RelationshipBit	relationshipBits_Romance_NeutralBit
# 0x000000000000692A	RelationshipBit	relationshipBits_Mischief_NeutralBit
# 0x12F11	RelationshipBit	RomanticCombo_Acquaintances
# 0x0000000000012F41	RelationshipBit	RomanticCombo_JustFriends
# 0x0000000000012F42	RelationshipBit	RomanticCombo_JustGoodFriends
# 0x0000000000012F4F	RelationshipBit	RomanticCombo_Disliked
# 0x0000000000012F50	RelationshipBit	RomanticCombo_Despised
# 0x1F90F	RelationshipBit	HasBeenFriends

# in packs i don't have
# 0x0000000000035662	RelationshipBit	relationshipBit_Robot_Creation
# 0x0000000000035663	RelationshipBit	relationshipBit_Robot_Creator

# added to notifs
# 0x3DB0	RelationshipBit	friendship-acquaintances
# 0x18961	RelationshipBit	relbit_Pregnancy_Birthparent
# 0x79EB	RelationshipBit	friendship-bff_BromanticPartner (bros??)
# 0x1A36D	RelationshipBit	relationshipbit_CoWorkers
# 0x27A6    had first kiss
# 0x12E3B	RelationshipBit	ShortTerm_RecentFirstKiss
# 0x873B	RelationshipBit	romantic-HaveDoneWooHoo
# 0x17B82	RelationshipBit	romantic-HaveDoneWooHoo_Recently
# 0x3DB4	RelationshipBit	friendship-despised
# 0x181C4	RelationshipBit	HaveBeenRomantic
# 0x1F064	RelationshipBit	romantic-ExchangedNumbers
# 0x3DDF	RelationshipBit	RomanticCombo_Soulmates
# 0x18465	RelationshipBit	romantic-Promised = engaged but as teens
# 0x3DC8	RelationshipBit	romantic-Engaged
# 0x3DCE	RelationshipBit	romantic-Married
# 0x34CCE	RelationshipBit	relationshipBit_Clone		[RoM]
# clone from GTW
# 0x3DD9	RelationshipBit	RomanticCombo_ItsAwkward
# 0x3DDA	RelationshipBit	RomanticCombo_ItsComplicated
# 0x3DDB	RelationshipBit	RomanticCombo_ItsVeryAwkward
# 0x3DDC	RelationshipBit	RomanticCombo_ItsVeryComplicated

# extendedrelationships.package by simsmodelsimmer also features:
# 0x794	great-grandchild
# 0x795	great-grandparent
# 0x796	sibling-in-law
# 0x797	??
# 0x798	??
# 0x793	child-in-law
# 0x788	parent-in-law

# test set instances
# 0x278D9 - testSetInstance_FamilyRelBitAcquired_HasNoSiblingBit
# 0x278EC - testSetInstance_FamilyRelBitAcquired_HasNoParentBit