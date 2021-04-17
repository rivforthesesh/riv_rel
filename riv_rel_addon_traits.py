# REPLACE THE BELOW WITH OUTPUT FROM MC4

from functools import wraps
import sims4.resources
from sims4.tuning.instance_manager import InstanceManager
from sims4.resources import Types
import services


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


riv_reltraits_24508_SnippetId = 24508
riv_reltraits_24508_MixerId = (13278191281562275542, 13754158052055453736,)


@inject_to(InstanceManager, 'load_data_into_class_instances')
def riv_reltraits_AddMixer_24508(original, self):
    original(self)
    if self.TYPE == Types.SNIPPET:
        key = sims4.resources.get_resource_key(riv_reltraits_24508_SnippetId, Types.SNIPPET)
        snippet_tuning = self._tuned_classes.get(key)
        if snippet_tuning is None:
            return
        for m_id in riv_reltraits_24508_MixerId:
            affordance_manager = services.affordance_manager()
            key = sims4.resources.get_resource_key(m_id, Types.INTERACTION)
            mixer_tuning = affordance_manager.get(key)
            if mixer_tuning is None:
                return
            if mixer_tuning in snippet_tuning.value:
                return
            snippet_tuning.value = snippet_tuning.value + (mixer_tuning,)


riv_reltraits_163702_SnippetId = 163702
riv_reltraits_163702_MixerId = (13278191281562275542, 13754158052055453736,)


@inject_to(InstanceManager, 'load_data_into_class_instances')
def riv_reltraits_AddMixer_163702(original, self):
    original(self)
    if self.TYPE == Types.SNIPPET:
        key = sims4.resources.get_resource_key(riv_reltraits_163702_SnippetId, Types.SNIPPET)
        snippet_tuning = self._tuned_classes.get(key)
        if snippet_tuning is None:
            return
        for m_id in riv_reltraits_163702_MixerId:
            affordance_manager = services.affordance_manager()
            key = sims4.resources.get_resource_key(m_id, Types.INTERACTION)
            mixer_tuning = affordance_manager.get(key)
            if mixer_tuning is None:
                return
            if mixer_tuning in snippet_tuning.value:
                return
            snippet_tuning.value = snippet_tuning.value + (mixer_tuning,)


riv_reltraits_24511_SnippetId = 24511
riv_reltraits_24511_MixerId = (10727265781376968145,)


@inject_to(InstanceManager, 'load_data_into_class_instances')
def riv_reltraits_AddMixer_24511(original, self):
    original(self)
    if self.TYPE == Types.SNIPPET:
        key = sims4.resources.get_resource_key(riv_reltraits_24511_SnippetId, Types.SNIPPET)
        snippet_tuning = self._tuned_classes.get(key)
        if snippet_tuning is None:
            return
        for m_id in riv_reltraits_24511_MixerId:
            affordance_manager = services.affordance_manager()
            key = sims4.resources.get_resource_key(m_id, Types.INTERACTION)
            mixer_tuning = affordance_manager.get(key)
            if mixer_tuning is None:
                return
            if mixer_tuning in snippet_tuning.value:
                return
            snippet_tuning.value = snippet_tuning.value + (mixer_tuning,)


riv_reltraits_163706_SnippetId = 163706
riv_reltraits_163706_MixerId = (10727265781376968145,)


@inject_to(InstanceManager, 'load_data_into_class_instances')
def riv_reltraits_AddMixer_163706(original, self):
    original(self)
    if self.TYPE == Types.SNIPPET:
        key = sims4.resources.get_resource_key(riv_reltraits_163706_SnippetId, Types.SNIPPET)
        snippet_tuning = self._tuned_classes.get(key)
        if snippet_tuning is None:
            return
        for m_id in riv_reltraits_163706_MixerId:
            affordance_manager = services.affordance_manager()
            key = sims4.resources.get_resource_key(m_id, Types.INTERACTION)
            mixer_tuning = affordance_manager.get(key)
            if mixer_tuning is None:
                return
            if mixer_tuning in snippet_tuning.value:
                return
            snippet_tuning.value = snippet_tuning.value + (mixer_tuning,)


# IT ENDS HERE

from server_commands.argument_helpers import SimInfoParam
from relationships.relationship_bit import RelationshipBit
from sims.sim_info_manager import SimInfoManager

# for .cfg management
import configparser
import os
from pathlib import Path

# recognise riv_rel
# Mods/riv_rel/riv_rel.ts4script/riv_rel.pyc
import sys

sys.path.append('../')
# https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
try:
    import riv_rel
    from riv_rel import get_parents_ingame, get_children_ingame

    riv_rel.riv_log('riv_rel_addon_traits successfully imported riv_rel')
except Exception as e:
    riv_rel.riv_log('error - riv_rel_addon_traits failed to import riv_rel because ' + str(e))


# new rivlog
def riv_log(string):
    return riv_rel.riv_log('[traits] ' + str(string))


# trait IDs
exc_ids = {'A': 0xc7823d01, 'B': 0xc7823d02, 'C': 0xc7823d03, 'D': 0xc7823d04,
           'E': 0xc7823d05, 'F': 0xc7823d06, 'G': 0xc7823d07, 'H': 0xc7823d08}
fam_ids = {'A': 0x8ffadecb, 'B': 0x8ffadec8, 'C': 0x8ffadec9, 'D': 0x8ffadece,
           'E': 0x8ffadecf, 'F': 0x8ffadecc, 'G': 0x8ffadecd, 'H': 0x8ffadec2}
founder_ids = {'A': 0xa2e336f4, 'B': 0xa2e336f7, 'C': 0xa2e336f6, 'D': 0xa2e336f1,
               'E': 0xa2e336f0, 'F': 0xa2e336f3, 'G': 0xa2e336f2, 'H': 0xa2e336fd}
inc_ids = {'A': 0x92c573ef, 'B': 0x92c573ec, 'C': 0x92c573ed, 'D': 0x92c573ea,
           'E': 0x92c573eb, 'F': 0x92c573e8, 'G': 0x92c573e9, 'H': 0x92c573e6}
heir_ids = {'A': 0xE9C0BADB, 'B': 0xE9C0BAD8, 'C': 0xE9C0BAD9, 'D': 0xE9C0BADE,
            'E': 0xE9C0BADF, 'F': 0xE9C0BADC, 'G': 0xE9C0BADD, 'H': 0xE9C0BAD2}

# search_if_updating_settings

# auto inclusions
# parent of fam
riv_auto_inc_parent = False
# parent of heir
riv_auto_inc_heir_parent = True
# spouse of fam
riv_auto_inc_spouse = False
# spouse of heir
riv_auto_inc_heir_spouse = True
# child of fam
riv_auto_fam_child = True

try:
    # config stuff
    config_dir = Path(__file__).resolve().parent.parent
    config_name = 'riv_rel - overall settings.cfg'
    file_path = os.path.join(config_dir, config_name)
    config = configparser.ConfigParser()

    # try to get cfg file
    try:
        config.read_file(open(file_path, 'r'))
    except:
        riv_log('no .cfg file found. creating one...')

    # default settings if needed
    if not (os.path.isfile(file_path) and 'addon_traits' in config.sections()):
        # search_if_updating_settings
        config['addon_traits'] = {}
        config['addon_traits']['riv_auto_inc_parent'] = str(riv_auto_inc_parent)
        config['addon_traits']['riv_auto_inc_heir_parent'] = str(riv_auto_inc_heir_parent)
        config['addon_traits']['riv_auto_inc_spouse'] = str(riv_auto_inc_spouse)
        config['addon_traits']['riv_auto_inc_heir_spouse'] = str(riv_auto_inc_heir_spouse)
        config['addon_traits']['riv_auto_fam_child'] = str(riv_auto_fam_child)
        with open(file_path, 'w') as cfg_file:
            config.write(cfg_file)
            riv_log('added cfg settings')

    # now cfg will exist; load in settings
    config.read_file(open(file_path, 'r'))
    try:  # have to have this within 'try' just in case
        # search_if_updating_settings
        riv_auto_inc_parent = config.getboolean('addon_traits', 'riv_auto_inc_parent')
        riv_auto_inc_heir_parent = config.getboolean('addon_traits', 'riv_auto_inc_heir_parent')
        riv_auto_inc_spouse = config.getboolean('addon_traits', 'riv_auto_inc_spouse')
        riv_auto_inc_heir_spouse = config.getboolean('addon_traits', 'riv_auto_inc_heir_spouse')
        riv_auto_fam_child = config.getboolean('addon_traits', 'riv_auto_fam_child')

        riv_log('loaded in cfg settings')
    except Exception as e:
        riv_log('error - failed to load in cfg settings because ' + str(e))
except Exception as e2:
    riv_log('error - something went wrong with the cfg: ' + str(e2))
    riv_log('using riv\'s default settings')

if riv_auto_inc_parent:
    riv_log('parents of famX that are not in famX are given incX')
if riv_auto_inc_heir_parent:
    riv_log('parents of heirX that are not in famX are given incX')
if riv_auto_inc_spouse:
    riv_log('spouses of famX that are not in famX are given incX')
if riv_auto_inc_heir_spouse:
    riv_log('spouses of heirX that are not in famX are given incX')
if riv_auto_fam_child:
    riv_log('children of famX are given famX')


# TRAITS: SETTING FOUNDERS AND GROWING FAMILIES
# https://modthesims.info/t/603511

def trait_exc(X: str):
    return services.get_instance_manager(Types.TRAIT).get(exc_ids[X])


def trait_fam(X: str):
    return services.get_instance_manager(Types.TRAIT).get(fam_ids[X])


def trait_founder(X: str):
    return services.get_instance_manager(Types.TRAIT).get(founder_ids[X])


def trait_inc(X: str):
    return services.get_instance_manager(Types.TRAIT).get(inc_ids[X])


def trait_heir(X: str):
    return services.get_instance_manager(Types.TRAIT).get(heir_ids[X])


# tells you if sim_x is any founder
def is_founder(sim_x: SimInfoParam):
    for X in founder_ids.keys():
        if sim_x.has_trait(trait_founder(X)):
            return True
    return False


# includes sim in family X
# TODO: clean it up
# via = True <=> this is being done by calling a boi
# output and _connection=None are just included for the sake of it!
def include_in_family(X: str, sim_x: SimInfoParam, via=False, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    if not (sim_x.has_trait(trait_fam(X)) or sim_x.has_trait(trait_inc(X))):  # if they're not already in famX / incX
        if not sim_x.has_trait(trait_exc(X)):  # and if they're not excluded from X
            sim_x.add_trait(trait_inc(X))  # then include them
            riv_log('included ' + sim_x.first_name + ' ' + sim_x.last_name + ' in family ' + X)
            try:  # for console output
                output(sim_x.first_name + ' ' + sim_x.last_name + ' is now included in family ' + X)
            except:
                pass
    else:
        try:
            if not via:
                output(sim_x.first_name + ' is in this family or already included.')
        except:
            pass


# above as a console command
# e.g. riv_include_in_family Pihn Pine A
@sims4.commands.Command('riv_include_in_family', command_type=sims4.commands.CommandType.Live)
def console_add_inc(sim_x: SimInfoParam, X='A', _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    X = X.upper()  # makes sure it's uppercase
    if not (sim_x.has_trait(trait_fam(X)) or sim_x.has_trait(trait_inc(X))):  # if they're not already in famX / incX
        if not sim_x.has_trait(trait_exc(X)):  # and if they're not excluded from X
            sim_x.add_trait(trait_inc(X))  # then include them
            riv_log('included ' + sim_x.first_name + ' ' + sim_x.last_name + ' in family ' + X)
            try:  # for console output
                output(sim_x.first_name + ' ' + sim_x.last_name + ' is now included in family ' + X)
            except:
                pass
    else:
        try:
            output(sim_x.first_name + ' is in this family or already included.')
        except:
            pass


# gets spouses ingame
def get_spouses(sim_x: SimInfoParam):
    manager = services.get_instance_manager(Types.RELATIONSHIP_BIT)
    spouse_relbit = manager.get(0x3DCE)
    sim_spouses = []
    for sim_y in services.sim_info_manager().get_all():
        if sim_x.relationship_tracker.has_bit(sim_y.sim_id, spouse_relbit):
            sim_spouses.append(sim_y)
    return sim_spouses


# adds sim to family X, includes parents/spouses if relevant
# via = True <=> done via another sim
def add_to_family(X: str, sim_x: SimInfoParam, output=None, via=False):
    if not sim_x.has_trait(trait_fam(X)):  # if they're not already in family X
        if not sim_x.has_trait(trait_exc(X)):  # and if they're not excluded from X
            sim_x.add_trait(trait_fam(X))  # then add to family
            riv_log('added ' + sim_x.first_name + ' ' + sim_x.last_name + ' to family ' + X)
            if sim_x.has_trait(trait_inc(X)):  # remove inc trait
                sim_x.remove_trait(trait_inc(X))
        else:
            try:
                if not via:
                    output(sim_x.first_name + ' has been excluded from family ' + X)
            except:
                pass
            return
    # if they have the trait, whether added before or now
    if sim_x.has_trait(trait_fam(X)):
        if riv_auto_inc_parent:  # if we want to auto add parents
            for parent in get_parents_ingame(sim_x):  # look at ingame parents
                if not parent.has_trait(trait_fam(X)):  # if the parent isn't in the family
                    riv_log('including parent ' + parent.first_name)
                    include_in_family(X, parent, True)  # then include them
        if riv_auto_inc_spouse:  # if we want to auto add spouses
            for spouse in get_spouses(sim_x):  # look at spouses
                if not spouse.has_trait(trait_fam(X)):  # if the spouse isn't in the family
                    riv_log('including spouse ' + spouse.first_name)
                    include_in_family(X, spouse, True)  # then include them
        if riv_auto_fam_child:  # if we want to auto add fam to childen
            for child in get_children_ingame(sim_x):  # look at children
                if not child.has_trait(trait_fam(X)):  # if the child isn't in the family
                    riv_log('including child ' + child.first_name)
                    add_to_family(X, child, output, True)  # then add them


# above as a console command
# e.g. riv_add_to_family Rhona "Pine I" A
@sims4.commands.Command('riv_add_to_family', command_type=sims4.commands.CommandType.Live)
def console_add_fam(sim_x: SimInfoParam, X='A', _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    X = X.upper()  # makes sure it's uppercase

    if sim_x.has_trait(trait_fam(X)):
        output(sim_x.first_name + ' ' + sim_x.last_name + ' is already in this family!')
        return
    add_to_family(X, sim_x, output, False)
    if sim_x.has_trait(trait_fam(X)):
        output(sim_x.first_name + ' ' + sim_x.last_name + ' is now in family ' + X + '!')


# excludes sim from family X
def exclude_from_family(X: str, sim_x: SimInfoParam, output=None):
    if not sim_x.has_trait(trait_exc(X)):  # if they aren't already excluded
        if not sim_x.has_trait(trait_founder(X)):  # if they aren't the founder
            sim_x.add_trait(trait_exc(X))
            riv_log('excluded ' + sim_x.first_name + ' ' + sim_x.last_name + ' from family ' + X)
        else:
            try:
                output(sim_x.first_name + ' is the founder! You can\'t exclude them.')
            except:
                pass
            return
    else:
        try:
            output(sim_x.first_name + ' is already excluded.')
        except:
            pass
        return
    # remove family and inc traits
    if sim_x.has_trait(trait_fam(X)):
        sim_x.remove_trait(trait_fam(X))
        riv_log('removed fam' + X + ' trait from ' + sim_x.first_name + ' ' + sim_x.last_name)
    if sim_x.has_trait(trait_inc(X)):
        sim_x.remove_trait(trait_inc(X))
        riv_log('removed inc' + X + ' trait from ' + sim_x.first_name + ' ' + sim_x.last_name)
    if sim_x.has_trait(trait_heir(X)):
        sim_x.remove_trait(trait_heir(X))
        riv_log('removed heir' + X + ' trait from ' + sim_x.first_name + ' ' + sim_x.last_name)
    try:
        output(sim_x.first_name + ' is now excluded from family ' + X)
    except:
        pass


# above as a console command
# e.g. riv_exclude_from_family Kerry Oschner A
@sims4.commands.Command('riv_exclude_from_family', command_type=sims4.commands.CommandType.Live)
def console_add_exc(sim_x: SimInfoParam, X='A', _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    X = X.upper()  # makes sure it's uppercase
    exclude_from_family(X, sim_x, output)


# different version for the .package to call
@sims4.commands.Command('riv_exclude_from_A', command_type=sims4.commands.CommandType.Live)
def exclude_from_A(x_id: int):
    riv_log('added excA trait to ' + services.sim_info_manager().get(x_id).sim_info.first_name)
    return exclude_from_family('A', services.sim_info_manager().get(x_id).sim_info)


# makes sim heir of family X
def make_heir(X: str, sim_x: SimInfoParam, output=None):
    if (sim_x.has_trait(trait_fam(X)) or sim_x.has_trait(trait_inc(X))):  # if they're in famX / incX
        if not sim_x.has_trait(trait_heir(X)):  # and if they aren't already an heir
            sim_x.add_trait(trait_heir(X))  # then make them the heir
            riv_log('made ' + sim_x.first_name + ' ' + sim_x.last_name + ' an heir of family ' + X)
            try:  # for console output
                output(sim_x.first_name + ' ' + sim_x.last_name + ' is now an heir of family ' + X)
            except:
                pass
            # propagate this
            if riv_auto_inc_heir_parent:  # if we want to auto add parents
                for parent in get_parents_ingame(sim_x):  # look at ingame parents
                    if not parent.has_trait(trait_fam(X)):  # if the parent isn't in the family
                        riv_log('including parent ' + parent.first_name)
                        include_in_family(X, parent, True)  # then include them
            if riv_auto_inc_heir_spouse:  # if we want to auto add spouses
                for spouse in get_spouses(sim_x):  # look at spouses
                    if not spouse.has_trait(trait_fam(X)):  # if the spouse isn't in the family
                        riv_log('including spouse ' + spouse.first_name)
                        include_in_family(X, spouse, True)  # then include them
        else:
            try:
                output(sim_x.first_name + ' ' + sim_x.last_name + ' is already an heir of family ' + X)
            except:
                pass
    else:
        try:
            output(sim_x.first_name + ' ' + sim_x.last_name + ' is not in, or included in, family ' + X)
            if sim_x.has_trait(trait_exc(X)):
                output('you need to remove excX and then add either famX or incX before you can add heirX')
            else:
                output('you need to add either famX or incX before you can add heirX')
        except:
            pass


# above as a console command
# e.g. riv_make_heir Avina Pine A
@sims4.commands.Command('riv_make_heir', command_type=sims4.commands.CommandType.Live)
def console_make_heir(sim_x: SimInfoParam, X='A', _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    X = X.upper()  # makes sure it's uppercase
    make_heir(X, sim_x, output)


# different version for the .package to call
@sims4.commands.Command('riv_make_heir_A', command_type=sims4.commands.CommandType.Live)
def make_heir_A(x_id: int):
    riv_log('added heirA trait to ' + services.sim_info_manager().get(x_id).sim_info.first_name)
    return make_heir('A', services.sim_info_manager().get(x_id).sim_info)


# function to check what traits sim_x has for family X
# returns whether they have any traits for this family
def rivtraits_name_fam(sim_x: SimInfoParam, X='A', _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    if sim_x.has_trait(trait_exc(X)):
        output('sim ' + sim_x.first_name + ' ' + sim_x.last_name + ' is excluded from family ' + X)
        if sim_x.has_trait(trait_founder(X)):
            output(f'    they also have the founder{X} trait - please remove the wrong one with MCCC')
        if sim_x.has_trait(trait_heir(X)):
            output(f'    they also have the heir{X} trait - please remove the wrong one with MCCC')
        if sim_x.has_trait(trait_founder(X)):
            output(f'    they also have the fam{X} trait - please remove the wrong one with MCCC')
        if sim_x.has_trait(trait_heir(X)):
            output(f'    they also have the inc{X} trait - please remove the wrong one with MCCC')
    elif sim_x.has_trait(trait_founder(X)):
        output('sim ' + sim_x.first_name + ' ' + sim_x.last_name + ' is the founder of family ' + X)
        if sim_x.has_trait(trait_heir(X)):
            output(f'    they also have the heir{X} trait!')
        else:
            output(f'    they don\'t have the heir{X} trait - you\'ll want to add this one with the command:')
            output('        riv_make_heir {} {} {}'.format(sim_x.first_name, sim_x.last_name, X))
        if sim_x.has_trait(trait_fam(X)):
            output(f'    they also have the fam{X} trait!')
        else:
            output(f'    they don\'t have the fam{X} trait - you\'ll want to add this one with the command:')
            output('        riv_add_to_family {} {} {}'.format(sim_x.first_name, sim_x.last_name, X))
        if sim_x.has_trait(trait_inc(X)):
            output(f'    they also have the inc{X} trait - please remove the wrong one with MCCC')
    elif sim_x.has_trait(trait_heir(X)):
        output('sim ' + sim_x.first_name + ' ' + sim_x.last_name + ' is an heir of family ' + X)
        if sim_x.has_trait(trait_fam(X)):
            output(f'    they also have the fam{X} trait!')
        elif sim_x.has_trait(trait_inc(X)):
            output(f'    they also have the inc{X} trait!')
        else:
            output(f'    they don\'t have the fam{X} or inc{X} traits - if they\'re related to your founder, enter:')
            output('        riv_add_to_family {} {} {}'.format(sim_x.first_name, sim_x.last_name, X))
            output('    otherwise, if they aren\'t related to your founder, enter this command:')
            output('        riv_include_in_family {} {} {}'.format(sim_x.first_name, sim_x.last_name, X))
    elif sim_x.has_trait(trait_fam(X)):
        output('sim ' + sim_x.first_name + ' ' + sim_x.last_name + ' is a member of family ' + X)
        if sim_x.has_trait(trait_inc(X)):
            output(f'    they also have the inc{X} trait - please remove the wrong one with MCCC')
    elif sim_x.has_trait(trait_inc(X)):
        output('sim ' + sim_x.first_name + ' ' + sim_x.last_name + ' is included in family ' + X)
    else:
        return False  # they don't have a family trait
    return True  # they do have a family trait


# console command to find the traits
@sims4.commands.Command('riv_traits_by_name', command_type=sims4.commands.CommandType.Live)
def console_rivtraits_name(sim_x: SimInfoParam, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    num_fams = 0
    for X in founder_ids.keys():
        if rivtraits_name_fam(sim_x, X, _connection):
            num_fams += 1
        else:
            continue  # doesn't have any of these traits
    if num_fams == 1:
        output(sim_x.first_name + ' ' + sim_x.last_name + ' is a member of 1 family')
    else:
        output(sim_x.first_name + ' ' + sim_x.last_name + ' is a member of ' + str(num_fams) + ' families')


# console command to find the traits
@sims4.commands.Command('riv_traits_by_fam', command_type=sims4.commands.CommandType.Live)
def console_rivtraits_fam(X='A', _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    num_sims = 0
    X = X.upper()  # makes sure it's uppercase
    for sim_x in services.sim_info_manager().get_all():
        if rivtraits_name_fam(sim_x, X, _connection):
            num_sims += 1
        else:
            continue  # doesn't have any of these traits
    output('number of sims in this family = ' + str(num_sims))


# do the above for all sims
@sims4.commands.Command('riv_traits', command_type=sims4.commands.CommandType.Live)
def console_rivtraits(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    for X in founder_ids.keys():
        output('family ' + X + ':')
        console_rivtraits_fam(X, _connection)
        output('')


# adds founder trait to sim named, e.g. riv_add_founder Zaaham Pine A
@sims4.commands.Command('riv_add_founder', command_type=sims4.commands.CommandType.Live)
def console_add_founder(sim_x: SimInfoParam, X='A', _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    X = X.upper()  # makes sure it's uppercase

    # make sure that there is NO other sim with this particular founder trait first
    for sim_y in services.sim_info_manager().get_all():
        if sim_y.has_trait(trait_founder(X)) and not sim_x == sim_y:  # if another is the founder
            output('sim ' + sim_y.first_name + ' ' + sim_y.last_name + ' is the founder of family ' + X)
            return

    if is_founder(sim_x):
        if sim_x.has_trait(trait_founder(X)):
            output(sim_x.first_name + ' is already the founder of family ' + X + '!')
        else:
            output(sim_x.first_name + ' is already a founder of a different legacy!')
            return
    else:
        sim_x.add_trait(trait_founder(X))
        output(sim_x.first_name + ' is now the founder of family ' + X + '!')
        # housekeeping, ensuring propagation
        output('adding to family...')
        add_to_family(X, sim_x, output, False)
        output('making heir...')
        make_heir(X, sim_x, output)


# removes founder trait from sim named
# @sims4.commands.Command('riv_remove_founder', command_type=sims4.commands.CommandType.Live)
# def console_remove_founder(sim_x: SimInfoParam, _connection=None):
#    output = sims4.commands.CheatOutput(_connection)


# clears family X
@sims4.commands.Command('riv_clear_fam', command_type=sims4.commands.CommandType.Live)
def console_clear_fam(X='A', _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    X = X.upper()  # makes sure it's uppercase
    traits_count = 0
    for sim_x in services.sim_info_manager().get_all():
        if sim_x.has_trait(trait_founder(X)):
            sim_x.remove_trait(trait_founder(X))
            traits_count += 1
        if sim_x.has_trait(trait_heir(X)):
            sim_x.remove_trait(trait_heir(X))
            traits_count += 1
        if sim_x.has_trait(trait_fam(X)):
            sim_x.remove_trait(trait_fam(X))
            traits_count += 1
        if sim_x.has_trait(trait_inc(X)):
            sim_x.remove_trait(trait_inc(X))
            traits_count += 1
        if sim_x.has_trait(trait_exc(X)):
            sim_x.remove_trait(trait_exc(X))
            traits_count += 1
    output(f'cleared {str(traits_count)} founder/heir/fam/inc/exc traits for family {X}')
    riv_log(f'cleared {str(traits_count)} founder/heir/fam/inc/exc traits for family {X}')


# clears all families
@sims4.commands.Command('riv_clear_fam_all', command_type=sims4.commands.CommandType.Live)
def console_clear_fam_all(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    for X in founder_ids.keys():
        console_clear_fam(X, _connection)


# clears all family traits from one sim
@sims4.commands.Command('riv_clear_fam_sim', command_type=sims4.commands.CommandType.Live)
def console_clear_fam_from_sim(sim_x: SimInfoParam, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    traits_count = 0
    for X in founder_ids.keys():
        if sim_x.has_trait(trait_founder(X)):
            sim_x.remove_trait(trait_founder(X))
            output(f'removed founder{X} trait - you might want to run "riv_clear_fam {X}" to remove family {X} traits '
                   f'from all sims, or readd with "riv_add_founder {sim_x.first_name} {sim_x.last_name} {X}"')
            traits_count += 1
        if sim_x.has_trait(trait_heir(X)):
            sim_x.remove_trait(trait_heir(X))
            output(f'removed heir{X} trait; readd with "riv_make_heir {sim_x.first_name} {sim_x.last_name} {X}"')
            traits_count += 1
        if sim_x.has_trait(trait_fam(X)):
            sim_x.remove_trait(trait_fam(X))
            output(f'removed fam{X} trait; readd with "riv_add_to_family {sim_x.first_name} {sim_x.last_name} {X}"')
            traits_count += 1
        if sim_x.has_trait(trait_inc(X)):
            sim_x.remove_trait(trait_inc(X))
            output(f'removed inc{X} trait; readd with "riv_include_in_family {sim_x.first_name} {sim_x.last_name} {X}"')
            traits_count += 1
        if sim_x.has_trait(trait_exc(X)):
            sim_x.remove_trait(trait_exc(X))
            output(f'removed exc{X} trait; readd with "riv_exclude_from_family {sim_x.first_name} {sim_x.last_name} {X}"')
            traits_count += 1
    output(f'cleared {str(traits_count)} founder/heir/fam/inc/exc traits from {sim_x.first_name}')
    riv_log(f'cleared {str(traits_count)} founder/heir/fam/inc/exc traits from {sim_x.first_name}')


# for me lol
@sims4.commands.Command('riv_propagate_heir_A', command_type=sims4.commands.CommandType.Live)
def console_propagate_heir_A(sim_x: SimInfoParam, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    founder = None  # making sure this variable exists outside the loop

    # get founder
    for sim_y in services.sim_info_manager().get_all():
        if sim_y.has_trait(trait_founder('A')):
            founder = sim_y
            break
    else:
        # did not break
        output('did not find founderA')
        return

    # get founder's descendants and sim's ancestors
    founder_descendants = riv_rel.get_descendants(founder)
    sim_ancestors = riv_rel.get_ancestors(sim_x)

    # different cases based on whether there are rivsims or not
    if riv_rel.riv_sim_list.sims:
        heir_list_tmp = [heir for heir in founder_descendants.keys() if heir in sim_ancestors.keys()]
        heir_list = []
        for rivsim in heir_list_tmp:
            # get ingame sims
            heir = riv_rel.get_sim_from_rivsim(rivsim)
            if heir is not None:
                heir_list.append(heir)
    else:
        heir_list = [heir for heir in founder_descendants.keys() if heir in sim_ancestors.keys()]
    # add the sims themselves
    heir_list.append(riv_rel.get_sim_from_rivsim(sim_x))
    heir_list.append(riv_rel.get_sim_from_rivsim(founder))
    riv_log('heir_list = ' + str([heir.first_name for heir in heir_list]))

    # make these sims heirs
    for sim_y in heir_list:
        make_heir('A', sim_y)


# injections
@inject_to(SimInfoManager, 'on_sim_info_created')
def auto_json_fam_osic(original, self):
    result = original(self)
    try:
        # go through babies, get their parents
        for sim in services.sim_info_manager().get_all():
            if sim.is_baby:
                # riv_log('tmp!! - auto_inc_parent, baby ' + sim.first_name + ' ' + sim.last_name)
                # got to here on birth
                #
                parents = get_parents_ingame(sim)
                for parent in parents:
                    # add bab to family
                    if riv_auto_fam_child:  # sim_y parent in fam X => sim_x in fam X
                        for X in fam_ids.keys():
                            if parent.has_trait(trait_fam(X)):
                                add_to_family(X, sim)
                    # include parent in family
                    if riv_auto_inc_parent:  # sim_x in fam X => sim_y included in X
                        for X in inc_ids.keys():
                            if sim.has_trait(trait_fam(X)) and not parent.has_trait(trait_fam(X)):
                                include_in_family(X, parent)
                    elif riv_auto_inc_heir_parent:  # sim_x heir of X => sim_y included in X
                        for X in heir_ids.keys():
                            if sim.has_trait(trait_heir(X)) and not not parent.has_trait(trait_fam(X)):
                                include_in_family(X, parent)
                riv_log('ran auto_fam_osic for sim ' + sim.first_name + ' ' + sim.last_name)
    except Exception as e:
        riv_log('error in auto_fam in on_sim_info_created: ' + str(e))
        raise Exception('(riv) error in auto_fam in on_sim_info_created: ' + str(e))
    return result


def auto_inc(sim, X):
    try:
        include_in_family(X, sim)
        riv_log('ran auto_inc for sim ' + sim.first_name + ' into family ' + X)
    except Exception as e:
        riv_log('error in auto_inc: ' + str(e))
        raise Exception('(riv) error in auto_inc: ' + str(e))


# AUTOMATIC ADD TO FAM, INC PARENT IN FAM
# run on age up to toddler
# !!! inject to age up

# AUTOMATIC INC SPOUSE IN FAM
# run on add spouse
@inject_to(RelationshipBit, 'on_add_to_relationship')
def auto_inc_spouse_oatr(original, self, sim, target_sim_info, relationship, from_load):
    result = original(self, sim, target_sim_info, relationship, from_load)
    try:
        if riv_auto_inc_spouse or riv_auto_inc_heir_spouse:
            manager = services.get_instance_manager(Types.RELATIONSHIP_BIT)
            spouse_relbit = manager.get(0x3DCE)
            if self.matches_bit(spouse_relbit):  # if a parent relbit has been added
                # see if any family relbits need adding
                for X in founder_ids.keys():  # for each family
                    if target_sim_info.has_trait(trait_fam(X)) and riv_auto_inc_spouse:
                        # if the target is in the family
                        auto_inc(sim, X)  # include the spouse
                    elif target_sim_info.has_trait(trait_heir(X)) and riv_auto_inc_heir_spouse:
                        # if the target is an heir
                        auto_inc(sim, X)  # include the spouse
                riv_log('ran auto_inc_spouse_oatr for sims ' + sim.first_name + ' and ' + target_sim_info.first_name)
            # nb. should have already returned if it was an object rel
    except Exception as e:
        riv_log('error in auto_inc_spouse in on_add_to_relationship: ' + str(e))
        raise Exception('(riv) error in auto_inc_spouse in on_add_to_relationship: ' + str(e))
    return result


# list sims in each generation in fam A
@sims4.commands.Command('riv_show_family', command_type=sims4.commands.CommandType.Live)
def console_famX(X='A', _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    X = X.upper()

    # find heir
    # for sim_x in [riv_rel.get_sim_from_rivsim(sim_z) for sim_z in riv_rel.riv_sim_list.sims
    # if riv_rel.get_sim_from_rivsim(sim_z) is not None]:
    for sim_x in services.sim_info_manager().get_all():
        if sim_x.has_trait(trait_founder(X)):
            # alternatively...
            # if get_sim_from_rivsim(sim_x) is not None:
            # if get_sim_from_rivsim(sim_x).has_trait(services.get_instance_manager(Types.TRAIT).get('0xa2e336f4')):
            founder = riv_rel.get_rivsim_from_sim(sim_x)
            riv_log(f'got the founder for family {X}')
            break
    else:
        output(f'did not find founder for family {X}')
        return  # no founder

    # find their descendants
    famX_tmp = riv_rel.get_descendants(founder)  # = {sim_z: [(n, sim_zx), ...]}
    riv_log('got list of founder\'s descendants')
    famX_list = [(f'{founder.first_name} {founder.last_name}', 1, 0)]

    for sim_z in famX_tmp.keys():
        game_sim_z = riv_rel.get_sim_from_rivsim(sim_z)
        # get the stage heir, fam, exc, no traits
        if sim_z.is_culled:
            stage = 4
        elif game_sim_z.has_trait(trait_heir(X)):
            stage = 0
        elif game_sim_z.has_trait(trait_fam(X)):
            stage = 1
        elif game_sim_z.has_trait(trait_exc(X)):
            stage = 2
        else:
            stage = 3
        famX_list.append((f'{sim_z.first_name} {sim_z.last_name}',
                          max([tup[0] for tup in famX_tmp[sim_z]]) + 1,
                          stage))
    # famX_list = [(sim_z's name, n), ...] where n is the (max!) generation number of that sim
    riv_log('got famX_list')

    # TODO: make sure this doesn't loop infinitely
    #   output to text file
    gen = 0
    stages = {0: f'heir{X}', 1: f'fam{X}', 2: f'exc{X}', 3: 'other, unculled', 4: 'culled'}
    max_gen = max([sim[1] for sim in famX_list])
    max_stage = max(list(stages.keys()))
    while gen < max_gen:
        gen += 1
        output(f'\n ---- gen {gen} ---- ')
        stage = 0
        while stage < max_stage:
            this_block = [sim[0] for sim in famX_list if sim[1] == gen and sim[2] == stage]
            if this_block:
                output(stages[stage] + ' sims: '
                       + str(this_block).replace('[', '').replace(']', '').replace('\'', '').replace('"', ''))
            stage += 1
