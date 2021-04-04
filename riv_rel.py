from server_commands.argument_helpers import SimInfoParam
# from relationships.relationship_service import RelationshipService
# from server_commands.genealogy_commands import get_family_relationship_bit
# from sims.sim_info import get_sim_instance, get_name_data
from sims.sim_info import SimInfo
import services, sims4.commands, sims.sim_info_types, sims.sim_info_manager, server_commands.relationship_commands
from relationships.relationship import Relationship
from relationships.relationship_bit import RelationshipBit
from relationships.relationship_tracker import RelationshipTracker
from sims4.resources import INSTANCE_TUNING_DEFINITIONS, Types # for get_parents
from typing import List, Dict

# services, sims4.commands:
#   @sims4.commands.Command
#   command_type=sims4.commands.CommandType.Live
#   output = sims4.commands.CheatOutput(_connection)
# sims.sim_info_manager:
#   get_sim_info_by_name
# find out what specifically we need from sims.sim_info

# commands break if sim has spaces in their first/last names (e.g. Rhona Pine I)
# overcome with Rhona "Pine I"

# gets direct and indirect rel as a console command
@sims4.commands.Command('riv_rel', command_type=sims4.commands.CommandType.Live)
def riv_getrelation(sim_x: SimInfoParam, sim_y: SimInfoParam, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    found_rel = 0
    if sim_x is not None:
        if sim_y is not None:
            if sim_x == sim_y:
                output('{} {} is {} {}'.format(sim_x.first_name, sim_x.last_name, sim_y.first_name, sim_y.last_name))
                found_rel += 1
            else:
                x_ancestors = get_ancestors(sim_x)
                y_ancestors = get_ancestors(sim_y)

                # console_get_direct_rel(sim_x, sim_y, x_ancestors, y_ancestors)
                xy_direct_rel = get_direct_rel(sim_x, sim_y, x_ancestors, y_ancestors)
                if xy_direct_rel: # there is a direct relation, list is not empty
                    xy_direct_rel_str = format_direct_rel(xy_direct_rel, sim_x, sim_y)
                    for xy_rel in xy_direct_rel_str:
                        output('{} {} is {} {}\'s {}'.format(sim_x.first_name, sim_x.last_name, sim_y.first_name, sim_y.last_name, xy_rel))
                        found_rel += 1

                #console_get_indirect_rel(sim_x, sim_y, x_ancestors, y_ancestors)
                xy_indirect_rel = get_indirect_rel(sim_x, sim_y, x_ancestors, y_ancestors)
                rels_via = format_indirect_rel(xy_indirect_rel, sim_x, sim_y)
                # we now have a list (relation, via this person)
                if rels_via:
                    for rel_via in rels_via:
                        if rel_via[1] == rel_via[2]:  # via one sim
                            output('{} {} is {} {}\'s {} (relation found via {} {})'.format(sim_x.first_name, sim_x.last_name, sim_y.first_name, sim_y.last_name, rel_via[0], rel_via[1].first_name, rel_via[1].last_name))
                        else:
                            sim_z = rel_via[1]
                            sim_w = rel_via[2]  # via two sims
                            output('{} {} is {} {}\'s {} (relation found via {} {} and {} {})'.format(sim_x.first_name, sim_x.last_name, sim_y.first_name, sim_y.last_name, rel_via[0], sim_z.first_name, sim_z.last_name, sim_w.first_name, sim_w.last_name))
                        found_rel += 1
    output('relations found: ' + str(found_rel))

## for testing purposes
@sims4.commands.Command('riv_show_relbits', command_type=sims4.commands.CommandType.Live)
def console_show_relbits(sim_x: SimInfoParam, sim_y: SimInfoParam, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    relbits = services.relationship_service().get_all_bits(sim_x.sim_id, sim_y.sim_id)
    output(str(relbits))

## input: a sim. output: list of their parents
def get_parents(sim_x: SimInfoParam):
    sim_parents = []
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
    if not sim_parents:
        output('{}\'s parents not found'.format(sim_x.first_name))
    else:
        for sim_y in sim_parents:
            output('{} {} is {}\'s parent'.format(sim_y.first_name, sim_y.last_name, sim_x.first_name))

# input: a sim. output: dictionary of their ancestors sim_z with values (gens back, via child of sim_z)
# note the values are lists!!
def get_ancestors(sim_x: SimInfoParam):
    ancestors = {} # stores ancestors as {sim_z: [(n, sim_zx), (n, sim_zx)]} where
        # sim_z is n generations back from sim_x
        # sim_zx child of sim_z and ancestor of sim_x
    queue = [] # stores sims to check
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
            ancestors[sim_z] = ancestors[sim_z].append((n, sim_zx))
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
    if sim_x == sim_y:
        xy_direct_rel.append(0)
    if sim_y in x_ancestors.keys(): # sim_y is a direct ancestor of sim_x
        for sim_z in x_ancestors[sim_y]:
            xy_direct_rel.append(sim_z[0]) # gets each n from {sim_y: [(n, sim_yx), (n, sim_yx), ...]}
    if sim_x in y_ancestors.keys(): # sim_x is a direct ancestor of sim_y
        for sim_z in y_ancestors[sim_x]:
            xy_direct_rel.append(-sim_z[0]) # gets each -n from {sim_x: [(n, sim_xy), (n, sim_xy), ...]}
    return xy_direct_rel
# ... -1 => sim_x parent of sim_y, 0 => sim_x is sim_y, 1 => sim_x child of sim_y, ...

# input: two sims. output: None if there is no direct relation, generational difference if there is
def get_direct_relation(sim_x: SimInfoParam, sim_y: SimInfoParam):
    return get_direct_rel(sim_x, sim_y, get_ancestors(sim_x), get_ancestors(sim_y))

# input: a number and two sims. output: sim_x's relation to sim_y
# gens = xy_direct_rel
def format_direct_rel(gens: List, sim_x: SimInfoParam, sim_y: SimInfoParam):
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
            if sim_x.is_female:
                rel_str += 'daughter'
            else:
                rel_str += 'son'
        elif n < 0:
            if sim_x.is_female:
                rel_str += 'mother'
            else:
                rel_str += 'father'
        elif n == 0:
            rel_str = 'self'
        gens_str.append(rel_str)
    return gens_str

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
        output('{} is {}'.format(sim_x.first_name, sim_y.first_name))
    elif sib_strength == 1:
        output('{} and {} are full siblings'.format(sim_x.first_name, sim_y.first_name))
    elif sib_strength == 0.5:
        output('{} and {} are half-siblings'.format(sim_x.first_name, sim_y.first_name))
    elif sib_strength == 0:
        output('{} and {} are not siblings'.format(sim_x.first_name, sim_y.first_name))
    else:
        output('something went wrong')

# input: two sims and ancestors. output: None if there is no indirect relation, list if there is
def get_indirect_rel(sim_x: SimInfoParam, sim_y: SimInfoParam, x_ancestors: Dict, y_ancestors: Dict):
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
# SPAGHETTI
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
def format_indirect_rel(xy_indirect_rels: List, sim_x: SimInfoParam, sim_y: SimInfoParam):
    rels_via = []
    for boi in xy_indirect_rels:
        sim_z = boi[0]
        sim_w = boi[1]
        nx = boi[2]
        ny = boi[3]
        sib_strength = boi[4]
        nth = min([nx, ny]) - 1 # nth cousin
        nce = nx - ny # n times removed
        rel_str = ''
        if sib_strength == 0.5:
            rel_str = 'half-'
        if nth == 0: # pibling/sibling/nibling
            if abs(nce) > 1:
                if abs(nce) > 2:
                    rel_str += 'great'
                    if abs(nce) > 3:
                        rel_str += '(x' + str(abs(nce) - 2) + ')'
                    rel_str += '-'
                rel_str += 'grand'
            if nce < 0:
                if sim_x.is_female:
                    rel_str += 'aunt'
                else:
                    rel_str += 'uncle'
            elif nce == 0:
                if sim_x.is_female:
                    rel_str += 'sister'
                else:
                    rel_str += 'brother'
            elif nce > 0:
                if sim_x.is_female:
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
    return rels_via

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

# help
@sims4.commands.Command('riv_help', command_type=sims4.commands.CommandType.Live)
def console_help(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    output('riv_rel gen 1 - console commands and biological relations only')
    output('sim_x and sim_y can be typed as firstname lastname (use "" if there is a space in the first/last name, e.g. J "Huntington III" or "J" "Huntington III") or as the sim ID')
    output('')
    output('LIST OF COMMANDS:')
    output('riv_rel sim_x sim_y > lists family relations between sim_x and sim_y')
    output('riv_get_parents sim_x > lists parents of sim_x')
    output('riv_get_sib_strength sim_x sim_y > returns whether these sims are half/full/not siblings')
    output('riv_get_direct_rel sim_x sim_y > lists direct relations (ie. ((great-...)grand)parent/child)')
    output('riv_get_indirect_rel sim_x sim_y > lists indirect relations (ie. pibling/sibling/nibling/nth cousin m times removed)')
    output('riv_show_relbits sim_x sim_y > just dumps a list of relbits from sim_x to sim_y (not properly formatted)')
    output('riv_get_ancestors sim_x > lists ancestors of sim_x and how many generations back they are')

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

# rel bits (TARGET [TargetSim] is the XYZ of RECIPIENT [Actor])

# DIRECT
# 0x2268	RelationshipBit	family_grandparent
# 0x2269	RelationshipBit	family_parent
# 0x18961	RelationshipBit	relbit_Pregnancy_Birthparent
# 0x2265	RelationshipBit	family_son_daughter
# 0x2267	RelationshipBit	family_grandchild

# VIA SIBLINGS
# 0x2262	RelationshipBit	family_brother_sister
# 0x227A	RelationshipBit	family_cousin
# 0x227D	RelationshipBit	family_aunt_uncle
# 0x2705	RelationshipBit	family_niece_nephew

# BY MARRIAGE
# 0x2278	RelationshipBit	family_stepsibling
# 0x5FAA	RelationshipBit	family_husband_wife

# BY LOCALITY
# 0x1261E	RelationshipBit	neighbor
# 0x1A36D	RelationshipBit	relationshipbit_CoWorkers

# MISC
# 0x1ABED	RelationshipBit	relationshipBit_IsClone		[GTW]
# 0x34CCE	RelationshipBit	relationshipBit_Clone		[RoM]
# 0x27AB2	RelationshipBit	CT_notParent_CareGiver		[PH]
# 0x27AB3	RelationshipBit	CT_notParent_CareDependent	[PH]

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