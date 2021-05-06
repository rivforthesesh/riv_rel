from server_commands.argument_helpers import SimInfoParam
# from relationships.relationship_service import RelationshipService
# from server_commands.genealogy_commands import get_family_relationship_bit
# from sims.sim_info import get_sim_instance, get_name_data
from sims.sim_info import SimInfo
import services
import sims4.commands  # , sims.sim_info_types, sims.sim_info_manager, server_commands.relationship_commands
# from relationships.relationship import Relationship
from relationships.relationship_bit import RelationshipBit
# from relationships.relationship_tracker import RelationshipTracker
from typing import List, Dict
from functools import wraps
import sims4.resources
from sims.sim_info_types import Age
from sims4.resources import Types, get_resource_key
from sims4.tuning.instance_manager import InstanceManager
import random
from distributor.shared_messages import IconInfoData
# from sims4.collections import make_immutable_slots_class
from sims4.localization import LocalizationHelperTuning  # , _create_localized_string
from sims.sim_info_manager import SimInfoManager

# for notifications
# from ui.ui_dialog import UiDialogResponse, ButtonType, CommandArgType
from ui.ui_dialog_notification import UiDialogNotification

# for finding file location
# https://discordapp.com/channels/605863047654801428/624442188335415320/760257300002504756
import json
# import date_and_time
import os
from pathlib import Path

# for config file (used for auto_json settings)
import configparser

# for getting save IDs and running on save
from services.persistence_service import PersistenceService

# for getting autosaves from MCCC (add IDs to mccc_autosaves = [])
# Mods/riv_rel/riv_rel.ts4script/riv_rel.pyc
import sys
import time

# for despawn (death) things
from interactions.utils.death import DeathTracker

# for cache (used for consang and is_eligible_couple)
from functools import lru_cache

# get irl datetime
from datetime import datetime

# datetime object containing current date and time
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")


# gets slot, e.g. if your save is Slot_0000000e then you get '0000000e'
# 14 -> 0xe -> e -> 0000000e
def get_slot():
    # get save slot ID
    per = services.get_persistence_service()
    int_slot_id = int(per._save_game_data_proto.save_slot.slot_id)
    hex_slot_id_tmp = hex(int_slot_id)[2:]
    hex_slot_id = ('0' * (8 - len(hex_slot_id_tmp))) + hex_slot_id_tmp
    return hex_slot_id


# edit a bit more from sim info
def format_sim_date():
    simNow = str(services.time_service().sim_now)
    listNow = simNow.split(' ')
    simWeek = listNow[2].split(':')
    simDay = listNow[1].split(':')
    simTime = listNow[0].split('.')
    if 0 <= int(simDay[1]):
        simWeekNumber = 1 + int(simWeek[1])
        simDayNumber = 1 + int(simDay[1])
        simTimeNow = 'week {} day {} {}'.format(simWeekNumber, simDayNumber, simTime[0])
        return simTimeNow


# GLOBALS
# mod gen/version
rr_gen = 6
# autosave
riv_auto_enabled = False  # this can be set by the user for each save. KEEP this as default false!!!
file_name_extra = ''
hex_slot_id = '00000000'  # updated on game load
# interactions (ask if related)
riv_rel_int_24508_SnippetId = 24508
riv_rel_int_24508_MixerId = (17552881007513514036,)
riv_rel_int_163702_SnippetId = 163702
riv_rel_int_163702_MixerId = (17552881007513514036,)
# for giving a heads up about own folder
jsyk_ownfolder = False  # KEEP FALSE
# for MCCC autosave compatibility
mccc_autosaves = []
mccc_autosave_enabled = False  # KEEP FALSE
# existence of addons
addons = {'computer': False, 'traits': False, 'GT': False}  # KEEP FALSE
# performance
use_currentsession_files = False  # KEEP FALSE
# features
global_include_step_rels = False  # KEEP FALSE TODO: until they work
# default cfg values
# search_if_updating_settings
cfg_default_vals = dict(
    # gen 4
    file_name_extra='default_asdfghjkl',
    auto_update_json='False',  # stays false to prevent multiple writes to default_asdfghjkl
    # gen 5
    advanced_use_currentsession_files='False',
    # gen 6
    # include_step_rels='False',
    # gen ?
)
# logging stuff for testing (true <=> riv_rel.log is in the folder)
riv_auto_log = os.path.isfile(os.path.join(Path(__file__).resolve().parent.parent, 'riv_rel.log'))
riv_log_last_line = ''
num_reps = 1
# log level (3 for showing extra, 2 for normal, 1 for errors only, 0 for none)
log_level = 2


# TODO [gen 6] always print errors option (rk. alter to make sure they don't keep getting sib/nib/pib pairs)
# new 'level' represents logging level, filtering out unneeded ones. normally 2
def riv_log(string, level=2):
    # make absolutely sure it's a string lol
    string = str(string)
    global riv_auto_log
    global log_level
    if riv_auto_log and level <= log_level:
        file_dir = Path(__file__).resolve().parent.parent
        file_name = 'riv_rel.log'
        file_path = os.path.join(file_dir, file_name)
        global riv_log_last_line
        global num_reps
        try:
            if string == riv_log_last_line:
                num_reps += 1
            else:
                if 'error' in string:
                    log_level = 1
                with open(file_path, 'a') as file:
                    if num_reps > 1:
                        file.write(f'    (repeated {num_reps} times)\n')
                    file.write(string + '\n')
                    riv_log_last_line = string
                    num_reps = 1
        except Exception as e:
            riv_log(str(e))
    else:
        pass


# new line before session
riv_log(f'[game loaded at {format(dt_string)}]', 1)
riv_log('', 1)

extra_files_tic = time.perf_counter()

# access the mods folder
mods_path = Path(__file__).resolve()
appendage = '/'
# https://stackoverflow.com/questions/33372054/get-folder-name-of-the-file-in-python
while not os.path.basename(mods_path) == 'Mods':
    mods_path = mods_path.parent
    appendage = '.' + appendage
sys.path.append(appendage)  # will go up to Mods/ folder
try:
    mccc_cfg_path = None
    # search folders and subfolders
    # https://stackoverflow.com/questions/5817209/browse-files-and-subfolders-in-python
    for root, dirs, files in os.walk(mods_path):
        for name in files:
            if name.startswith('mc_settings') and name.endswith('cfg'):
                mccc_cfg_path = root + os.sep + name
            elif name.startswith('riv_rel_addon_computer') and name.endswith('package'):
                riv_log('detected computer addon', 2)
                addons['computer'] = True
            elif (not addons['traits']) and name.startswith('riv_rel_addon_traits') \
                    and (name.endswith('package') or name.endswith('ts4script')):
                riv_log('detected traits addon', 2)
                addons['traits'] = True
            elif name.startswith('riv_rel_addon_GT') and name.endswith('ts4script'):
                riv_log('detected GT addon', 2)
                addons['GT'] = True
            if addons['computer'] and addons['traits'] and addons['GT'] and (mccc_cfg_path is not None):
                # all settings confirmed
                break
    # find file and grab it as dict
    if mccc_cfg_path is not None:
        with open(mccc_cfg_path, 'r') as mccc_cfg:
            mccc_cfg_dict = json.load(mccc_cfg)
    else:
        riv_log('did not find mc_settings.cfg', 1)
    # get vars
    mccc_autosave_enabled = mccc_cfg_dict['Autosave_Enabled']
    mccc_autosave_hexslotnumber = mccc_cfg_dict['Autosave_HexSlotNumber']
    mccc_autosave_maxsavenumber = mccc_cfg_dict['Autosave_MaxSaveNumber']
    # kill dict
    del mccc_cfg_dict
except Exception as ex:
    riv_log(f'mc_settings not grabbed from .cfg: {ex}', 1)
    mccc_autosave_enabled = False
    mccc_autosave_hexslotnumber = ''
    mccc_autosave_maxsavenumber = 0

# get list of autosave slots
if mccc_autosave_enabled:
    # turn smallest save ID into an int: '1111' -> '0x1111' -> 4369
    smallest_save = int('0x' + str(mccc_autosave_hexslotnumber), 16)
    for i in range(0, mccc_autosave_maxsavenumber):
        # int_slot_id = 4369 + i
        int_slot_id = smallest_save + i
        # hex_slot_id_tmp = 1111
        hex_slot_id_tmp = hex(int_slot_id)[2:]
        # hex_slot_id = 00001111
        hex_slot_id = ('0' * (8 - len(hex_slot_id_tmp))) + hex_slot_id_tmp
        mccc_autosaves.append(hex_slot_id)
    riv_log(f'autosave slots = {mccc_autosaves}')

extra_files_toc = time.perf_counter()
riv_log(f'time taken to find extra files (riv_rel addons and mc_settings.cfg): {extra_files_toc - extra_files_tic}')

# gen 4 -> gen 5 update: rename .cfg
for file in os.scandir(Path(__file__).resolve().parent.parent):
    if file.name.startswith('riv_rel_autojson') and file.name.endswith('.cfg'):
        os.rename(os.path.join(Path(__file__).resolve().parent.parent, file),
                  os.path.join(Path(__file__).resolve().parent.parent, 'riv_rel - individual save settings.cfg'))

# search_if_updating_settings
consang_limit = 2 ** -5  # second cousin
drel_incest = True  # whether direct rels always count as incestuous
show_consang = False  # whether consanguinity is shown in notifications

# add to or make overall cfg file
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
    if not (os.path.isfile(file_path) and 'main_mod' in config.sections()):
        config['main_mod'] = {}
        with open(file_path, 'w') as cfg_file:
            config.write(cfg_file)
            riv_log('created main_mod section in overall cfg')

    # now cfg will exist; load in settings
    config.read_file(open(file_path, 'r'))
    keys = []
    for (key, val) in config.items('main_mod'):
        if key not in keys:
            keys.append(key)
    # search_if_updating_settings

    # consanguinity
    try:
        consang_limit = config.getfloat('main_mod', 'consanguinity_limit')
        riv_log(f'grabbed main_mod consanguinity limit as {consang_limit}')
    except Exception as e:
        config['main_mod']['consanguinity_limit'] = str(consang_limit)
        with open(file_path, 'w') as cfg_file:
            config.write(cfg_file)
        riv_log(f'set up main_mod consanguinity limit as {consang_limit}')

    # show consanguinity in notifications
    try:
        show_consang = config.getboolean('main_mod', 'show_consanguinity_in_notifs')
        riv_log(f'grabbed main_mod show_consanguinity_in_notifs as {show_consang}')
    except Exception as e:
        config['main_mod']['show_consanguinity_in_notifs'] = str(show_consang)
        with open(file_path, 'w') as cfg_file:
            config.write(cfg_file)
        riv_log(f'set up main_mod show_consanguinity_in_notifs as {show_consang}')

    # direct rels are incest
    try:
        drel_incest = config.getboolean('main_mod', 'direct_rels_are_incestuous')
        riv_log(f'grabbed main_mod direct rel is always incest as {drel_incest}')
    except Exception as e:
        config['main_mod']['direct_rels_are_incestuous'] = str(drel_incest)
        with open(file_path, 'w') as cfg_file:
            config.write(cfg_file)
        riv_log(f'set up main_mod direct rel is always incest as {drel_incest}')

    riv_log('loaded in cfg settings')
except Exception as e2:
    riv_log('error - something went wrong with the cfg: ' + str(e2))
    riv_log('using riv\'s default settings')


# true and false
def true_false(x):
    if x in [True, 'True', 'true', 'TRUE']:
        return True
    elif x in [False, 'False', 'false', 'FALSE']:
        return False
    else:
        return None


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
# @sims4.commands.Command('riv_get_locale', command_type=sims4.commands.CommandType.Live)
# def riv_get_locale(_connection=None):
#    output = sims4.commands.CheatOutput(_connection)
#    output(services.get_locale())

# riv_sim_list and riv_rel_dict will be used if riv_sim_list is not empty!
# for now, sim_x and sim_y in commands MUST be sims that exist in the game

# range(a,b)   = [a, b) \cap ZZ
# range(a,b+1) = [a, b] \cap ZZ

# RivSim, RivSimList

class RivSim:
    def __init__(self, sim_x):  # will only be created in game, so current time will be readily available
        # creates RivSim from Dict (in json)
        # this code assumes that the keys exist, so make sure you're importing the right thing!
        if isinstance(sim_x, Dict):
            self.sim_id = str(sim_x['sim_id'])  # should be a string anyway
            self.first_name = sim_x['first_name']
            self.last_name = sim_x['last_name']
            self.is_female = true_false(sim_x['is_female'])
            self.is_culled = true_false(sim_x['is_culled'])
            self.time = int(sim_x['time'])
        # creates RivSim from SimInfoParam (in game)
        else:  # elif isinstance(sim_x, SimInfoParam):
            self.sim_id = str(sim_x.sim_id)  # bc json keys need to be strings
            self.first_name = sim_x.first_name
            self.last_name = sim_x.last_name
            self.is_female = sim_x.is_female
            self.is_culled = False
            self.time = services.time_service().sim_now.absolute_ticks()

    def __str__(self):
        return f'<RivSim {self.first_name} {self.last_name} {self.sim_id}>'

    def __repr__(self):
        return str(self)

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
    # also removes their marriages
    # TODO: work out why every already culled sim gets culled AGAIN
    def cull(self):
        if not self.is_culled:
            # riv_log(f'marked {self.first_name} {self.last_name} as culled')
            self.is_culled = True

    # for marking a sim as unculled; for cleaning
    def uncull(self):
        if self.is_culled:
            self.is_culled = False
            riv_log(f'marked {self.first_name} {self.last_name} as unculled')

    # for updating a sim in the file if that sim exists with different details
    def update_info(self, new_first_name, new_last_name, new_is_female, new_time):
        something_changed = False
        if self.first_name != new_first_name:
            riv_log('updated first name ' + self.first_name + ' to ' + new_first_name)
            self.first_name = new_first_name
            something_changed = True
        if self.last_name != new_last_name:
            riv_log('updated last name ' + self.last_name + ' to ' + new_last_name)
            self.last_name = new_last_name
            something_changed = True
        if self.is_female != new_is_female:
            riv_log('updated is_female ' + self.is_female + ' to ' + new_is_female)
            self.is_female = new_is_female
            something_changed = True
        if something_changed:
            self.time = new_time
            riv_log(f'updated info for {self.first_name} {self.last_name}')


class RivSimList:
    sims = []

    # TODO: check if works
    def __str__(self):
        return f'<RivSimList - len {len(self.sims)}>'

    def __repr__(self):
        return str(self)

    # loads in list of sims from .json
    def load_sims(self, file_name_extra: str):
        file_dir = Path(__file__).resolve().parent.parent
        file_name = f'riv_rel_{file_name_extra}.json'  # e.g. riv_rel_pine.json
        file_name2 = f'riv_currentsession_tmp_{file_name_extra}.json'  # e.g. riv_currentsession_tmp_pine.json
        file_path = os.path.join(file_dir, file_name)
        file_path2 = os.path.join(file_dir, file_name2)

        # https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
        if os.path.isfile(file_path2):  # if tmp file is already being used
            with open(file_path2, 'r') as json_file:  # read from this
                temp_sims = json.load(json_file)
            self.sims = [RivSim(sim) for sim in temp_sims]
        else:  # tmp file hasn't been created yet
            with open(file_path, 'r') as json_file:  # read from perm file
                temp_sims = json.load(json_file)
            if use_currentsession_files:
                riv_log('creating temporary file in .load_sims for ' + file_name_extra)
                with open(file_path2, 'w') as json_file2:  # create tmp file
                    json.dump(temp_sims, json_file2)
            self.sims = [RivSim(sim) for sim in temp_sims]
        return self.sims

    def clear_sims(self):
        self.sims = []


class RivRelDict:
    rels = {}  # sim_id: [parent_ids]

    def __str__(self):
        return f'<RivRelDict - len {len(list(self.rels.keys()))}>'

    def __repr__(self):
        return str(self)

    # loads in dict of rels from .json
    def load_rels(self, file_name_extra: str):
        file_dir = Path(__file__).resolve().parent.parent
        file_name = f'riv_relparents_{file_name_extra}.json'  # e.g. riv_rel_pine.json
        file_name2 = f'riv_currentsession_tmpparents_{file_name_extra}.json'  # e.g. riv_currentsession_tmp_pine.json
        file_path = os.path.join(file_dir, file_name)
        file_path2 = os.path.join(file_dir, file_name2)

        # https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
        if os.path.isfile(file_path2):  # if tmp file is already being used
            with open(file_path2, 'r') as json_file:
                self.rels = json.load(json_file)
        else:  # tmp file hasn't been created yet
            if os.path.isfile(file_path):
                # perm file exists
                with open(file_path, 'r') as json_file:
                    self.rels = json.load(json_file)
                if use_currentsession_files:
                    riv_log('creating temporary file in .load_rels for ' + file_name_extra)
                    with open(file_path2, 'w') as json_file2:
                        json.dump(self.rels, json_file2)
        return self.rels

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


# get list of pairs in lists
def get_pairs_yield(a: List, b: List):
    for x in a:
        for y in b:
            yield x, y


def get_pairs_return(a: List, b: List):
    ab = []
    for x in a:
        for y in b:
            ab.append((x, y))
    return ab


# input: two sims. output: list of relbits
@sims4.commands.Command('riv_show_relbits', command_type=sims4.commands.CommandType.Live)
def console_show_relbits(sim_x: SimInfoParam, sim_y: SimInfoParam, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    relbits = services.relationship_service().get_all_bits(sim_x.sim_id, sim_y.sim_id)
    output(str(relbits))


# input: a sim ID as Int or String. output: the corresponding RivSim in mem
def get_rivsim_from_id(sim_id):
    if isinstance(sim_id, int):  # if the ID is an integer
        return get_rivsim_from_id(str(sim_id))  # calls the function again but with sim_id as string
    else:
        for rivsim in riv_sim_list.sims:  # for all rivsims
            if rivsim.sim_id == sim_id:  # if it has the same ID
                return rivsim  # then this is the rivsim we want

        # has not found that rivsim, so we make it
        rivsim = RivSim(services.sim_info_manager().get(int(sim_id)).sim_info)
        riv_sim_list.sims.append(rivsim)
        return rivsim


# input: a sim as SimInfoParam or RivSim. output: the corresponding RivSim in mem
# updates the name if needed, adds rivsim if needed
def get_rivsim_from_sim(sim_z):
    try:
        if isinstance(sim_z, RivSim):  # if this is a rivsim
            return sim_z  # then just return the rivsim
        else:  # this will be a SimInfoParam
            rivsim_z = get_rivsim_from_id(str(sim_z.sim_id))
            sim_time = services.time_service().sim_now.absolute_ticks()

            if rivsim_z is None:
                rivsim_z = RivSim(sim_z)
                riv_sim_list.sims.append(rivsim_z)
            else:
                rivsim_z.update_info(sim_z.first_name, sim_z.last_name, sim_z.is_female, sim_time)

            return rivsim_z  # so we get rivsim from the id
    except Exception as e:
        riv_log(f'get_rivsim_from_sim error: {e}')


# input: a rivsim or sim. output: the corresponding sim info if it exists, else None
def get_sim_from_rivsim(rivsim_z):
    try:
        sim_z = services.sim_info_manager().get(int(rivsim_z.sim_id))
        if sim_z is not None:
            return sim_z.sim_info
        else:
            return None
    except Exception as e:
        riv_log(f'get_sim_from_rivsim error: {e}')


# gets parents, but only the sim infos in the game, going via parent relbits
def get_parents_ingame(sim_x):
    sim_parents = []
    sim_x = get_sim_from_rivsim(sim_x)

    if sim_x is None:
        return sim_parents

    manager = services.get_instance_manager(Types.RELATIONSHIP_BIT)
    parent_relbit = manager.get(0x2269)
    for sim_y in services.sim_info_manager().get_all():
        if sim_x.relationship_tracker.has_bit(sim_y.sim_id, parent_relbit):
            sim_parents.append(sim_y)

    # remove list elements that are NOT sim infos (bc apparently this happens???)
    for parent in sim_parents:
        if not isinstance(parent, SimInfo):
            sim_parents.remove(parent)

    return sim_parents


# input: a sim. output: list of their parents
def get_parents(sim_x):
    # try ingame ones first
    ingame_parents = get_parents_ingame(sim_x)

    # sort out sim_x as a rivsim
    rivsim_x = get_rivsim_from_sim(sim_x)  # rivsim_x is the entry for sim_x in riv_sim_list.sims
    if rivsim_x is None:
        rivsim_x = RivSim(sim_x)
        riv_sim_list.sims.append(RivSim(sim_x))
        riv_log(f'get_parents added sim {sim_x.first_name} {sim_x.last_name} to riv_sim_list.sims')
        # not a rivsim => won't have a rel => need to set up
        riv_rel_dict.rels[str(rivsim_x.sim_id)] = [int(parent.sim_id) for parent in ingame_parents]
    x_id = rivsim_x.sim_id  # and this is the ID as a string

    # now we build this list as rivsims
    sim_parents = []
    # sort out parents sim_y as rivsims, grabbing them from the dict entry
    for y_id in riv_rel_dict.rels.get(x_id):  # for each y_id in the list of sim_x's parents
        # {x_id: [y_id,...]}
        rivsim_y = get_rivsim_from_id(y_id)  # get rivsim_y as a rivsim
        # if there is no rivsim for this sim, create one
        if rivsim_y is None:
            sim_y = services.sim_info_manager().get(y_id).sim_info
            rivsim_y = RivSim(sim_y)
            riv_sim_list.sims.append(rivsim_y)
            riv_log(f'get_parents added sim {sim_y.first_name} {sim_y.last_name} to riv_sim_list.sims')
            riv_rel_dict.rels[str(rivsim_y.sim_id)] = [int(parent.sim_id) for parent in get_parents(rivsim_y)]
        sim_parents.append(rivsim_y)  # then add rivsim_y to the list

    return sim_parents


# the above as a console command
@sims4.commands.Command('riv_get_parents', command_type=sims4.commands.CommandType.Live)
def console_get_parents(sim_x: SimInfoParam, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    sim_parents = get_parents(sim_x)
    if not sim_parents:
        output(f'{sim_x.first_name}\'s parents not found')
    else:
        for sim_y in sim_parents:
            output(f'{sim_y.first_name} {sim_y.last_name} is {sim_x.first_name}\'s parent')


# gets children, but only the sim infos in the game, going via child relbits
def get_children_ingame(sim_x):
    sim_children = []
    sim_x = get_sim_from_rivsim(sim_x)

    if sim_x is None:
        return sim_children

    manager = services.get_instance_manager(Types.RELATIONSHIP_BIT)
    parent_relbit = manager.get(0x2269)
    for sim_y in services.sim_info_manager().get_all():
        if sim_y.relationship_tracker.has_bit(sim_x.sim_id, parent_relbit):
            sim_children.append(sim_y)

    # remove list elements that are NOT sim infos (bc apparently this happens???)
    for child in sim_children:
        if not isinstance(child, SimInfo):
            sim_children.remove(child)

    return sim_children


# also adds all sims concerned as rivsims if needed
def get_children(sim_x):
    # try ingame ones first
    ingame_children = get_children_ingame(sim_x)

    # sort out sim_x as a rivsim
    rivsim_x = get_rivsim_from_sim(sim_x)  # rivsim_x is the entry for sim_x in riv_sim_list.sims
    if rivsim_x is None:
        rivsim_x = RivSim(sim_x)
        riv_sim_list.sims.append(RivSim(sim_x))
        riv_log('get_children added sim {} {} to riv_sim_list.sims'.format(sim_x.first_name, sim_x.last_name))
    x_id = rivsim_x.sim_id  # and this is the ID as a string

    # now we build this list as rivsims
    # grab ingame kids
    sim_children = []
    for y_id in [str(child.sim_id) for child in ingame_children]:  # for each y_id in the list of sim_x's children
        rivsim_y = get_rivsim_from_id(y_id)  # get rivsim_y as a rivsim
        # if there is no rivsim for this sim, create one
        if rivsim_y is None:
            sim_y = services.sim_info_manager().get(y_id).sim_info
            rivsim_y = RivSim(sim_y)
            riv_sim_list.sims.append(rivsim_y)
            riv_log('get_children added sim {} {} to riv_sim_list.sims'.format(sim_y.first_name, sim_y.last_name))
            riv_rel_dict.rels[str(rivsim_y.sim_id)] = [int(parent.sim_id) for parent in get_parents(rivsim_y)]
        sim_children.append(rivsim_y)  # then add rivsim_y to the list

    # grab ones in rel dict
    for rivsim_y in riv_sim_list.sims:  # for every known rivsim
        y_id = rivsim_y.sim_id  # get their ID as a string
        y_parents = riv_rel_dict.rels.get(y_id)  # and this is a list of parent simIDs as ints
        if y_parents is not None:
            for z_id in y_parents:  # for each z_id
                if int(z_id) == int(x_id) and rivsim_y not in sim_children:  # same id, and this child has been counter
                    sim_children.append(rivsim_y)

    return sim_children


# the above as a console command
@sims4.commands.Command('riv_get_children', command_type=sims4.commands.CommandType.Live)
def console_get_children(sim_x: SimInfoParam, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    sim_children = get_children(sim_x)
    if not sim_children:
        output('{}\'s children not found'.format(sim_x.first_name))
    else:
        for sim_y in sim_children:
            output('{} {} is {}\'s child'.format(sim_y.first_name, sim_y.last_name, sim_x.first_name))


# input: a sim. output: dictionary of their ancestors sim_z with values (gens back, via child of sim_z)
# note the values are lists!!
# look into defaultdict later to rework adding items to the list
def get_ancestors(sim_x):
    ancestors = {}  # stores ancestors as {sim_z: [(n, sim_zx), (n, sim_zx)]} where
    # sim_z is n generations back from sim_x
    # sim_zx child of sim_z and ancestor of sim_x
    queue = []  # stores sims to check

    if riv_sim_list.sims:  # using list in mem
        sim_x = get_rivsim_from_sim(sim_x)  # rivsim_x is the entry for sim_x in riv_sim_list.sims

    for sim_z in get_parents(sim_x):
        queue.append((sim_z, 1, sim_x))
    while queue:
        tuple_znzx = queue[0]  # gets first (sim_z, n, sim_zx)
        sim_z = tuple_znzx[0]
        n = tuple_znzx[1]
        sim_zx = tuple_znzx[2]
        queue.pop(0)  # removes first item (tuple_znzx) from the queue
        for parent in get_parents(sim_z):
            queue.append((parent, n + 1, sim_z))  # adds parents of sim_z to the queue
        if sim_z in ancestors.keys():
            temp_list = ancestors[sim_z]
            temp_list.append((n, sim_zx))
            ancestors[sim_z] = temp_list.copy()
        else:
            ancestors[sim_z] = [(n, sim_zx)]  # adds sim_z: [(n, sim_zx)] to the dictionary
    return ancestors  # dictionary of sim_z: (n, sim_zx) for sim_z ancestor, n gens back, via sim_zx


# input: a sim. output: dictionary of their ancestors sim_z with values (gens back, via child of sim_z)
# note the values are lists!!
# look into defaultdict later to rework adding items to the list
def get_ancestors_ingame(sim_x):
    ancestors = {}  # stores ancestors as {sim_z: [(n, sim_zx), (n, sim_zx)]} where
    # sim_z is n generations back from sim_x
    # sim_zx child of sim_z and ancestor of sim_x
    queue = []  # stores sims to check

    if isinstance(sim_x, RivSim):
        sim_x = get_sim_from_rivsim(sim_x)
    if sim_x is None:
        return {}

    try:
        for sim_z in get_parents_ingame(sim_x):
            queue.append((sim_z, 1, sim_x))
        while queue:
            tuple_znzx = queue[0]  # gets first (sim_z, n, sim_zx)
            sim_z = tuple_znzx[0]
            n = tuple_znzx[1]
            sim_zx = tuple_znzx[2]
            queue.pop(0)  # removes first item (tuple_znzx) from the queue
            for parent in get_parents_ingame(sim_z):
                queue.append((parent, n + 1, sim_z))  # adds parents of sim_z to the queue
            if sim_z in ancestors.keys():
                temp_list = ancestors[sim_z]
                temp_list.append((n, sim_zx))
                ancestors[sim_z] = temp_list.copy()
            else:
                ancestors[sim_z] = [(n, sim_zx)]  # adds sim_z: [(n, sim_zx)] to the dictionary
    except Exception as e:
        riv_log(f'get_ancestors error: {e}')
    return ancestors  # dictionary of sim_z: (n, sim_zx) for sim_z ancestor, n gens back, via sim_zx


# get list of sims/rivsims, turn into list of sims
def rivsims_to_sims(rivsims):
    return [get_sim_from_rivsim(rivsim) for rivsim in rivsims if not (isinstance(rivsim, RivSim) and rivsim.is_culled)]


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
                output('{} {} is {} {}\'s ancestor, {} generations back'.format(sim_y.first_name, sim_y.last_name,
                                                                                sim_x.first_name, sim_x.last_name,
                                                                                sim_z[0]))


# input: a sim. output: dictionary of their descendants sim_z with values (gens back, via child of sim_z)
# note the values are lists!!
# look into defaultdict later to rework adding items to the list
def get_descendants(sim_x):
    descendants = {}  # stores descendants as {sim_z: [(n, sim_zx), (n, sim_zx)]} where
    # sim_z is n generations back from sim_x
    # sim_zx child of sim_z and descendant of sim_x
    queue = []  # stores sims to check

    if riv_sim_list.sims:  # using list in mem
        sim_x = get_rivsim_from_sim(sim_x)  # rivsim_x is the entry for sim_x in riv_sim_list.sims

    for sim_z in get_children(sim_x):
        queue.append((sim_z, 1, sim_x))
    while queue:
        tuple_znzx = queue[0]  # gets first (sim_z, n, sim_zx)
        try:
            sim_z = tuple_znzx[0]
            n = tuple_znzx[1]
            sim_zx = tuple_znzx[2]
            queue.pop(0)  # removes first item (tuple_znzx) from the queue
            for child in get_children(sim_z):
                queue.append((child, n + 1, sim_z))  # adds children of sim_z to the queue
            if sim_z in descendants.keys():
                temp_list = descendants[sim_z]
                temp_list.append((n, sim_zx))
                descendants[sim_z] = temp_list.copy()
            else:
                descendants[sim_z] = [(n, sim_zx)]  # adds sim_z: [(n, sim_zx)] to the dictionary
        except Exception as e:
            riv_log(f'get_descendants error: {e}')
    return descendants  # dictionary of sim_z: [(n, sim_zx), ...] for sim_z descendant, n gens forward, via sim_zx


# the above as a console command. redundant except for debugging
@sims4.commands.Command('riv_get_descendants', command_type=sims4.commands.CommandType.Live)
def console_get_descendants(sim_x: SimInfoParam, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    x_descendants = get_descendants(sim_x)
    if not x_descendants:
        output('{}\'s descendants not found'.format(sim_x.first_name))
    else:
        for sim_y in x_descendants.keys():
            for sim_z in x_descendants[sim_y]:
                output('{} {} is {} {}\'s descendant, {} generations forward'.format(sim_y.first_name, sim_y.last_name,
                                                                                     sim_x.first_name, sim_x.last_name,
                                                                                     sim_z[0]))


# input: two sims and ancestors. output: [] if there is no direct relation, generational difference if there is
def get_direct_rel(sim_x, sim_y, x_ancestors, y_ancestors):
    xy_direct_rels = []

    if riv_sim_list.sims:
        sim_x = get_rivsim_from_sim(sim_x)
        sim_y = get_rivsim_from_sim(sim_y)

    if not (sim_x is None or sim_y is None):
        if sim_x.sim_id == sim_y.sim_id:  # same sim
            riv_log(sim_x.sim_id + ' ' + sim_y.sim_id)
            xy_direct_rels.append(0)
        if sim_y in x_ancestors.keys():  # sim_y is a direct ancestor of sim_x
            for sim_z in x_ancestors[sim_y]:
                xy_direct_rels.append(sim_z[0])  # gets each n from {sim_y: [sim_z = (n, sim_yx), (n, sim_yx), ...]}
        if sim_x in y_ancestors.keys():  # sim_x is a direct ancestor of sim_y
            for sim_z in y_ancestors[sim_x]:
                xy_direct_rels.append(-sim_z[0])  # gets each -n from {sim_x: [sim_z = (n, sim_xy), (n, sim_xy), ...]}

        riv_log(f'[get direct rel {sim_x.first_name} {sim_y.first_name}] {xy_direct_rels}', 3)

    # order the rels by magnitude
    xy_direct_rels.sort(key=abs)

    return xy_direct_rels


# ... -1 => sim_x child of sim_y, 0 => sim_x is sim_y, 1 => sim_x parent of sim_y, ...

# input: two sims. output: [] if there is no direct relation, generational difference if there is
def get_direct_relation(sim_x: SimInfoParam, sim_y: SimInfoParam):
    return get_direct_rel(sim_x, sim_y, get_ancestors(sim_x), get_ancestors(sim_y))


# input: a number and sim_x's gender. output: sim_x's relation to sim_y
# gens = xy_direct_rels
# gender bit is for compatibility with inlaw rels
def format_direct_rel_gender(gens: List, gender: int):
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

    riv_log(f'[format direct rel] {gens_str}', 3)

    return gens_str


def format_direct_rel(gens: List, sim_x: SimInfoParam):
    return format_direct_rel_gender(gens, sim_x.is_female)


# direct relation as a console command
@sims4.commands.Command('riv_get_direct_rel', command_type=sims4.commands.CommandType.Live)
def console_get_direct_rel(sim_x: SimInfoParam, sim_y: SimInfoParam, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    if sim_x is not None:
        if sim_y is not None:
            xy_direct_rels = get_direct_relation(sim_x, sim_y)
            if not xy_direct_rels:  # there is no direct relation, list is empty
                output('no direct rel found between {} and {}'.format(sim_x.first_name, sim_y.first_name))
            else:
                xy_direct_rel_str = format_direct_rel(xy_direct_rels, sim_x)
                for xy_rel in xy_direct_rel_str:
                    output('{} {} is {} {}\'s {}.'.format(sim_x.first_name, sim_x.last_name, sim_y.first_name,
                                                          sim_y.last_name, xy_rel))


# input: two sims. output: the strength of their siblinghood
# 0 if not sibs, 0.5 if half-sibs, 1 if full sibs (or undetermined bc parents don't exist)
def get_sib_strength(sim_x: SimInfoParam, sim_y: SimInfoParam):
    x_parents = get_parents(sim_x)
    y_parents = get_parents(sim_y)
    z_parents = [value for value in x_parents if value in y_parents]  # intersection of list
    if riv_sim_list.sims:  # if using riv_sim_list
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
        return 0


# the above as a console command
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
        output(f'something went wrong: sib_strength is {sib_strength} when it should be 0, 0.5, or 1')


# input: two sims and ancestors. output: None if there is no indirect relation, list if there is
def get_indirect_rel(sim_x: SimInfoParam, sim_y: SimInfoParam, x_ancestors: Dict, y_ancestors: Dict):
    xy_indirect_rels = []  # will be the output

    if riv_sim_list.sims:
        sim_x = get_rivsim_from_sim(sim_x)
        sim_y = get_rivsim_from_sim(sim_y)

    if not (sim_x is None or sim_y is None):
        # list is empty if it's the same sim
        if sim_x == sim_y:
            return []

        xy_ancestors = [get_rivsim_from_sim(value) for value in x_ancestors.keys() if
                        value in y_ancestors.keys()]  # intersection of list

        # get list of shared ancestors [(sim_z, nx, ny, sim_zx, sim_zy)]
        # where sim_zx =/= sim_zy are siblings, children of sim_z, ancestors of x,y resp; nx, ny gens back
        xy_rels = []  # dumps all shared ancestors with needed info
        for sim_z in xy_ancestors:  # {sim_z: [(n, sim_zx),...],...}
            for sim_xz in x_ancestors[sim_z]:  # x_ancestors[sim_z] = [sim_xz,...], sim_xz = (n, sim_zx)
                for sim_yz in y_ancestors[sim_z]:
                    nx = sim_xz[0]
                    ny = sim_yz[0]
                    sim_zx = sim_xz[1]
                    sim_zy = sim_yz[1]
                    if not sim_zx == sim_zy:
                        xy_rels.append((sim_z, nx, ny, sim_zx, sim_zy))

        # case handling siblings where both parents exist
        to_remove = []  # to be removed from xy_rels
        for rel_one in xy_rels:
            for rel_two in xy_rels:
                if not rel_one[0] == rel_two[0]:
                    if rel_one[1:] == rel_two[1:]:  # i.e. (nx, ny, sim_zx, sim_zy) is the same
                        # this indicates these are the parents
                        if rel_one[0].sim_id < rel_two[0].sim_id:
                            # ensures we don't have (sim1, sim2,...), (sim2, sim1,...) for parents
                            to_add = (rel_one[0], rel_two[0], rel_one[1], rel_one[2], 1)
                            if to_add not in xy_indirect_rels:  # removes duplicates
                                xy_indirect_rels.append(to_add)
                                if rel_one not in to_remove:
                                    to_remove.append(rel_one)
                                if rel_two not in to_remove:
                                    to_remove.append(rel_two)

        # remove rels handled above
        for rel in to_remove:
            if rel in xy_rels:
                xy_rels.remove(rel)

        # case handling the ones that are from one shared parent
        for rel in xy_rels:
            to_add = (rel[0], rel[0], rel[1], rel[2], get_sib_strength(rel[3], rel[4]))
            if to_add not in xy_indirect_rels:
                xy_indirect_rels.append(to_add)

        # case handling filled gaps by indirect relations
        # i.e. there exists a close indirect relation between sim_xx and sim_yy where
        # sim_xx is an ancestor of only sim_x
        # sim_yy is an ancestor of only sim_y
        # sim_xx has no parent who is an ancestor of sim_x and sim_y

        xx = []  # list of sims who are x or ancestors of x and not y
        yy = []  # list of sims who are y or ancestors of y and not x
        x_ancestors[sim_x] = [(0, sim_x)]  # here it helps to have the sim's self
        y_ancestors[sim_y] = [(0, sim_y)]  # trust me it'll be useful later
        for sim_xx in x_ancestors.keys():
            if sim_xx not in y_ancestors.keys():
                xx.append(get_sim_from_rivsim(sim_xx))
        for sim_yy in y_ancestors.keys():
            if sim_yy not in x_ancestors.keys():
                yy.append(get_sim_from_rivsim(sim_yy))

        # remove nones
        # ancestors of only x, as sims
        xx = [sim for sim in xx if sim is not None]
        # ancestors of only y, as sims
        yy = [sim for sim in yy if sim is not None]

        # x (has an ancestor who) is a close indirect relative of y('s ancestor), but these share no ancestor who is an
        # ancestor of x AND y changed from elifs bc some rels are gross af

        #   sim_x.relationship_tracker.has_bit(sim_y.sim_id, relname_relbit) <=> sim_y is the relname of sim_x

        # todo: FOR FUCK SAKE
        manager = services.get_instance_manager(Types.RELATIONSHIP_BIT)
        sibling_relbit = manager.get(0x2262)
        cousin_relbit = manager.get(0x227A)
        pibling_relbit = manager.get(0x227D)
        nibling_relbit = manager.get(0x2705)
        for sim_xx in xx:
            for sim_yy in yy:
                try:
                    # sim_xx and sim_yy siblings, with no parent who is an ancestor of x and y
                    if sim_xx.relationship_tracker.has_bit(int(sim_yy.sim_id), sibling_relbit):
                        # get parents of sim_xx or sim_yy that are ancestors of x and y
                        xx_parents = [p for p in get_parents(sim_xx) if p in xy_ancestors]
                        yy_parents = [p for p in get_parents(sim_yy) if p in xy_ancestors]

                        #riv_log(f'relation stitching for siblings {sim_x.first_name} and {sim_y.first_name}:', 3)
                        #riv_log(xx_parents, 3)
                        #riv_log(yy_parents, 3)
                        #riv_log([p for p in xx_parents if p in yy_parents], 3)

                        # get parents of sim_xx AND sim_yy that are ancestors of x and y
                        if not [p for p in xx_parents if p in yy_parents]:
                            # convert back to rivsims
                            rivsim_xx = get_rivsim_from_sim(sim_xx)
                            rivsim_yy = get_rivsim_from_sim(sim_yy)
                            # sim_xx and sim_yy have no parents that are ancestors of sim_x and sim_y
                            #   => rels via xx and yy have not been added yet
                            for sim_xz in x_ancestors[rivsim_xx]:
                                # x_ancestors[sim_xx] = [sim_xz,...], sim_xz = (n, sim)
                                # where sim_xx is n gens back from sim_x via sim
                                for sim_yz in y_ancestors[rivsim_yy]:
                                    # y_ancestors[sim_yy] = [sim_yz,...], sim_yz = (n, sim)
                                    # where sim_yy is n gens back from sim_x via sim
                                    nx = sim_xz[0]
                                    ny = sim_yz[0]
                                    to_add = (rivsim_xx, rivsim_yy, nx + 1, ny + 1, get_sib_strength(sim_xx, sim_yy))
                                    # connections are sibs (sharing parents), so gen + 1
                                    if to_add not in xy_indirect_rels:
                                        xy_indirect_rels.append(to_add)
                except Exception as e:
                    riv_log('error with siblings ' + sim_xx.first_name + ' and ' + sim_yy.first_name + ': ' + str(e))

                try:
                    # sim_yy pibling of sim_xx, and there are no siblings to check
                    if sim_xx.relationship_tracker.has_bit(int(sim_yy.sim_id), pibling_relbit):
                        for sim_xxx in get_parents(sim_xx):
                            sim_xxx = get_sim_from_rivsim(sim_xxx)
                            if sim_xxx is not None:
                                if sim_xxx.relationship_tracker.has_bit(int(sim_yy.sim_id), sibling_relbit):
                                    # this case will already by covered by sib case, using yy's parent = xx's sib
                                    break
                        else:
                            # convert back to rivsims
                            rivsim_xx = get_rivsim_from_sim(sim_xx)
                            rivsim_yy = get_rivsim_from_sim(sim_yy)
                            for sim_xz in x_ancestors[rivsim_xx]:
                                # x_ancestors[sim_xx] = [sim_xz,...], sim_xz = (n, sim)
                                # where sim_xx is n gens back from sim_x via sim
                                for sim_yz in y_ancestors[rivsim_yy]:
                                    # y_ancestors[sim_yy] = [sim_yz,...], sim_yz = (n, sim)
                                    # where sim_yy is n gens back from sim_x via sim
                                    nx = sim_xz[0]
                                    ny = sim_yz[0]
                                    to_add = (rivsim_xx, rivsim_yy, nx + 2, ny + 1, 1)
                                    # connections are nibling + pibling, so an extra 2, 1 to joining point.
                                    # assume missing parent of xx is yy's full sib
                                    if to_add not in xy_indirect_rels:
                                        xy_indirect_rels.append(to_add)
                except Exception as e:
                    riv_log(
                        'error with pibling/nibling ' + sim_xx.first_name + ' and ' + sim_yy.first_name + ': ' + str(e))

                try:
                    # sim_yy nibling of sim_xx, and there are no siblings to check
                    if sim_xx.relationship_tracker.has_bit(int(sim_yy.sim_id), nibling_relbit):
                        for sim_yyy in get_parents(sim_yy):
                            sim_yyy = get_sim_from_rivsim(sim_yyy)
                            if sim_yyy is not None:
                                if sim_yyy.relationship_tracker.has_bit(int(sim_xx.sim_id), sibling_relbit):
                                    # this case will already by covered by sib case, using xx's parent = yy's sib
                                    break
                        else:
                            # convert back to rivsims
                            rivsim_xx = get_rivsim_from_sim(sim_xx)
                            rivsim_yy = get_rivsim_from_sim(sim_yy)
                            for sim_xz in x_ancestors[rivsim_xx]:
                                # x_ancestors[sim_xx] = [sim_xz,...], sim_xz = (n, sim)
                                # where sim_xx is n gens back from sim_x via sim
                                for sim_yz in y_ancestors[rivsim_yy]:
                                    # y_ancestors[sim_yy] = [sim_yz,...], sim_yz = (n, sim)
                                    # where sim_yy is n gens back from sim_x via sim
                                    nx = sim_xz[0]
                                    ny = sim_yz[0]
                                    to_add = (rivsim_xx, rivsim_yy, nx + 1, ny + 2, 1)
                                    # connections are pibling + nibling, so an extra 1, 2 to joining point.
                                    # assume missing parent of yy is xx's full sib
                                    if to_add not in xy_indirect_rels:
                                        xy_indirect_rels.append(to_add)
                except Exception as e:
                    riv_log(
                        'error with nibling/pibling ' + sim_xx.first_name + ' and ' + sim_yy.first_name + ': ' + str(e))

                try:
                    # sim_xx and sim_yy first cousins, and there are no siblings to check
                    # (between sim_xx+parents AND sim_yy+parents)
                    # spaghet bc i don't fkn remember which way round the pnibling rel goes, two of these are unneeded
                    if sim_xx.relationship_tracker.has_bit(int(sim_yy.sim_id), cousin_relbit):
                        xx_parents = get_parents(sim_xx)
                        yy_parents = get_parents(sim_yy)
                        for sim_xxx, sim_yyy in get_pairs_yield(xx_parents, yy_parents):
                            sim_xxx = get_sim_from_rivsim(sim_xxx)
                            sim_yyy = get_sim_from_rivsim(sim_yyy)
                            if sim_xxx is not None and sim_yyy is not None:
                                if sim_xxx.relationship_tracker.has_bit(sim_yyy.sim_id, sibling_relbit):
                                    # handled by sibling case
                                    break
                                if sim_xxx.relationship_tracker.has_bit(sim_yy.sim_id, nibling_relbit):
                                    # handled by pnibling case
                                    break
                                if sim_xx.relationship_tracker.has_bit(sim_yyy.sim_id, nibling_relbit):
                                    # handled by pnibling case
                                    break
                                if sim_yyy.relationship_tracker.has_bit(sim_xx.sim_id, nibling_relbit):
                                    # handled by pnibling case
                                    break
                                if sim_yy.relationship_tracker.has_bit(sim_xxx.sim_id, nibling_relbit):
                                    # handled by pnibling case
                                    break
                        else:  # sim_xx and sim_yy are first cousins, but have no parents who are siblings
                            # convert back to rivsims
                            rivsim_xx = get_rivsim_from_sim(sim_xx)
                            rivsim_yy = get_rivsim_from_sim(sim_yy)
                            for sim_xz in x_ancestors[rivsim_xx]:
                                # x_ancestors[sim_xx] = [sim_xz,...], sim_xz = (n, sim)
                                # where sim_xx is n gens back from sim_x via sim
                                for sim_yz in y_ancestors[rivsim_yy]:
                                    # y_ancestors[sim_yy] = [sim_yz,...], sim_yz = (n, sim)
                                    # where sim_yy is n gens back from sim_x via sim
                                    nx = sim_xz[0]
                                    ny = sim_yz[0]
                                    to_add = (rivsim_xx, rivsim_yy, nx + 2, ny + 2, 1)
                                    # connections are cousins (sharing grandparents), so gen + 2.
                                    # assume missing parents would be full sibs
                                    if to_add not in xy_indirect_rels:
                                        xy_indirect_rels.append(to_add)
                except Exception as e:
                    riv_log(
                        'error with first cousins ' + sim_xx.first_name + ' and ' + sim_yy.first_name + ': ' + str(e))

        riv_log(f'[get indirect rel {sim_x.first_name} {sim_y.first_name}] {xy_indirect_rels}', 3)

    # order the rels by magnitude
    xy_indirect_rels.sort(key=lambda irel: -irel[4] * -(2 ** (irel[2] + irel[3])))  # - to ensure ascending

    return xy_indirect_rels  # [(sim_z, sim_w, nx, ny, sib_strength)]
    # where sim_z and sim_w are parents/sibs/relations to link, sim_z = sim_w if half-
    # sim_x and sim_y are connected nx and ny gens back respectively, via sim_z and sim_w


# input: two sims. output: None if there is no indirect relation, list if there is
def get_indirect_relation(sim_x: SimInfoParam, sim_y: SimInfoParam):
    return get_indirect_rel(sim_x, sim_y, get_ancestors(sim_x), get_ancestors(sim_y))


# input: list of indirect rels and sim_x's gender. output: formatted version
# nb. expected list is the output from get_indirect_rel: [(sim_z, sim_w, nx, ny, sib_strength),...]
# the gender bit is for making in-law stuff easier
def format_indirect_rel_gender(xy_indirect_rels: List, gender: int):
    rels_via = []
    for boi in xy_indirect_rels:
        sim_z = boi[0]
        sim_w = boi[1]
        nx = boi[2]
        ny = boi[3]
        if nx <= 0 or ny <= 0:  # filtering out any Problems
            continue
        sib_strength = boi[4]
        nth = min([nx, ny]) - 1  # nth cousin
        nce = nx - ny  # n times removed
        rel_str = ''
        if sib_strength == 0.5:
            rel_str = 'half '
        if nth == 0:  # pibling/sibling/nibling
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
        else:  # cousin
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

    riv_log(f'[format indirect rel] {rels_via}', 3)

    return rels_via  # [(str, sim_z, sim_w)]


# the above just using sim_x's gender
def format_indirect_rel(xy_indirect_rels: List, sim_x: SimInfoParam):
    return format_indirect_rel_gender(xy_indirect_rels, sim_x.is_female)


# indirect relation as a console command
@sims4.commands.Command('riv_get_indirect_rel', command_type=sims4.commands.CommandType.Live)
def console_get_indirect_rel(sim_x: SimInfoParam, sim_y: SimInfoParam, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    rels_via = format_indirect_rel(get_indirect_relation(sim_x, sim_y), sim_x)
    # we now have a list (relation, via this person)
    if sim_x is not None:
        if sim_y is not None:
            if rels_via:
                for rel_via in rels_via:
                    if rel_via[1] == rel_via[2]:  # via one sim
                        output(
                            '{} {} is {} {}\'s {} (relation found via {} {})'.format(sim_x.first_name, sim_x.last_name,
                                                                                     sim_y.first_name, sim_y.last_name,
                                                                                     rel_via[0], rel_via[1].first_name,
                                                                                     rel_via[1].last_name))
                    else:
                        sim_z = rel_via[1]
                        sim_w = rel_via[2]  # via two sims
                        output('{} {} is {} {}\'s {} (relation found via {} {} and {} {})'.format(sim_x.first_name,
                                                                                                  sim_x.last_name,
                                                                                                  sim_y.first_name,
                                                                                                  sim_y.last_name,
                                                                                                  rel_via[0],
                                                                                                  sim_z.first_name,
                                                                                                  sim_z.last_name,
                                                                                                  sim_w.first_name,
                                                                                                  sim_w.last_name))
            else:
                output('no indirect rel found between {} and {}'.format(sim_x.first_name, sim_y.first_name))


# gets spouses ingame
def get_spouses(sim_x: SimInfoParam):

    sim_x = get_sim_from_rivsim(sim_x)
    if sim_x is None:
        return []

    manager = services.get_instance_manager(Types.RELATIONSHIP_BIT)
    spouse_relbit = manager.get(0x3DCE)
    sim_spouses = []
    for sim_y in services.sim_info_manager().get_all():
        if sim_x.relationship_tracker.has_bit(sim_y.sim_id, spouse_relbit):
            sim_spouses.append(sim_y)

    return sim_spouses


# gets inlaw relations
# NOTE this can *only* be done with sims in the game
# if sim_x or sim_y are culled then we assume they have no spouse
# if not culled, we make sure it's using the sim and not the RivSim
def get_inlaw_rel(sim_x, sim_y, x_ancestors, y_ancestors):
    x_spouse = []
    y_spouse = []
    xy_inlaw_rels = []
    # gets list of spouses for each of sim_x and sim_y
    try:
        if riv_sim_list.sims:  # if using RivSims
            # uses actual sim for spouse if needed and doable
            ssim_x_tmp = get_sim_from_rivsim(sim_x)
            ssim_y_tmp = get_sim_from_rivsim(sim_y)
            if ssim_x_tmp is not None:
                x_culled = False
            else:
                x_culled = True
            if ssim_y_tmp is not None:
                y_culled = False
            else:
                y_culled = True
        else:  # these will defo be non-culled sims
            x_culled = False
            y_culled = False

        # we now have sims in game where possible, and whether the sim has been culled
        # if the sim is culled then we just assume they have no spouse

        if not x_culled:
            x_spouse = get_spouses(sim_x)
        if not y_culled:
            y_spouse = get_spouses(sim_y)

    except Exception as e:
        riv_log(f'error in getting spouse lists ({e})')
    # check if sim_x is married to sim_y
    try:
        if sim_x in y_spouse:
            if sim_y in x_spouse:  # just checks nothing is weird
                xy_inlaw_rels.append((0,))  # the comma is needed to make this a tuple
    except Exception as e:
        riv_log(f'error in checking if sims are married ({e})')

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
                    if rel < 0:  # if x is y's spouse's ancestor (e.g. mother-in-law)
                        xy_inlaw_rels.append((1, rel, sim_x, sim_s))
            # indirect rel is a list of (sim_z, sim_w, nx, ny, sib_strength)
            temp_rels = get_indirect_rel(sim_x, sim_s, x_ancestors, s_ancestors)
            if temp_rels:
                for rel in temp_rels:
                    xy_inlaw_rels.append((2, rel, sim_x, sim_s))
    except Exception as e:
        riv_log(f'error in checking if sim_x is related to sim_y\'s spouse ({e})')
    # check if sim_y is related to sim_x's spouse
    try:
        # x is the spouse of y's relative / y is related to x's spouse (type b on site above)
        for sim_s in x_spouse:
            s_ancestors = get_ancestors(sim_s)
            # direct rel is a list of integers with generational difference
            temp_rels = get_direct_rel(sim_s, sim_y, s_ancestors, y_ancestors)
            if temp_rels:
                for rel in temp_rels:
                    if rel > 0:  # if x is the spouse of y's descendant (e.g. son-in-law)
                        xy_inlaw_rels.append((1, rel, sim_y, sim_s))
            # indirect rel is a list of (sim_z, sim_w, nx, ny, sib_strength)
            temp_rels = get_indirect_rel(sim_s, sim_y, s_ancestors, y_ancestors)
            if temp_rels:
                for rel in temp_rels:
                    xy_inlaw_rels.append((2, rel, sim_y, sim_s))
    except Exception as e:
        riv_log(f'error in checking if sim_y is related to sim_x\'s spouse ({e})')

    riv_log(f'[get inlaw rel {sim_x.first_name} {sim_y.first_name}] {xy_inlaw_rels}', 3)

    return xy_inlaw_rels
    # list [(0), (1, drel, sim_t, sim_s), (2, irel, sim_t, sim_s)] where
    # sim_s is the spouse of sim_t = sim_x or sim_y
    # drel = n describing the direct-in-law relationship between sim_x and sim_y
    # irel = (sim_z, sim_w, nx, ny, sib_strength) describing the indirect-in-law relationship


def get_inlaw_relation(sim_x: SimInfoParam, sim_y: SimInfoParam):
    return get_inlaw_rel(sim_x, sim_y, get_ancestors(sim_x), get_ancestors(sim_y))


def format_inlaw_rel(xy_inlaw_rels: List, sim_x: SimInfoParam):
    inlaw_rels = []  # this will have the strings and via
    for rel in xy_inlaw_rels:
        try:
            if rel[0] == 0:  # spouse
                try:
                    if sim_x.is_female:
                        inlaw_rels.append(('wife', 0))
                    else:
                        inlaw_rels.append(('husband', 0))
                except Exception as e:
                    riv_log(f'error in adding/appending spouse relation ({e})')
            elif rel[0] == 1:  # direct-rel-in-law
                try:
                    for drel in format_direct_rel_gender([rel[1]], sim_x.is_female):  # = [str,...]
                        try:
                            inlaw_rels.append((drel + ' in law', rel[3]))
                        except Exception as e:
                            riv_log(f'error in appending direct-rel-in-law ({e})')
                except Exception as e:
                    riv_log(f'error in adding direct-rel-in-law ({e})')
            elif rel[0] == 2:  # indirect rel-in-law
                try:
                    for irel in format_indirect_rel_gender([rel[1]], sim_x.is_female):  # = [(str, sim_z, sim_w),...]
                        try:
                            inlaw_rels.append((irel[0] + ' in law', rel[3]))
                        except Exception as e:
                            riv_log(f'error in appending indirect-rel-in-law ({e})')
                except Exception as e:
                    riv_log(f'error in adding indirect-rel-in-law ({e})')
            elif rel[0] == -1:  # error
                inlaw_rels.append((rel[1], 1))
        except Exception as e:
            riv_log(f'error in formatting inlaw rels ({e})')

    riv_log(f'[format inlaw rel] {inlaw_rels}', 3)

    return inlaw_rels  # [(string, sim)] where sim is the spouse related to sim_x or sim_y, or is 0 if spouse


# gets step relations #
# make sure it's using the sim and not the RivSim
def get_step_rel(sim_x, sim_y, x_ancestors_tmp, y_ancestors_tmp):
    get_step_rel_tic = time.perf_counter()
    riv_log(f'finding step rels between {sim_x.first_name} and {sim_y.first_name}...')

    # test for married sims:
    # sim_z.spouse_sim_id is not None
    manager = services.get_instance_manager(Types.RELATIONSHIP_BIT)

    x_ancestors = {}
    x_list_ingame = rivsims_to_sims(x_ancestors_tmp.keys())
    riv_log(f'number of ingame ancestors of {sim_x.first_name}: {len(x_list_ingame)}')
    for rivsim_z in x_ancestors.keys():
        sim_z = get_sim_from_rivsim(rivsim_z)
        if sim_z in x_list_ingame:
            x_ancestors[sim_z] = x_ancestors_tmp[rivsim_z]
    del x_list_ingame
    sim_x = get_sim_from_rivsim(sim_x)

    y_ancestors = {}
    y_list_ingame = rivsims_to_sims(y_ancestors_tmp.keys())
    riv_log(f'number of ingame ancestors of {sim_y.first_name}: {len(y_list_ingame)}')
    for rivsim_z in y_ancestors.keys():
        sim_z = get_sim_from_rivsim(rivsim_z)
        if sim_z in y_list_ingame:
            y_ancestors[sim_z] = y_ancestors_tmp[rivsim_z]
    del y_list_ingame
    sim_y = get_sim_from_rivsim(sim_y)

    x_step_y = []

    # check step-parent / step-child
    try:
        # sim_x spouse of sim_z, sim_z parent of sim_y, sim_x not parent of sim_y => sim_x step-parent of sim_y
        for sim_z in get_spouses(sim_x):
            if sim_z in get_parents_ingame(sim_y):
                if sim_x not in get_parents_ingame(sim_y):
                    x_step_y.append({'sim_xz': sim_z, 'sim_zy': sim_z, 'xzy': [((0,), 1)]})
                    riv_log('{} is the step-parent of {}'.format(sim_x.first_name, sim_y.first_name))
    except Exception as e:
        riv_log(f'error in checking if {sim_x.first_name} is the step-parent of {sim_y.first_name}: {e}')
    try:
        # sim_x child of sim_z, sim_z spouse of sim_y, sim_x not child of sim_y => sim_x step-child of sim_y
        for sim_z in get_parents_ingame(sim_x):
            if sim_z in get_spouses(sim_y):
                if sim_x not in get_children_ingame(sim_y):
                    x_step_y.append({'sim_xz': sim_z, 'sim_zy': sim_z, 'xzy': [(-1, (0,))]})
                    riv_log(f'{sim_x.first_name} is the step-child of {sim_y.first_name}')
    except Exception as e:
        riv_log(f'error in checking if {sim_x.first_name} is the step-child of {sim_y.first_name}: {e}')

    # get all married relatives of sim_x and sim_y
    x_rels = {}  # rels x to z
    num_xz = 0
    y_rels = {}  # rels z to y
    num_zy = 0
    for sim_z in services.sim_info_manager().get_all():
        try:
            if sim_z.spouse_sim_id is not None and sim_z not in [sim_x, sim_y]:
                z_ancestors = get_ancestors_ingame(sim_z)
                xz = get_direct_rel(sim_x, sim_z, x_ancestors, z_ancestors) + \
                     get_indirect_rel(sim_x, sim_z, x_ancestors, z_ancestors) + \
                     get_inlaw_rel(sim_x, sim_z, x_ancestors, z_ancestors)
                zy = get_direct_rel(sim_z, sim_y, z_ancestors, y_ancestors) + \
                     get_indirect_rel(sim_z, sim_y, z_ancestors, y_ancestors) + \
                     get_inlaw_rel(sim_z, sim_y, z_ancestors, y_ancestors)
                # [n] + [(sim_z, sim_w, nx, ny, sib_strength)] + [(0), (1, drel, sim_t, sim_s), (2, irel, sim_t, sim_s)]
                #   n = 1 => sim_x parent of sim_y
                #   sim_z and sim_w are parents/sibs/relations to link, sim_z = sim_w if half-
                #   sim_x and sim_y are connected nx and ny gens back respectively, via sim_z and sim_w
                #   sim_s is the spouse of sim_t = sim_x or sim_y
                #   (0) if sim_x is sim_y's spouse
                #   drel = n describing the direct-in-law relationship between sim_x and sim_y
                #   irel = (sim_z, sim_w, nx, ny, sib_strength) describing the indirect-in-law relationship
                if xz:
                    x_rels[sim_z] = xz
                    num_xz += len(xz)
                if zy:
                    y_rels[sim_z] = zy
                    num_zy += len(zy)
        except Exception as e:
            riv_log(f'error in getting relatives of sim_x and sim_y: {e}')
    riv_log(f'number of married rels found for {sim_x.first_name}: {num_xz}')
    riv_log(f'number of married rels found for {sim_y.first_name}: {num_zy}')

    # stop here if either is 0
    if num_xz == 0 and num_zy == 0:
        get_step_rel_toc = time.perf_counter()
        riv_log(f'time taken to find step rels between {sim_x.first_name} and {sim_y.first_name} = '
                f'{get_step_rel_toc - get_step_rel_tic}')
        return []

    # check if any are married to each other
    try:
        for sim_xz in x_rels.keys():
            for sim_zy in y_rels.keys():
                if sim_xz.relationship_tracker.has_bit(sim_zy.sim_id, manager.get(0x3DCE)):
                    # we have a rel of x married to a rel of y!
                    x_step_y.append({'sim_xz': sim_xz, 'sim_zy': sim_zy,
                                     'xzy': [(a, b) for a in x_rels[sim_xz] for b in y_rels[sim_zy]]})
                    riv_log(f'found a marriage between {sim_xz.first_name} and {sim_zy.first_name}!')
        riv_log('marriages found: ' + str(len(x_step_y)))
    except Exception as e:
        riv_log(f'error in checking if any relatives are married: {e}')

    # combine the relations
    xy_step_rels = []
    for d in x_step_y:
        try:
            sim_xz = d['sim_xz']
            sim_zy = d['sim_zy']
            xzy_rels = []
            for rel_tuple in d['xzy']:
                rel_xz = rel_tuple[0]
                rel_zy = rel_tuple[1]
                if isinstance(rel_xz, int):
                    # x and xz direct rel
                    if isinstance(rel_zy, int):
                        # zy and y direct rel
                        if (rel_xz * rel_zy) > 0:  # same sign
                            # x and y step direct rel
                            # (rel_xz > 0, rel_zy > 0) x ancestor of xz, zy ancestor of y
                            # (rel_xz < 0, rel_zy < 0) x descendant of xz, zy descendant of y
                            xzy_rels.append(rel_xz + rel_zy)
                        elif rel_xz < 0 and rel_zy > 0:
                            # x and y step indirect rel
                            # (rel_xz < 0, rel_zy > 0) x descendant of xz, zy ancestor of y
                            # want output in the form of [(sim_z, sim_w, nx, ny, sib_strength)]
                            xzy_rels.append((sim_xz, sim_zy, abs(rel_xz), abs(rel_zy), 1))
                    elif isinstance(rel_zy, tuple):
                        # zy and y not direct rel
                        if isinstance(rel_zy[0], int):
                            # zy and y inlaw rel
                            # do this later
                            continue
                        elif rel_xz < 0:
                            # x descendant of xz
                            # zy and y indirect rel
                            # x and y step indirect rel
                            # rel_zy = (sim_z, sim_w, nx, ny, sib_strength)
                            xzy_rels.append((rel_zy[0], rel_zy[1], rel_zy[2] - rel_xz, rel_zy[3], rel_zy[4]))
                elif isinstance(rel_xz, tuple):
                    # x and xz not direct rel
                    if isinstance(rel_xz[0], int):
                        # x and xz inlaw rel
                        #
                        continue
                    else:
                        # x and xz indirect rel
                        if isinstance(rel_zy, int):
                            # zy and y direct rel
                            if rel_zy > 0:
                                # zy ancestor of y
                                # x and y step indirect rel
                                # rel_xz = (sim_z, sim_w, nx, ny, sib_strength)
                                xzy_rels.append((rel_xz[0], rel_xz[1], rel_xz[2], rel_xz[3] + rel_zy, rel_xz[4]))
                        else:
                            # zy and y not direct rel
                            # is there even anything here???
                            continue
            xy_step_rels.append((sim_xz, sim_zy, xzy_rels))
            riv_log('found rels: ' + str(xzy_rels))
        except Exception as e:
            riv_log(f'error in trying to create step-relation: {e}')

    get_step_rel_toc = time.perf_counter()
    riv_log(f'time taken to find step rels between {sim_x.first_name} and {sim_y.first_name} = '
            f'get_step_rel_toc - get_step_rel_tic')

    riv_log(f'[get step rel {sim_x.first_name} {sim_y.first_name}] {xy_step_rels}', 3)

    return xy_step_rels  # [(sim_xz, sim_zy, [rels if sim_xz = sim_zy])]


def get_step_relation(sim_x: SimInfoParam, sim_y: SimInfoParam):
    return get_step_rel(sim_x, sim_y, get_ancestors_ingame(sim_x), get_ancestors_ingame(sim_y))


def format_step_rel(xy_step_rels: List, sim_x: SimInfoParam):
    step_rels = []  # this will have the strings and via
    for step_rel in xy_step_rels:
        try:
            sim_xz = step_rel[0]
            sim_zy = step_rel[1]
            rel_list = step_rel[2]
            for rel in rel_list:
                try:
                    if isinstance(rel, int):
                        rel_str = format_direct_rel([rel], sim_x)[0]
                        # str from [str]
                    else:
                        rel_str = format_indirect_rel([rel], sim_x)[0][0]
                        # str from [(str, sim_z, sim_w)]
                    step_rels.append(('step ' + rel_str, sim_xz, sim_zy))
                except Exception as e:
                    riv_log(f'error in formatting step rel {rel} ({e})')
        except Exception as e:
            riv_log(f'error in formatting step rels {step_rel} ({e})')

    riv_log(f'[format step rel] {step_rels}', 3)

    return step_rels  # [(string, sim_xz, sim_zy)]


# get drel% from two sims' drels
@lru_cache(maxsize=None)
def drel_percent(x_id, y_id):
    if int(y_id) < int(x_id):
        return drel_percent(y_id, x_id)

    drels = get_direct_relation(get_rivsim_from_id(x_id), get_rivsim_from_id(y_id))
    drel_ps = [0.5 ** abs(gen) for gen in drels]
    riv_log(drel_ps, 3)
    return sum(drel_ps)


# get irel% from two sims' irels
@lru_cache(maxsize=None)
def irel_percent(x_id, y_id):
    if int(y_id) < int(x_id):
        return irel_percent(y_id, x_id)

    irels = get_indirect_relation(get_rivsim_from_id(x_id), get_rivsim_from_id(y_id))
    irel_ps = [2 * irel[4] * (0.5 ** (irel[2] + irel[3])) for irel in irels]
    riv_log(irel_ps, 3)
    return sum(irel_ps)


# calculate consanguinity for two sims
@lru_cache(maxsize=None)
def consang(sim_x: RivSim, sim_y: RivSim):
    # 100% relationship with self
    if sim_x == sim_y:
        return 1.0
    # o/w return sum of consang percentages
    return drel_percent(sim_x.sim_id, sim_y.sim_id) + irel_percent(sim_x.sim_id, sim_y.sim_id)


@sims4.commands.Command('riv_consang', command_type=sims4.commands.CommandType.Live)
def console_get_consanguinity(sim_x: SimInfoParam, sim_y: SimInfoParam, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    xy_consang = consang(sim_x, sim_y)
    output(f'consanguinity between {sim_x.first_name} and {sim_y.first_name} is {round(100 * xy_consang,5)}%')


# riv_rel interactions below
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
            snippet_tuning.value = snippet_tuning.value + (mixer_tuning,)


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
            snippet_tuning.value = snippet_tuning.value + (mixer_tuning,)


# attempt for notification:
def scumbumbo_show_notification(sim_x: SimInfoParam, sim_y: SimInfoParam, text: str):  # , title=None):
    # We need the client to get the active sim for the icon
    client = services.client_manager().get_first_client()
    localized_title = lambda **_: LocalizationHelperTuning.get_raw_text(sim_x.first_name + ' to ' + sim_y.first_name)
    # localized_text = lambda **_: _create_localized_string(0x054DDA26, text) this is {0.String}
    localized_text = lambda **_: LocalizationHelperTuning.get_raw_text(text)

    # For the primary icon we'll use the Sim's icon (a sim_info, or just the active_sim)
    primary_icon = lambda _: IconInfoData(obj_instance=sim_x)  # IF THIS BREAKS go back to client.active_sim

    # For a secondary (not normally used) icon
    # First we need to get a resource key setup for the UI to find it, then we can create the IconInfoData from that
    # using an icon_resource argument.
    # sprout_plant_icon_key = get_resource_key(0x9993999E26D6CB56, Types.PNG)
    # secondary_icon = lambda _: IconInfoData(icon_resource=sprout_plant_icon_key)

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
    notification = UiDialogNotification.TunableFactory().default(client.active_sim, text=localized_text,
                                                                 title=localized_title, icon=primary_icon,
                                                                 # secondary_icon=secondary_icon,
                                                                 urgency=urgency,
                                                                 information_level=information_level,
                                                                 visual_type=visual_type)
    notification.show_dialog()


# attempt for notification:
def scumbumbo_show_notif_texttitle(text: str, title: str):
    # We need the client to get the active sim for the icon
    client = services.client_manager().get_first_client()
    localized_title = lambda **_: LocalizationHelperTuning.get_raw_text(title)
    # localized_text = lambda **_: _create_localized_string(0x054DDA26, text) this is {0.String}
    localized_text = lambda **_: LocalizationHelperTuning.get_raw_text(text)

    sprout_plant_icon_key = get_resource_key(0x9993999E26D6CB56, Types.PNG)
    primary_icon = lambda _: IconInfoData(icon_resource=sprout_plant_icon_key)

    #   Green for defaults (urgency=DEFAULT, information_level=PLAYER, visual_type=INFORMATION)
    #   Orange for urgency = URGENT
    #   Blue for information_level = SIM
    #   Purple for visual_type = SPECIAL_MOMENT & information_level = SIM
    #   Dark "chat bubble" from Sim's icon information_level = SPEECH
    urgency = UiDialogNotification.UiDialogNotificationUrgency.DEFAULT
    information_level = UiDialogNotification.UiDialogNotificationLevel.PLAYER
    visual_type = UiDialogNotification.UiDialogNotificationVisualType.INFORMATION

    # Prepare and show the notification.  The TunableFactory() is basically allowing us to fill in the
    # blanks that normally would have been specified in a UiDialogNotification XML tuning.
    # had client.active_sim at the start??
    notification = UiDialogNotification.TunableFactory().default(client.active_sim, text=localized_text,
                                                                 title=localized_title, icon=primary_icon,
                                                                 urgency=urgency, information_level=information_level,
                                                                 visual_type=visual_type)
    notification.show_dialog()


# input: two sims and their ancestors; output: a tuple of lists with bio rels first, non-bio rels second.
# these lists have ONLY the strings and not the via part
def get_str_list(sim_x, sim_y, x_ancestors, y_ancestors, include_step_rels=global_include_step_rels):
    bio_rels_output = []
    inlaw_rels_output = []
    step_rels_output = []

    # makes list of relations
    direct_rels = get_direct_rel(sim_x, sim_y, x_ancestors, y_ancestors)
    for rel in format_direct_rel(direct_rels, sim_x):
        try:
            bio_rels_output.append(rel)
        except Exception as e:
            bio_rels_output.append(f'[direct rel error {e}]')
            riv_log(f'get_str_list; direct rel error {e}')
    indirect_rels = get_indirect_rel(sim_x, sim_y, x_ancestors, y_ancestors)
    for rel in format_indirect_rel(indirect_rels, sim_x):
        try:
            bio_rels_output.append(rel[0])
        except Exception as e:
            bio_rels_output.append(f'[indirect rel error {e}]')
            riv_log(f'get_str_list; indirect rel error {e}')
    inlaw_rels = get_inlaw_rel(sim_x, sim_y, x_ancestors, y_ancestors)
    for rel in format_inlaw_rel(inlaw_rels, sim_x):
        try:
            inlaw_rels_output.append(rel[0])
        except Exception as e:
            inlaw_rels_output.append(f'[inlaw rel error {e}]')
            riv_log(f'get_str_list; inlaw rel error {e}')
    if include_step_rels or global_include_step_rels:
        step_rels = get_step_rel(sim_x, sim_y, x_ancestors, y_ancestors)
        for rel in format_step_rel(step_rels, sim_x):
            try:
                step_rels_output.append(rel[0])
                riv_log(f'found this step rel: {rel[0]}', 3)
            except Exception as e:
                step_rels_output.append(f'[step rel error {e}]')
                riv_log(f'get_str_list; step rel error {e}')

    riv_log(f'[get str list {sim_x.first_name} {sim_y.first_name}] '
            f'{(bio_rels_output, inlaw_rels_output, step_rels_output)}', 3)

    return (bio_rels_output, inlaw_rels_output, step_rels_output)


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
    elif n == 1 and show_single == 0:  # doesn't show single when redundant
        return ''
    elif n < 10:
        return leq_ten_tuple[n] + ' '
    elif n <= 100:
        ones_bit = n % 10
        tens_bit = int((n - (n % 10)) / 10)
        # i.e. if n = ab (these are digits), ones_bit = b, tens_bit = a
        return prefix_tuple[ones_bit] + tens_tuple[tens_bit] + ' '
    else:
        return f'{n}-tuple '


# input: lists of bio_rels and inlaw_rels and step_rels as strings with repeats for multiplicity
# output: lists of bio_rels_fixed and inlaw_rels_fixed and step_rels_fixed with multiplicity in strings
def combine_str_list(bio_rels: List, inlaw_rels: List, step_rels: List):
    br_count_dict = {}  # bio rels
    ir_count_dict = {}  # inlaw rels
    sr_count_dict = {}  # step rels

    # counts the number of times each string shows up
    for rel in bio_rels:
        try:
            br_count_dict[rel] += 1  # adds 1 to multiplicity
        except:
            br_count_dict[rel] = 1
    # br_count_dict now has {rel: n} where n is the number of times rel shows up

    # do the same for ir_count_dict
    for rel in inlaw_rels:
        try:
            ir_count_dict[rel] += 1  # adds 1 to multiplicity
        except:
            ir_count_dict[rel] = 1  # sets multiplicity to 1
    # ir_count_dict now has {rel: n} where n is the number of times rel shows up

    # do the same for sr_count_dict
    for rel in step_rels:
        try:
            sr_count_dict[rel] += 1  # adds 1 to multiplicity
        except:
            sr_count_dict[rel] = 1  # sets multiplicity to 1
    # sr_count_dict now has {rel: n} where n is the number of times rel shows up

    bio_rels_fixed = []
    inlaw_rels_fixed = []
    step_rels_fixed = []
    # turns br into a list of strings
    for rel in br_count_dict.keys():  # key is the main part of the rel
        prefix = num_to_tuple(br_count_dict[rel], 0)  # prefix is the 'n-tuple' bit
        bio_rels_fixed.append(prefix + rel)
    # turns ir into a list of strings
    for rel in ir_count_dict.keys():  # key is the main part of the rel
        prefix = num_to_tuple(ir_count_dict[rel], 0)  # prefix is the 'n-tuple' bit
        inlaw_rels_fixed.append(prefix + rel)
    # turns sr into a list of strings
    for rel in sr_count_dict.keys():  # key is the main part of the rel
        prefix = num_to_tuple(sr_count_dict[rel], 0)  # prefix is the 'n-tuple' bit
        step_rels_fixed.append(prefix + rel)
    return (bio_rels_fixed, inlaw_rels_fixed, step_rels_fixed)


# input: type of string needed for the part of the notification right before "i'm your...". ends with a space
# output: string
def give_me_a_string(string_type):
    # string_types:
    # 0 = 000 = no rels
    # 1 = 001 = inlaw only
    # 2 = 010 = bio only
    # 3 = 011 = bio and inlaw
    # 4 = 100 = step only
    # 5 = 101 = step and inlaw
    # 6 = 110 = step and bio
    # 7 = 111 = step, bio, and inlaw
    strings_dict = {
        0: ['Nope, we aren\'t related.',
            'We aren\'t related at all.',
            'I\'m not related to you. What gave you that idea?'],
        1: ['I\'d hope we aren\'t related.',
            'We aren\'t related.',
            'We don\'t have any biological relation.'],
        2: ['Yeah, we\'re related.',
            'Of course we\'re related.'],
        3: ['Uh... we are related.',
            'Might as well start singing Sweet Home Appaloosa...',
            'This is a bit awkward.',
            'It\'s a little complicated...'],
        4: ['We aren\'t exactly related.',
            'Technically, we aren\'t related.',
            'We\'re only stepfamily.'],
        5: ['We aren\'t technically related.',
            'I\'m one of your in-laws, but we\'re also stepfamily.',
            'Well... we aren\'t related!'],
        6: ['We\'re related, but also stepfamily, which is... odd.',
            'Yeah, we\'re related. Everything is kinda messy though.',
            'I mean, we are related, but we\'re stepfamily too.'],
        7: ['Oh llamas, our family relationship is an absolute mess!',
            'It\'s very complicated.',
            'Bit of an odd family...']
    }
    string_list = strings_dict[string_type]
    string_output = random.choice(string_list)
    # amend these if there are strong friendship/romantic relations
    return string_output + ' '


# for the interaction
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
    try:
        x_ancestors = get_ancestors(sim_x)
        y_ancestors = get_ancestors(sim_y)
    except Exception as e:
        scumbumbo_show_notification(sim_x, sim_y, '[failed to get ancestors: ' + str(e) + ']')
        return

    # gets lists of strings for bio_rels and inlaw_rels
    rel_lists = get_str_list(sim_x, sim_y, x_ancestors, y_ancestors, global_include_step_rels)
    bio_rels = rel_lists[0]
    inlaw_rels = rel_lists[1]
    step_rels = rel_lists[2]

    # replaces these with strings that have multiplicity
    # (e.g. ['first cousin', 'first cousin'] -> {'first cousin': 2} -> ['double first cousin']
    rel_lists = combine_str_list(bio_rels, inlaw_rels, step_rels)
    bio_rels = rel_lists[0]
    inlaw_rels = rel_lists[1]
    step_rels = rel_lists[2]

    # rel_code tells you if they are bio/inlaw/step rels
    rel_code = 0
    if inlaw_rels:
        rel_code += 1
    if bio_rels:
        rel_code += 2
    if step_rels:
        rel_code += 4

    # formats the notification
    notif_text = give_me_a_string(rel_code)
    if bio_rels:
        # has bio rel
        notif_text += 'I\'m your ' + bio_rels[0]
        if len(bio_rels) == 2:  # a and b
            notif_text += ' and ' + bio_rels[1]
        elif len(bio_rels) > 2:  # a, b, c, and d
            for i in range(1, len(bio_rels) - 1):
                notif_text += ', ' + bio_rels[i]
            notif_text += ', and ' + bio_rels[len(bio_rels) - 1]
        notif_text += '. '
        if inlaw_rels + step_rels:
            # has bio and non-bio rel
            non_bio_rels = inlaw_rels + step_rels
            notif_text += 'I\'m also your ' + non_bio_rels[0]
            if len(non_bio_rels) == 2:  # a and b
                notif_text += ' and ' + non_bio_rels[1]
            elif len(non_bio_rels) > 2:  # a, b, c, and d
                for i in range(1, len(non_bio_rels) - 1):
                    notif_text += ', ' + non_bio_rels[i]
                notif_text += ', and ' + non_bio_rels[len(non_bio_rels) - 1]
            notif_text += '. '
    else:
        # no bio rel
        if inlaw_rels:
            # has inlaw rel
            notif_text += 'I\'m your ' + inlaw_rels[0]
            if len(inlaw_rels) == 2:  # a and b
                notif_text += ' and ' + inlaw_rels[1]
            elif len(inlaw_rels) > 2:  # a, b, c, and d
                for i in range(1, len(inlaw_rels) - 1):
                    notif_text += ', ' + inlaw_rels[i]
                notif_text += ', and ' + inlaw_rels[len(inlaw_rels) - 1]
            notif_text += '. '
            if step_rels:
                # has inlaw and step rel
                notif_text += 'I\'m also your ' + step_rels[0]
                if len(step_rels) == 2:  # a and b
                    notif_text += ' and ' + step_rels[1]
                elif len(step_rels) > 2:  # a, b, c, and d
                    for i in range(1, len(step_rels) - 1):
                        notif_text += ', ' + step_rels[i]
                    notif_text += ', and ' + step_rels[len(step_rels) - 1]
                notif_text += '. '
        else:
            # no inlaw rel
            if step_rels:
                # step rel
                notif_text += 'I\'m your ' + step_rels[0]
                if len(step_rels) == 2:  # a and b
                    notif_text += ' and ' + step_rels[1]
                elif len(step_rels) > 2:  # a, b, c, and d
                    for i in range(1, len(step_rels) - 1):
                        notif_text += ', ' + step_rels[i]
                    notif_text += ', and ' + step_rels[len(step_rels) - 1]
                notif_text += '. '

    try:
        # extra starting/ending strings
        manager = services.get_instance_manager(Types.RELATIONSHIP_BIT)
        if sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x3DB4)):  # friendship-despised
            if rel_code == 0:
                notif_text = 'I\'m so glad we aren\'t related.'
                scumbumbo_show_notification(sim_x, sim_y, notif_text)
                return  # bc we don't need to do anything else here
            else:
                notif_text = notif_text + ' Doesn\'t mean I want anything to do with you.'
        if sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x79EB)):  # friendship-bff_BromanticPartner
            notif_text = 'Bro... ' + notif_text
        if sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x18961)):  # relbit_Pregnancy_Birthparent
            notif_text = 'What? I gave birth to you! ' + notif_text
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x3DDF)):  # RomanticCombo_Soulmates
            if rel_code < 2:  # no rel or inlaw only
                notif_text = 'You\'re my soulmate! ' + notif_text
            elif rel_code < 8:  # bio, step, combos of bio/step/inlaw, futureproofed for codes \geq 8
                notif_text = notif_text + ' I can\'t help being deeply in love with you, though.'  # i mean, EW
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id,
                                                manager.get(0x18465)):  # romantic-Promised = engaged teens
            notif_text = 'I\'ve already promised myself to you, so it\'s a bit late to ask... ' + notif_text
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x3DC8)):  # romantic-Engaged
            notif_text = notif_text + ' ...we\'re still on for the wedding, right?'
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x3DCE)):  # romantic-Married
            notif_text = 'Ah yes, the right time to double check is after we get married. ' + notif_text
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x17B82)):  # romantic-HaveDoneWooHoo_Recently
            notif_text = 'We JUST woohooed! ' + notif_text
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x873B)):  # romantic-HaveDoneWooHoo
            notif_text = 'We\'ve woohooed, and now you\'re asking? ' + notif_text
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x27A6)):  # ShortTerm_RecentFirstKiss
            notif_text = 'We literally just had our first kiss. ' + notif_text
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x27A6)):  # had first kiss
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
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x181C4)):  # HaveBeenRomantic
            notif_text = 'We\'ve already been flirting... it\'s a little late to ask. ' + notif_text
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x1A36D)):  # relationshipbit_CoWorkers
            notif_text = 'We work together. ' + notif_text
        elif sim_x.relationship_tracker.has_bit(sim_y.sim_id, manager.get(0x3DB0)):  # friendship-acquaintances
            notif_text = 'Oh, right, you barely know me. ' + notif_text
    except Exception as e:
        riv_log('error: failed to add flavour to notif because ' + str(e))

    # add consanguinity
    if show_consang:
        notif_text = notif_text + f'\n\n[consanguinity: {round(100 * consang(sim_x, sim_y),5)}%]'

    scumbumbo_show_notification(sim_x, sim_y, notif_text)


# save/load/clean json
# FOR USE WITH CURRENTSESSION
def load_sims(file_name_extra: str):
    file_dir = Path(__file__).resolve().parent.parent
    file_name = f'riv_rel_{file_name_extra}.json'  # e.g. riv_rel_pine.json
    file_name2 = f'riv_currentsession_tmp_{file_name_extra}.json'  # e.g. riv_currentsession_tmp_pine.json
    file_path = os.path.join(file_dir, file_name)
    file_path2 = os.path.join(file_dir, file_name2)

    # https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
    if os.path.isfile(file_path2):  # if tmp file is already being used
        with open(file_path2, 'r') as json_file:  # read from this
            sims = json.load(json_file)
    else:  # tmp file hasn't been created yet
        with open(file_path, 'r') as json_file:  # read from perm file
            sims = json.load(json_file)
        if use_currentsession_files:
            riv_log('creating temporary file in load_sims for ' + file_name_extra)
            with open(file_path2, 'w') as json_file2:  # create tmp file
                json.dump(sims, json_file2)
    return sims


# sims_input is a list of sims as SimInfoParam, Dict, or RivSim (can be mixed in list)
# file_name_extra is a str that fits in the * in riv_rel_*.json
def save_sims(sims_input: List, file_name_extra: str):  # List<RivSim>
    sim_time = services.time_service().sim_now.absolute_ticks()
    file_dir = Path(__file__).resolve().parent.parent
    file_name = f'riv_rel_{file_name_extra}.json'  # e.g. riv_rel_pine.json
    file_name2 = f'riv_currentsession_tmp_{file_name_extra}.json'  # e.g. riv_currentsession_tmp_pine.json
    file_path = os.path.join(file_dir, file_name)
    file_path2 = os.path.join(file_dir, file_name2)
    sims = []  # for output; each sim is a Dict here!
    # game_sims if file does not exist
    # UPDATED file_sims + new_sims (subset of game_sims) if file does exist

    if os.path.isfile(file_path2) or not use_currentsession_files:  # update file / ingame list
        game_sims = []  # sims from the game as RivSims
        for sim in sims_input:
            if isinstance(sim, RivSim):
                game_sims.append(sim)
            else:
                game_sims.append(RivSim(sim))
        # game_sims is now a list of ingame sims as RivSims
        riv_log('number of sims in game = ' + str(len(game_sims)))
        # get sims in file as a list of rivsims

        if (use_currentsession_files or not riv_sim_list.sims) and os.path.isfile(file_path):
            file_sims = [RivSim(sim) for sim in load_sims(file_name_extra)]  # sims from the file as RivSims
        else:
            file_sims = [RivSim(sim) for sim in riv_sim_list.sims]  # sims in mem as RivSims
        # add in game sims (append if sim not in file, update if in file AND needs updating)

        # put sims that are in game and not in file in new sims list
        new_sims = []  # sims from the game that are NOT in the file
        for sim_g in game_sims:
            sim_fg = None
            # try to find sim in file
            for sim_f in file_sims:
                if str(sim_g.sim_id) == str(sim_f.sim_id):
                    sim_fg = sim_f
                    break
            if sim_fg is None:  # sim_g is in game and not in file
                new_sims.append(sim_g)
                riv_log(f'new sim: {sim_g.first_name} {sim_g.last_name} spawned {format_sim_date()}')
                if not use_currentsession_files:  # add to rivsimlist.sims
                    riv_sim_list.sims.append(RivSim(sim_g))

        # put sims in file in new file
        # update to show if sims are culled (sim in file and not in game)
        # update name and gender
        for sim_f in file_sims:  # sim is in file
            sim_g = get_sim_from_rivsim(sim_f)
            if sim_f.time <= sim_time:  # if the current time is LATER than when the sim was last updated
                if sim_g is None:  # sim is in file and not in game
                    if not sim_f.is_culled:  # and if sim isn't registered as culled
                        sim_f.cull()  # then register sim as culled
                else:  # might need updating
                    sim_f.update_info(sim_g.first_name, sim_g.last_name, sim_g.is_female, sim_time)
            sims.append(sim_f.to_dict())  # put each sim_f in the output WHETHER CULLED OR NOT

        # add new sims to end of the list
        for sim_n in new_sims:  # for sim that is in game and not in file
            sims.append(sim_n.to_dict())  # add to sims (list for file)

        riv_log(f'number of new sims = {len(new_sims)}')
        riv_log(f'number of sims in file = {len(sims)}')

    else:  # haven't got a tmp file right now, and we should have one
        if os.path.isfile(file_path):  # we have a perm file
            with open(file_path, 'r') as json_file:  # read from perm file
                temp_sims = json.load(json_file)
            riv_log('creating temporary file in save_sims for ' + file_name_extra)
            with open(file_path2, 'w') as json_file2:  # create tmp file
                json.dump(temp_sims, json_file2)
            # call this again (return is to make sure it doesn't overwrite sims with []
            return save_sims(sims_input, file_name_extra)
        else:  # new file
            game_sims = []  # sims from the game as RivSims
            for sim in sims_input:
                if isinstance(sim, RivSim):
                    game_sims.append(sim)
                else:
                    game_sims.append(RivSim(sim))
            # game_sims is now a list of ingame sims as RivSims
            riv_log(f'number of sims in game = {len(game_sims)}')
            # makes a list of sims as dict
            sims = [sim_g.to_dict() for sim_g in game_sims]

    if use_currentsession_files:
        # https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
        with open(file_path2, 'w') as json_file2:
            json.dump(sims, json_file2)

    # ensure perm file is created, or updated if not using currentsession
    if not os.path.isfile(file_path) or not use_currentsession_files:
        with open(file_path, 'w') as json_file:
            json.dump(sims, json_file)
        riv_log('created/updated perm file for sims ' + file_name_extra)

    riv_log('saved json files to ' + file_name_extra)
    # update ingame sim list
    riv_sim_list.sims = [RivSim(sim) for sim in sims]


# we want to remove duplicate sim IDs by taking the MOST RECENT version
# this cleans the tmp file, which will be committed to the main one on save!
def clean_sims(file_name_extra: str):
    dict_sims = load_sims(file_name_extra)

    # get list of RivSims, removing exact duplicates
    sims = []
    for i in range(0, len(dict_sims)):  # for i in the range
        if dict_sims[i] not in dict_sims[i + 1:]:  # if the i^th dict is not later in the list
            sims.append(RivSim(dict_sims[i]))  # then append it to the list

    # get list of sims to be removed (same sim, different times)
    to_remove = []
    for sim_x in sims:
        for sim_y in sims:
            if sim_x.sim_id == sim_y.sim_id:  # same sim
                if sim_x.time < sim_y.time:  # sim_x is earlier in time
                    if not sim_x in to_remove:  # sim_x isn't already flagged to remove
                        to_remove.append(sim_x)

    # remove these sims
    for sim in to_remove:
        sims.remove(sim)

    # un-cull
    sim_time = services.time_service().sim_now.absolute_ticks()
    for rivsim in sims:
        sim = get_sim_from_rivsim(rivsim)
        if sim is not None:  # if sim is still in game
            if rivsim.is_culled:  # and sim is recorded as culled
                if not sim_time < rivsim.time:  # and we haven't gone back in time
                    # then this sim should not be listed as culled
                    rivsim.uncull()

    # make back into dicts for json
    output_sims = []
    for sim in sims:
        output_sims.append(sim.to_dict())

    file_dir = Path(__file__).resolve().parent.parent
    file_name = f'riv_rel_{file_name_extra}.json'  # e.g. riv_rel_pine.json
    file_name2 = f'riv_currentsession_tmp_{file_name_extra}.json'  # e.g. riv_currentsession_tmp_pine.json
    file_path = os.path.join(file_dir, file_name)
    file_path2 = os.path.join(file_dir, file_name2)

    # replace info in temp file with cleaned one
    if os.path.isfile(file_path2):
        with open(file_path2, 'w') as json_file2:
            json.dump(output_sims, json_file2)

    # do we also want to remove sims with no parents from riv_relparents?
    #   NO - this can cause issues
    # we might want to remove sim IDs from riv_relparents that aren't in riv_rel


# saves parent rels as a dict { sim_id : [parent1_id, parent2_id], ... }
# does all new rels if new file
# adds in new rels if updating file, taking the union of lists where possible
def save_rels(game_sims: List, file_name_extra: str):  # List<RivSim>
    file_dir = Path(__file__).resolve().parent.parent
    file_name = f'riv_relparents_{file_name_extra}.json'  # e.g. riv_rel_pine.json
    file_name2 = f'riv_currentsession_tmpparents_{file_name_extra}.json'  # e.g. riv_currentsession_tmp_pine.json
    file_path = os.path.join(file_dir, file_name)
    file_path2 = os.path.join(file_dir, file_name2)
    rels = {}  # for output
    new_rels = {}  # contains rels from the game

    # makes a list of parent rels in the game
    for sim_x in game_sims:
        # get list of parents
        # riv_log('tmp!! - save_rels, sim ' + sim_x.first_name + ' ' + sim_x.last_name)
        parents = get_parents_ingame(sim_x)
        # get list of parent IDs
        parents_id = []
        for parent in parents:
            parents_id.append(parent.sim_id)
        # add to dict
        new_rels[str(sim_x.sim_id)] = parents_id

    if os.path.isfile(file_path2) or not use_currentsession_files:  # update file
        # only load from file if needed: either using currentsession, or no rels loaded in
        if (use_currentsession_files or not riv_rel_dict.rels) and os.path.isfile(file_path):
            json_rels = riv_rel_dict.load_rels(
                file_name_extra)  # dict where key is a sim ID, value is list of parent IDs
        else:
            json_rels = riv_rel_dict.rels
        for sim in list(set(new_rels.keys()) | set(json_rels.keys())):
            # add union of parent lists to new file. either gets list if exists, or uses empty list
            rels[sim] = list(set(json_rels.get(sim, [])) | set(new_rels.get(sim, [])))
    else:  # no tmp file and we want one
        if os.path.isfile(file_path):  # we have a perm file
            riv_log('creating temporary file in save_rels for ' + file_name_extra)
            with open(file_path, 'r') as json_file:  # read from perm file
                temp_rels = json.load(json_file)
            with open(file_path2, 'w') as json_file2:  # create tmp file
                json.dump(temp_rels, json_file2)
            # call this again
            return save_rels(game_sims, file_name_extra)
        else:  # new file
            rels = new_rels

    # ensure perm file is created, or updated if not using currentsession
    if not os.path.isfile(file_path) or not use_currentsession_files:
        with open(file_path, 'w') as json_file:
            json.dump(rels, json_file)
        riv_log('created/updated perm file for rels ' + file_name_extra)

    if use_currentsession_files:
        # https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
        with open(file_path2, 'w') as json_file2:
            json.dump(rels, json_file2)


# saves sims
@sims4.commands.Command('riv_save', command_type=sims4.commands.CommandType.Live)
def console_save_sims(file_name_extra: str, _connection=None):
    output = sims4.commands.CheatOutput(_connection)

    sim_time = services.time_service().sim_now
    abs_tick = sim_time.absolute_ticks()
    output(f'the current sim time is {sim_time}, formatted as {format_sim_date()}')
    output(f'[this number appears at the end of sims that are not culled and were added/updated this time] '
           f'abs_tick = {abs_tick}')

    save_sims(services.sim_info_manager().get_all(), file_name_extra)
    output('saved sims.')  # add debug info later
    save_rels(services.sim_info_manager().get_all(), file_name_extra)
    output(f'saved parent rels. \nif you\'re not using riv_auto, then to use these relations in riv_rel, type the '
           f'following: riv_load {file_name_extra}\n[riv_save: all done]')  # add debug info later
    # output('added details from ' + str(len(sims)) + ' sims to file ' + 'riv_rel_' + file_name_extra + '.json')


# loads sims from file, or from mem if nothing is entered
@sims4.commands.Command('riv_load', command_type=sims4.commands.CommandType.Live)
def console_load_sims(file_name_extra: str, _connection=None):
    output = sims4.commands.CheatOutput(_connection)

    try:
        riv_sim_list.load_sims(file_name_extra)
        riv_rel_dict.load_rels(file_name_extra)
        # sims = load_sims(file_name_extra)
        output(f'loaded in parent rels and {len(riv_sim_list.sims)} sim mini-infos. '
               f'\nshowing a random sim and their parents:')
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
    except Exception as e:
        output('hit error: ' + str(e))
        output('something went wrong while loading these sims and rels; '
               'please check that these files exist in the same folder as riv_rel.ts4script:')
        output(f'riv_rel_{file_name_extra}.json and riv_relparents_{file_name_extra}.json')
        output('if these files do exist then please let me (rivforthesesh / riv#4381) know; '
               'if you are able to provide your current save and/or the .json files, '
               'that would be super helpful for finding the issue')

    output('[riv_load: all done]')


# shows which RivSims are in mem
@sims4.commands.Command('riv_mem', command_type=sims4.commands.CommandType.Live)
def console_mem_sims(_connection=None):
    output = sims4.commands.CheatOutput(_connection)

    output(f'riv_sim_list = {riv_sim_list}')
    sims = riv_sim_list.sims
    if sims:
        output('showing a random sim:')
        randsim = random.choice(sims)
        output(str(randsim))
        output(str(randsim.to_dict()))
    else:
        output('use riv_load xyz to load in sim info from riv_rel_xyz.json and riv_relparents_xyz.json')

    output(f'riv_rel_dict = {riv_rel_dict}')
    rels = riv_rel_dict.rels
    if rels:
        output('showing a random sim\'s parents:')
        randsim = random.choice(sims)
        output(str(randsim))
        output(str(riv_rel_dict.rels[randsim.sim_id]))
    else:
        output('use riv_load xyz to load in sim info from riv_rel_xyz.json and riv_relparents_xyz.json')

    output('[riv_mem: all done]')


# cleans riv_rel_pine.json
@sims4.commands.Command('riv_clean', command_type=sims4.commands.CommandType.Live)
def console_clean_sims(file_name_extra: str, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    sims = load_sims(file_name_extra)
    old_n = len(sims)
    old_c = len([rsim for rsim in sims if rsim['is_culled']])  # ones that are culled
    output(f'this file contains {old_n} sim mini-infos, {old_c} of which are culled. cleaning...')
    clean_sims(file_name_extra)
    sims = load_sims(file_name_extra)
    new_n = len(sims)
    new_c = len([rsim for rsim in sims if rsim['is_culled']])  # ones that are culled
    output(f'after removing duplicates, this file contains {new_n} sim mini-infos.')
    if old_c > new_c:
        output(f'unculled {old_c - new_c} sims (please let riv know if this isn\'t the first time you\'ve '
               f'cleaned this file after the december update of this mod!)')
    if old_n < new_n:
        output('if you\'re currently using this file, please run riv_update ' + file_name_extra)
    output('[riv_clean: all done]')


# clears sims and rels from mem
@sims4.commands.Command('riv_clear', command_type=sims4.commands.CommandType.Live)
def console_clear_sims(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    riv_sim_list.clear_sims()
    riv_rel_dict.clear_rels()

    # clear tmp files
    # clear tmp files
    file_dir = Path(__file__).resolve().parent.parent
    # go through each file
    for file in os.scandir(file_dir):
        # if it is of the form 'riv_currentsession_tmp ... .json'
        if file.name.startswith('riv_currentsession_tmp') and file.name.endswith('.json'):
            os.remove(os.path.join(file_dir, file))
            riv_log('deleted ' + file.name)
            output('removed temporary file ' + file.name)

    output('[riv_clear: all done]')


# updates json files
@sims4.commands.Command('riv_update', command_type=sims4.commands.CommandType.Live)
def console_update_sims(file_name_extra: str, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    file_dir = Path(__file__).resolve().parent.parent
    file_name = f'riv_rel_{file_name_extra}.json'  # e.g. riv_rel_pine.json
    file_path = os.path.join(file_dir, file_name)
    if os.path.isfile(file_path):
        output('this file exists! loading this in')
        console_load_sims(file_name_extra, _connection)
    output('running save, clear, then load (updates sim/rel info in mem and .json file)...')
    console_save_sims(file_name_extra, _connection)
    console_clear_sims(_connection)
    console_load_sims(file_name_extra, _connection)
    output('[riv_update: all done]')


# CFG fixing to defaults:
#     file_name_extra='default_asdfghjkl',
#     auto_update_json='True',
#     include_step_rels='False',
#     advanced_use_currentsession_files='False',
# always put this in a try clause!
def fix_cfg_settings():
    config_dir = Path(__file__).resolve().parent.parent
    config_name = 'riv_rel - individual save settings.cfg'
    file_path = os.path.join(config_dir, config_name)
    config = configparser.ConfigParser()
    if os.path.isfile(file_path):
        config.read_file(open(file_path, 'r'))

    for slot_id in config.sections():
        # for a given save ID
        keys = []
        for (key, val) in config.items(slot_id):
            if key not in keys:
                keys.append(key)
        # keys has the list of all keys in the cfg file for this slot ID
        for key in list(cfg_default_vals.keys()) + keys:
            # add default values for all keys that don't exist
            if key not in keys:
                val = cfg_default_vals[key]
                config[slot_id][key] = val
                riv_log(f'set {key} for save {slot_id} to default value {val}')
            # remove keys that shouldn't be there
            elif key not in cfg_default_vals.keys():
                del config[slot_id][key]
                riv_log(f'removed invalid key {key} from settings for save {slot_id}')

    # update cfg file
    with open(file_path, 'w') as cfg_file:
        config.write(cfg_file)


# AUTOMATIC JSON UPDATES - zone load, save, birth, cull

# load in settings for this save
def load_cfg_settings(attempt_number=1):
    # grab globals
    # search_if_updating_settings
    global hex_slot_id
    global file_name_extra
    global riv_auto_enabled
    global global_include_step_rels
    global use_currentsession_files
    # config stuff
    config_dir = Path(__file__).resolve().parent.parent
    config_name = 'riv_rel - individual save settings.cfg'
    file_path = os.path.join(config_dir, config_name)
    config = configparser.ConfigParser()
    # only do this if cfg exists
    if os.path.isfile(file_path):
        config.read_file(open(file_path, 'r'))
        # see if slot ID is in sections
        if hex_slot_id in config.sections():
            try:  # have to have this within 'try' or it throws an error when not in .cfg
                # search_if_updating_settings
                file_name_extra = config.get(hex_slot_id, 'file_name_extra')
                riv_log(f'loading in cfg settings: {hex_slot_id} {file_name_extra}')

                riv_auto_enabled = config.getboolean(hex_slot_id, 'auto_update_json')
                riv_log(f'auto_update_json set to {riv_auto_enabled}')
                if riv_auto_enabled:
                    riv_log('json updates enabled')
                else:
                    riv_log('json updates disabled')

                try:
                    global_include_step_rels = config.getboolean(hex_slot_id, 'include_step_rels')
                    if global_include_step_rels:
                        riv_log('including step rels')
                    else:
                        riv_log('excluding step rels')
                except:
                    pass

                use_currentsession_files = config.getboolean(hex_slot_id, 'advanced_use_currentsession_files')
                if use_currentsession_files:
                    riv_log('using currentsession files')
                else:
                    riv_log('not using currentsession files')

                # riv_log(str(config[hex_slot_id])) # <Section: 0000000e>
            except Exception as e1:
                if attempt_number == 1:
                    try:
                        riv_log('some keys were missing in the cfg. fixing file...')
                        fix_cfg_settings()
                    except Exception as e2:
                        riv_log('error in fixing cfg settings: ' + str(e2))
                    return load_cfg_settings(2)  # return just to make sure attempt 1 ends here
                else:
                    riv_log('error in loading cfg settings: ' + str(e1))
        else:
            riv_log(f'no cfg settings for save {hex_slot_id}')
            # search_if_updating_settings
            file_name_extra = ''

            riv_auto_enabled = False
            riv_log('json updates disabled')

            try:
                global_include_step_rels = true_false(cfg_default_vals['include_step_rels'])
            except:
                global_include_step_rels = False

            if global_include_step_rels:
                riv_log('including step rels')
            else:
                riv_log('excluding step rels')

            use_currentsession_files = true_false(cfg_default_vals['advanced_use_currentsession_files'])
            if use_currentsession_files:
                riv_log('using currentsession files')
            else:
                riv_log('not using currentsession files')

    # [header]
    # key = value
    # some other key = some other value
    # [another header]
    # key = another value

    # config.get("header", "key")  # this returns "value"
    # config.get("header", "some other key")  # this returns "some other value"
    # config.get("another header", "key")  # this returns "another value"


# the above as a console command
@sims4.commands.Command('riv_load_cfg_manually', command_type=sims4.commands.CommandType.Live)
def console_load_cfg_manually(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    try:
        hsi = get_slot()
        if hsi not in ['00000000'] + mccc_autosaves:
            global hex_slot_id
            hex_slot_id = hsi
            load_cfg_settings()
            output(f'loaded in cfg settings for save {hex_slot_id}')
        else:
            output('currently the game thinks your save ID is 0, or your last save was an MCCC autosave - '
                   'this can be fixed by saving the game and then running this command again.')
            output('[riv_load_cfg_manually: finished with no changes made]')
            return
    except Exception as e:
        output('failed to load in cfg settings because of the below exception:')
        output(str(e))
        return
    if not file_name_extra == '':
        output(f'running riv_update {file_name_extra}...')
        console_update_sims(file_name_extra, _connection)
    else:
        output('there are no cfg settings for this save ID. '
               'run "riv_auto xyz" with whatever keyword you want in place of xyz to set this up for this save ID.')
    output('[riv_load_cfg_manually: all done]')


# automatically updates json files, with/out current session files
# if riv_auto is not enabled or file_name_extra is empty, this just makes/updates dict of sims/rels
def auto_json():
    # update list in mem and in temporary .json file if needed
    if riv_auto_enabled and not file_name_extra == '':
        sim_time = services.time_service().sim_now.absolute_ticks()

        # if we want to make current session files
        if use_currentsession_files:
            riv_log('running auto_json with currentsession files...')
            # riv_save without the console
            save_sims(services.sim_info_manager().get_all(), file_name_extra)
            save_rels(services.sim_info_manager().get_all(), file_name_extra)
            # riv_load without the console
            riv_sim_list.load_sims(file_name_extra)
            riv_rel_dict.load_rels(file_name_extra)

        # if we don't want to make CS files
        else:
            # rivsimlist or rivreldict are not loaded in
            if not riv_sim_list.sims or not riv_rel_dict.rels:
                riv_log('auto_json is loading in sims and rels...')
                # riv_load without the console
                riv_sim_list.load_sims(file_name_extra)
                riv_rel_dict.load_rels(file_name_extra)

            # rivsimlist and rivreldict are now loaded in
            riv_log('running auto_json without currentsession files...')
            # update riv_sim_list.sims
            game_sims = [RivSim(sim) for sim in services.sim_info_manager().get_all()]
            # game_sims is now a list of ingame sims as RivSims
            riv_log(f'number of sims in game = {len(game_sims)}')
            # get sims from riv_sim_list (file_sims is now the riv sim list)
            file_sims = [RivSim(sim) for sim in riv_sim_list.sims]
            new_sims = []  # sims from the game that are NOT in riv_sim_list
            # list for output
            sims = []
            # put sims that are in game and not in file in new sims list
            for sim_g in game_sims:
                sim_fg = None
                # try to find sim in file
                for sim_f in file_sims:
                    if str(sim_g.sim_id) == str(sim_f.sim_id):
                        sim_fg = sim_f
                        break
                if sim_fg is None:  # sim_g is in game and not in file
                    new_sims.append(sim_g)
                    riv_log(f'new sim: {sim_g.first_name} {sim_g.last_name} spawned {format_sim_date()}')
            # put sims in file in new file
            # update to show if sims are culled (sim in file and not in game)
            # update name and gender
            for sim_f in file_sims:  # sim is in file
                sim_g = get_sim_from_rivsim(sim_f)
                if sim_f.time <= sim_time:  # if the current time is LATER than when the sim was last updated
                    if sim_g is None:  # sim is in file and not in game
                        if not sim_f.is_culled:  # and if sim isn't registered as culled
                            sim_f.cull()  # then register sim as culled
                    else:  # might need updating
                        sim_f.update_info(sim_g.first_name, sim_g.last_name, sim_g.is_female, sim_time)
                sims.append(sim_f)  # put each sim_f in the output WHETHER CULLED OR NOT
            # add new sims to end of the list
            for sim_n in new_sims:  # for sim that is in game and not in file
                sims.append(sim_n)  # add to sims (list for file)
            # riv_log it
            riv_log('number of new sims = ' + str(len(new_sims)))
            riv_log('len(sims) = ' + str(len(sims)))
            riv_sim_list.sims = sims.copy()
            riv_log('updated sim list in mem')

            # update riv_rel_dict.rels
            new_rels = {}  # contains rels from the game
            # makes a list of parent rels in the game (using game_sims from above)
            for sim_x in game_sims:
                # get list of parents
                parents = get_parents_ingame(sim_x)
                # get list of parent IDs
                parents_id = []
                for parent in parents:
                    parents_id.append(parent.sim_id)
                # add to dict
                new_rels[str(sim_x.sim_id)] = parents_id
            if new_rels:
                for sim_id in list(set(new_rels.keys()) | set(riv_rel_dict.rels.keys())):
                    # add union of parent lists to new file. either gets list if exists, or uses empty list
                    riv_rel_dict.rels[sim_id] = list(
                        set(riv_rel_dict.rels.get(sim_id, [])) | set(new_rels.get(sim_id, [])))

        riv_log('ran auto_json')
    else:
        # get rivsimlist of just ones in game
        riv_sim_list.sims = [RivSim(sim) for sim in services.sim_info_manager().get_all()]
        riv_log('set up riv sim list without json file')
        # get rivreldict of just ones in game
        for riv_sim in riv_sim_list.sims:
            parents = get_parents_ingame(riv_sim)
            riv_rel_dict.rels[riv_sim.sim_id] = [parent.sim_id for parent in parents]
        riv_log('set up riv rel dict without json file')


# enter riv_auto xyz to set up automatic .json file updates
@sims4.commands.Command('riv_auto', command_type=sims4.commands.CommandType.Live)
def console_auto_json(file_name_extra: str, _connection=None):
    output = sims4.commands.CheatOutput(_connection)

    # set current slot
    global hex_slot_id
    hex_slot_id = get_slot()

    # make sure it's not an autosave slot
    if hex_slot_id not in mccc_autosaves:
        # get file location
        file_dir = Path(__file__).resolve().parent.parent
        config_name = 'riv_rel - individual save settings.cfg'
        file_path = os.path.join(file_dir, config_name)
        config = configparser.ConfigParser()
        # we want to create or update this file.

        # grab the file
        try:
            config.read_file(open(file_path, 'r'))
        except:
            output('no .cfg file found. creating one...')

        if hex_slot_id in config.sections():  # if we already have settings for this
            output(f'updating settings for Slot_{hex_slot_id}.save to riv_rel - individual save settings.cfg...')
        else:  # we don't already have settings for this
            output(f'adding settings for Slot_{hex_slot_id}.save to riv_rel - individual save settings.cfg...')
            config[hex_slot_id] = {}

        # search_if_updating_settings
        config[hex_slot_id]['file_name_extra'] = file_name_extra
        config[hex_slot_id]['auto_update_json'] = 'True'

        with open(file_path, 'w') as cfg_file:
            config.write(cfg_file)
            riv_log(f'added/updated cfg settings: slot {hex_slot_id} with word {file_name_extra}')

        output('loading in new .cfg settings...')
        load_cfg_settings()

        # load sims before saving if this is an existing json file
        sims_file_name = f'riv_rel_{file_name_extra}.json'  # e.g. riv_rel_pine.json
        sims_file_path = os.path.join(file_dir, sims_file_name)
        if os.path.isfile(sims_file_path):
            output('loading in sims from file...')
            riv_sim_list.load_sims(file_name_extra)

        # load rels before saving if this is an existing json file
        rels_file_name = f'riv_relparents_{file_name_extra}.json'  # e.g. riv_rel_pine.json
        rels_file_path = os.path.join(file_dir, rels_file_name)
        if os.path.isfile(rels_file_path):
            output('loading in rels from file...')
            riv_rel_dict.load_rels(file_name_extra)

        output('running save, clear, clean, then load...')
        console_save_sims(file_name_extra, _connection)
        console_clear_sims(_connection)
        console_clean_sims(file_name_extra, _connection)
        console_load_sims(file_name_extra, _connection)

        output('[riv_auto: all done]')
    else:  # this is an autosave slot
        output('the current game slot is an MCCC autosave slot')
        output('blocked riv_auto (autosave slots aren\'t specific to saves so this could cause issues)')
        output('please manually save your game to another slot and try again')


# automatically get slot
@inject_to(SimInfoManager, 'on_loading_screen_animation_finished')
def get_slot_olsaf(original, self, *args, **kwargs):
    result = original(self, *args, **kwargs)
    # get slot
    try:
        hsi = get_slot()
        if not hsi in ['00000000'] + mccc_autosaves:
            global hex_slot_id
            hex_slot_id = hsi
        else:
            riv_log(f'didn\'t change save ID in get_slot_olsaf to {hsi}')
    except Exception as e:
        riv_log(f'error in get_slot_olsaf in on_loading_screen_animation_finished: {e}')
        raise Exception(f'(riv) error in get_slot_olsaf in on_loading_screen_animation_finished: {e}')
    return result


# when going into live mode
# also covers sims created in CAS
@inject_to(SimInfoManager, 'on_all_households_and_sim_infos_loaded')
def auto_json_oahasil(original, self, client):
    result = original(self, client)
    # set slot id
    try:
        global jsyk_ownfolder
        global hex_slot_id
        # gets old slot id
        old_hsi = hex_slot_id
        hsi = get_slot()
        # replace if this is not 0
        if hsi not in ['00000000'] + mccc_autosaves:
            hex_slot_id = hsi
            riv_log(f'save ID replaced by {hex_slot_id}')
        else:
            riv_log(f'save ID not loaded in, as it was {hsi}')
            if (not riv_sim_list.sims) and riv_auto_enabled:  # if there are no sims loaded in, but there should be
                scumbumbo_show_notif_texttitle(
                    'failed to load in sims for this save ID: this usually happens when you\'ve just left CAS, '
                    'you quit a different save without saving and then loaded this one, or you moved/deleted the '
                    '.json files. \nif you have not (or aren\'t about to) set up auto .json file updates for this '
                    'save ID please ignore this notification. \notherwise, please save your game and then enter the '
                    'following into the command line (CTRL+SHIFT+C): \n\nriv_load_cfg_manually',
                    'riv_rel issue')
        # clears sims + rels if id changes
        # clears tmp files if id was 0
        if old_hsi != hex_slot_id:
            if old_hsi not in ['00000000'] + mccc_autosaves:
                # riv_clear without the console
                riv_sim_list.clear_sims()
                riv_rel_dict.clear_rels()
                riv_log('cleared sims and rels (parents and spouses)')
            else:
                # clear tmp files
                if old_hsi == '00000000':
                    file_dir = Path(__file__).resolve().parent.parent
                    # go through each file
                    for file in os.scandir(file_dir):
                        # if it isn't one of mine
                        if not file.name.startswith('riv'):
                            jsyk_ownfolder = True
                        # if it is of the form 'riv_currentsession_tmp ... .json'
                        if file.name.startswith('riv_currentsession_tmp') and file.name.endswith('.json'):
                            os.remove(os.path.join(file_dir, file))
                            riv_log('deleted ' + file.name)

    except Exception as e:
        riv_log(f'error in getting the slot ID in on_all_households_and_sim_infos_loaded: {e}')
        raise Exception(f'(riv) error in getting the slot ID in on_all_households_and_sim_infos_loaded: {e}')
    try:
        load_cfg_settings()
    except Exception as e:
        riv_log(f'error in load_cfg_settings in on_all_households_and_sim_infos_loaded: {e}')
        raise Exception(f'(riv) error in load_cfg_settings in on_all_households_and_sim_infos_loaded: {e}')
    # automatically update .json files
    try:
        auto_json()
        riv_log('ran auto_json_oahasil')

        if riv_auto_enabled and hex_slot_id not in mccc_autosaves:
            riv_log('   with riv_auto_enabled = true, slot ID is not an autosave')
            opener = f'loaded in settings from riv_rel - individual save settings.cfg for save ID ' \
                     f'{hex_slot_id} and keyword {file_name_extra}.\n\nsim mini-infos: {len(riv_sim_list.sims)}'
        elif riv_auto_enabled and hex_slot_id in mccc_autosaves:
            riv_log('   with riv_auto_enabled = true, slot ID is an autosave (ERROR)')
            scumbumbo_show_notif_texttitle('you\'ve created settings for an MCCC autosave - this won\'t work '
                                           'properly!\n\nplease save your game to another slot and set up '
                                           'riv_auto again.', 'riv_rel: auto json issue')
        elif hex_slot_id in mccc_autosaves:
            riv_log('   with riv_auto_enabled = false, slot ID is an autosave')
            opener = f'you\'ve loaded up an autosave slot! to use riv_auto backups, please save the game to another ' \
                     f'slot first (if you don\'t want to use riv_auto, you don\'t need to do this)' \
                     f'\n\nnumber of sims: {len(riv_sim_list.sims)}'
        else:
            riv_log('   with riv_auto_enabled = false, slot ID is not an autosave')
            opener = f'no sim/rel backups were found for this save - if you\'re expecting to see json file' \
                     f' backups or want to set them up, enter riv_auto xyz into the cheat console for a' \
                     f' keyword xyz!\n\nnumber of sims: {len(riv_sim_list.sims)}'

        if jsyk_ownfolder:
            ownfolder_warning = 'you have other files in the same folder as my mod - i would recommend ' \
                                'putting all files starting riv_rel in their own subfolder (i.e. in ' \
                                'Mods/riv_rel/) if you encounter any additional lag on save/load. '
        else:
            ownfolder_warning = ''
        if mccc_autosaves and riv_auto_enabled:
            mccc_autosaves_str = f'\n\nfound MCCC autosave slots (my mod will continue to see the save slot' \
                                 f' as {hex_slot_id} if the actual save slot changes to one of these):' \
                                 f' {mccc_autosaves}'
        else:
            mccc_autosaves_str = ''
        if addons['computer']:
            computer_str = '\n\nyou can see more information and help in the "Research on riv_rel.sim" menu ' \
                           'on the computer'
        else:
            computer_str = ''
        if addons['GT'] and not addons['traits']:
            ownfolder_warning += '\n\nyou\'ve downloaded the GT addon without the traits addon - ' \
                                 'please either download riv_rel_addon_traits or remove riv_rel_addon_GT ' \
                                 'or you may face glitches with clubs being unable to find my family traits!'

        scumbumbo_show_notif_texttitle(
            f'{opener} {mccc_autosaves_str}\n\nif this is the wrong file, run riv_clear, save your game, '
            f'and run riv_load_cfg_manually.{ownfolder_warning}{computer_str}\n\nthank you for using my mod! '
            , f'riv_rel gen {rr_gen}')

    except Exception as e:
        riv_log(f'error in auto_json in on_all_households_and_sim_infos_loaded: {e}')
        raise Exception(f'(riv) error in auto_json in on_all_households_and_sim_infos_loaded: {e}')

    return result


@inject_to(SimInfoManager, 'get_sims_for_spin_up_action')
def riv_get_sims_for_spin_up_action(original, self, action):
    result = original(self,action)
    try:
        preroll_consang_tic = time.perf_counter()
        instanced_sims = list(services.sim_info_manager().instanced_sims_gen())
        riv_log(f'number of instanced sims found: {len(instanced_sims)}')
        for sim_x in instanced_sims:
            for sim_y in instanced_sims:
                if sim_x.sim_id < sim_y.sim_id:
                    is_eligible_couple(sim_x.sim_id, sim_y.sim_id)
        preroll_consang_toc = time.perf_counter()
        riv_log(f'pre-rolled consanguinities of instanced sims - it took {preroll_consang_toc - preroll_consang_tic}s')
    except Exception as e:
        riv_log(f'error in pre-rolling consanguinities in get_sims_for_spin_up_action: {e}')

    return result



# when creating a new sim
# for births - this works for sim but not parent rel
# works for generated npcs!
# test for cloning
@inject_to(SimInfoManager, 'on_sim_info_created')
def auto_json_fam_osic(original, self):
    result = original(self)
    try:
        auto_json()
        riv_log('ran auto_json_osic')
    except Exception as e:
        riv_log(f'error in auto_json in on_sim_info_created: {e}')
        raise Exception(f'(riv) error in auto_json in on_sim_info_created: {e}')
    return result


# run on add parent
# sim_x has parent bit for sim_y => sim_y parent of sim_x
@inject_to(RelationshipBit, 'on_add_to_relationship')
def auto_json_fam_oatr(original, self, sim, target_sim_info, relationship, from_load):
    result = original(self, sim, target_sim_info, relationship, from_load)
    try:
        manager = services.get_instance_manager(Types.RELATIONSHIP_BIT)
        parent_relbit = manager.get(0x2269)
        #     @classmethod
        #     def matches_bit(cls, bit_type):
        #         return cls is bit_type
        if self.matches_bit(parent_relbit):  # if a parent relbit has been added
            riv_log('a parent relbit was identified in on_add_to_relationship')
            auto_json()  # then update the json files
            # nb. should have already returned if it was an object rel
    except Exception as e:
        riv_log(f'error in auto_json in on_add_to_relationship: {e}')
        raise Exception(f'(riv) error in auto_json in on_add_to_relationship: {e}')
    return result


# AUTOMATIC UPDATE PERM .JSON ON SAVE
# doing this with PersistenceService's save_game_gen fucks up everything with all errors passing silently
@inject_to(PersistenceService, 'save_using')
def auto_json_del_tmp_su(original, self, *args, **kwargs):
    result = original(self, *args, **kwargs)
    try:
        if riv_auto_enabled:
            # update .json files
            auto_json()
        # get dir and file names
        if not file_name_extra == '':
            file_dir = Path(__file__).resolve().parent.parent
            if use_currentsession_files:  # copy tmp over to perm files
                for file in os.scandir(file_dir):
                    # if it is of the form 'riv_currentsession_tmp ... .json'
                    if file.name.startswith('riv_currentsession_tmp') and file.name.endswith('.json'):
                        temp_file_name = file.name
                        perm_file_name = temp_file_name.replace('currentsession_tmp', 'rel')
                        # could be riv_rel_ or riv_relparents_
                        # read from tmp, write to perm
                        with open(os.path.join(file_dir, temp_file_name), 'r') as json_file:  # read from tmp file
                            temp_contents = json.load(json_file)
                        with open(os.path.join(file_dir, perm_file_name), 'w') as json_file:  # add to perm file
                            json.dump(temp_contents, json_file)
                        riv_log('written to ' + perm_file_name)
                        os.remove(os.path.join(file_dir, temp_file_name))
                        riv_log('removed file ' + temp_file_name)
            else:
                # riv_save without the console, save to perm
                save_sims(services.sim_info_manager().get_all(), file_name_extra)
                save_rels(services.sim_info_manager().get_all(), file_name_extra)
    except Exception as e:
        riv_log(f'error in auto_json_del_tmp_su in save_using: {e}')
        raise Exception(f'(riv) error in auto_json_del_tmp_su in save_using: {e}')
    finally:
        riv_log('')  # just to have a line break between saves
    return result


# tmp files are deleted when save slot ID changes from 0 to not 0

# @inject_to(RelationshipTracker, 'add_relationship_bit')
# def auto_json_addrelbit(original, self, target_sim_id, bit_to_add, force_add, from_load, send_rel_change_event, allow_readdition):
#    original(self, target_sim_id, bit_to_add, force_add, from_load, send_rel_change_event, allow_readdition)

# not working
# on_loading_screen_animation_finished in SimInfoManager

# unknown
# on_sim_info_created in SimInfoManager?
# __init__ in SimInfo?

# example code from frankkulak:
# @inject_to(SimInfoManager, 'on_loading_screen_animation_finished')
# def CREATORNAME_MODNAME_update_traits(original, self, *args, **kwargs):
#     result = original(self, *args, **kwargs)
#     try:
#         trait_manager = services.get_instance_manager(Types.TRAIT)
#         old_trait = trait_manager.get(123456789)
#         new_trait = trait_manager.get(12345)
#         for sim_info in services.sim_info_manager().get_all():
#             if sim_info.has_trait(old_trait):
#                 sim_info.add_trait(new_trait)
#                 sim_info.remove_trait(old_trait)
#     except Exception as e:
#         raise Exception(f"Error with MODNAME by CREATORNAME: {str(e)}")
#     return result

# RIV_REL (and riv_rel_rand, riv_rel_all, riv_help)
# TODO: continue making these into f-strings

# gets direct, indirect, inlaw, step rel as a console command
@sims4.commands.Command('riv_rel', command_type=sims4.commands.CommandType.Live)
def riv_getrelation(sim_x: SimInfoParam, sim_y: SimInfoParam, show_if_not_related=True,
                    include_step_rels=global_include_step_rels,
                    xx_ancestors=None, yy_ancestors=None, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    if sim_x is not None and sim_y is not None:
        if sim_x == sim_y:
            main_text = '{} {} is {} {}'.format(sim_x.first_name, sim_x.last_name, sim_y.first_name,
                                                sim_y.last_name)
            output(main_text)
            riv_log(main_text, 3)
            return False  # not related to self. kinda
        else:
            if xx_ancestors is None:
                x_ancestors = get_ancestors(sim_x)
            else:
                x_ancestors = xx_ancestors
            if yy_ancestors is None:
                y_ancestors = get_ancestors(sim_y)
            else:
                y_ancestors = yy_ancestors

            # A L L
            # gets lists of strings for bio_rels and inlaw_rels and step_rels
            rrel_lists = get_str_list(sim_x, sim_y, x_ancestors, y_ancestors,
                                      include_step_rels or global_include_step_rels)
            # replaces these with strings that have multiplicity
            # e.g. ['first cousin', 'first cousin'] -> {'first cousin': 2} -> ['double first cousin']
            rel_lists = combine_str_list(rrel_lists[0], rrel_lists[1], rrel_lists[2])
            rel_list = rel_lists[0] + rel_lists[1] + rel_lists[2]
            # and then this list gets formatted
            if len(rel_list) > 0:
                main_text = sim_x.first_name + ' is ' + sim_y.first_name + '\'s ' + rel_list[0]
                if len(rel_list) == 2:  # a and b
                    main_text += ' and ' + rel_list[1]
                elif len(rel_list) > 2:  # a, b, c, and d
                    for i in range(1, len(rel_list) - 1):
                        main_text += ', ' + rel_list[i]
                    main_text += ', and ' + rel_list[len(rel_list) - 1]
                main_text += '.'
                output(main_text)
                riv_log(main_text, 3)
            else:
                main_text = sim_x.first_name + ' and ' + sim_y.first_name + ' are not related.'
                if show_if_not_related:
                    output(main_text)
                riv_log(main_text, 3)
            # return statement for counting
            return len(rel_list) > 0


# always has step rels enabled
@sims4.commands.Command('riv_rel_more_info', command_type=sims4.commands.CommandType.Live)
def riv_getrelation_moreinfo(sim_x: SimInfoParam, sim_y: SimInfoParam, include_step_rels=True, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    if sim_x is not None and sim_y is not None:
        if sim_x == sim_y:
            output('{} {} is {} {}'.format(sim_x.first_name, sim_x.last_name, sim_y.first_name, sim_y.last_name))
            output('consanguinity: 100%')
        else:
            x_ancestors = get_ancestors(sim_x)
            y_ancestors = get_ancestors(sim_y)

            # part 1: work with rivsims
            sim_x = get_rivsim_from_sim(sim_x)
            sim_y = get_rivsim_from_sim(sim_y)

            # D I R E C T
            xy_direct_rels = get_direct_rel(sim_x, sim_y, x_ancestors, y_ancestors)
            if xy_direct_rels:  # there is a direct relation, list is not empty
                xy_direct_rel_str = format_direct_rel(xy_direct_rels, sim_x)
                for xy_rel in xy_direct_rel_str:
                    try:
                        output('{} {} is {} {}\'s {}'.format(sim_x.first_name, sim_x.last_name, sim_y.first_name,
                                                             sim_y.last_name, xy_rel))
                    except Exception as e:
                        output('error in riv_rel, direct rel section: ' + str(e))

            # I N D I R E C T
            xy_indirect_rels = get_indirect_rel(sim_x, sim_y, x_ancestors, y_ancestors)
            rels_via = format_indirect_rel(xy_indirect_rels, sim_x)
            # we now have a list (relation, via this person)
            if rels_via:
                for rel_via in rels_via:
                    try:
                        if rel_via[1] == rel_via[2]:  # via one sim
                            output('{} {} is {} {}\'s {} (relation found via {} {})'.format(sim_x.first_name,
                                                                                            sim_x.last_name,
                                                                                            sim_y.first_name,
                                                                                            sim_y.last_name,
                                                                                            rel_via[0],
                                                                                            rel_via[1].first_name,
                                                                                            rel_via[1].last_name))
                        else:
                            sim_z = rel_via[1]
                            sim_w = rel_via[2]  # via two sims
                            output(
                                '{} {} is {} {}\'s {} (relation found via {} {} and {} {})'.format(sim_x.first_name,
                                                                                                   sim_x.last_name,
                                                                                                   sim_y.first_name,
                                                                                                   sim_y.last_name,
                                                                                                   rel_via[0],
                                                                                                   sim_z.first_name,
                                                                                                   sim_z.last_name,
                                                                                                   sim_w.first_name,
                                                                                                   sim_w.last_name))
                    except Exception as e:
                        output('error in riv_rel, indirect rel section: ' + str(e))

            # consanguinity
            xy_consang = consang(sim_x, sim_y)
            output(f'consanguinity: {round(100 * xy_consang,5)}%')

            # part 2: work with sims
            sim_x = get_sim_from_rivsim(sim_x)
            sim_y = get_sim_from_rivsim(sim_y)

            if sim_x is not None and sim_y is not None:
                # I N L A W
                xy_inlaw_rels = get_inlaw_rel(sim_x, sim_y, x_ancestors, y_ancestors)
                if xy_inlaw_rels:
                    # output(str(xy_inlaw_rels))
                    inlaw_str = format_inlaw_rel(xy_inlaw_rels, sim_x)
                    for rel in inlaw_str:
                        try:
                            if rel[1] == 0:  # spouse
                                output(
                                    '{} {} is {} {}\'s {}'.format(sim_x.first_name, sim_x.last_name, sim_y.first_name,
                                                                  sim_y.last_name, rel[0]))
                            elif rel[1] == 1:  # error
                                output(rel[0])
                            else:  # rel = (string, sim)
                                output('{} {} is {} {}\'s {} (relation found via {} {})'.format(sim_x.first_name,
                                                                                                sim_x.last_name,
                                                                                                sim_y.first_name,
                                                                                                sim_y.last_name, rel[0],
                                                                                                rel[1].first_name,
                                                                                                rel[1].last_name))
                        except Exception as e:
                            output('error in riv_rel, inlaw section: ' + str(e))

                # S T E P
                if include_step_rels:
                    xy_step_rels = get_step_rel(sim_x, sim_y, x_ancestors, y_ancestors)
                    if xy_step_rels:
                        step_str = format_step_rel(xy_inlaw_rels, sim_x)
                        for rel in step_str:
                            try:
                                output(
                                    '{} {} is {} {}\'s {} (relation found via {} {} and {} {})'.format(sim_x.first_name,
                                                                                                       sim_x.last_name,
                                                                                                       sim_y.first_name,
                                                                                                       sim_y.last_name,
                                                                                                       rel[0],
                                                                                                       rel[
                                                                                                           1].first_name,
                                                                                                       rel[1].last_name,
                                                                                                       rel[
                                                                                                           2].first_name,
                                                                                                       rel[
                                                                                                           2].last_name))
                            except Exception as e:
                                output('error in riv_rel, step section: ' + str(e))


# checks against random sim
@sims4.commands.Command('riv_rel_rand', command_type=sims4.commands.CommandType.Live)
def riv_getrandomrel(sim_x: SimInfoParam, include_step_rels=global_include_step_rels, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    sim_y = random.choice(list(services.sim_info_manager()._objects.values()))
    output('relation with: {} {}'.format(sim_y.first_name, sim_y.last_name))
    riv_getrelation(sim_x, sim_y, True, global_include_step_rels or include_step_rels, None, None, _connection)


# checks random sim against random sim
@sims4.commands.Command('riv_rel_rand_rand', command_type=sims4.commands.CommandType.Live)
def riv_getrandomrandomrel(include_step_rels=global_include_step_rels, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    sim_x = random.choice(list(services.sim_info_manager()._objects.values()))
    sim_y = random.choice(list(services.sim_info_manager()._objects.values()))
    output('sims: {} {} and {} {}'.format(sim_x.first_name, sim_x.last_name, sim_y.first_name, sim_y.last_name))
    riv_getrelation(sim_x, sim_y, True, global_include_step_rels or include_step_rels, None, None, _connection)


# checks against all sims in the game
# TODO: check why this says "y is x's self"
@sims4.commands.Command('riv_rel_all', command_type=sims4.commands.CommandType.Live)
def riv_getallrels(sim_y: SimInfoParam, include_step_rels=global_include_step_rels, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    yy_ancestors = get_ancestors(sim_y)
    relatives_found = 0
    for sim_x in services.sim_info_manager().get_all():
        # for sim_x in [sim_z for sim_z in riv_sim_list.sims if get_sim_from_rivsim(sim_z) is not None]:
        # don't want any output if not related
        # do it the other way round
        x_y_related = riv_getrelation(sim_x, sim_y, False, False, None, yy_ancestors, _connection)
        if x_y_related:
            relatives_found += 1
    output(str(relatives_found) + ' relatives found for ' + sim_y.first_name + '.')


# checks all sims in the game against all sims in the game
@sims4.commands.Command('riv_rel_all_all', command_type=sims4.commands.CommandType.Live)
def riv_getallallrels(include_step_rels=global_include_step_rels, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    for sim_x in services.sim_info_manager().get_all():
        # for sim_x in [sim_z for sim_z in riv_sim_list.sims if get_sim_from_rivsim(sim_z) is not None]:
        riv_getallrels(sim_x, False, _connection)
        output('')


# help
@sims4.commands.Command('riv_help', command_type=sims4.commands.CommandType.Live)
def console_help(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    if addons['GT']:
        addon_GT_text = ' (fam and inc can be used as club requirements)'
    else:
        addon_GT_text = ''
    output(
        f'riv_rel gen {rr_gen} - biological, in-law, and (optional) step relations, console commands, social '
        f'interaction, auto .json files, optional computer help menu, optional traits{addon_GT_text}, consanguinity')
    output('all settings can be edited by opening the .cfg files (in the same folder as riv_rel) in notepad++')
    output(
        'sims can be typed as firstname lastname (use "" if there is a space in the first/last name, '
        'e.g. J "Huntington III") or as the sim ID')
    output(
        'if you find an error, please send me (rivforthesesh / riv#4381) the error text and any relevant rels/files!')

    output('')

    output(
        'commands taking two sims: '
        'riv_rel, riv_rel_more_info, riv_get_sib_strength, riv_get_direct_rel, riv_get_indirect_rel, riv_show_relbits, '
        'riv_gen_diff, riv_consang, riv_is_eligible_couple')
    output(
        'commands taking one sim: '
        'riv_get_parents, riv_get_children, riv_get_ancestors, riv_get_descendants, riv_rel_all, riv_rel_rand')

    output('')

    output(
        'using .json files '
        '[replace xyz by whatever you want to create/use the files riv_rel_xyz.json and riv_relparents_xyz.json]:')
    output(
        'riv_auto xyz (runs riv_update xyz on every zone load or sim birth or save), '
        'riv_save xyz (save sim info to .json files), riv_load xyz (load sim info from .json files), '
        'riv_clean xyz (removes duplicates from .json file), riv_mem (shows no. mini sim-infos in memory), '
        'riv_clear (clears memory), '
        'riv_update xyz (runs save, clear, then load), '
        'riv_save_slot_id (shows current save ID)')
    if addons['traits']:
        output('')

        output('trait commands taking one sim, and a letter from A to H: '
               'riv_include_in_family, riv_add_to_family, riv_exclude_from_family, riv_make_heir, riv_add_founder')
        output('trait commands taking one sim: riv_traits_by_name, riv_clear_fam_sim (removes fam traits)')
        output('trait commands taking a letter from A to H: riv_traits_by_fam, riv_clear_fam, riv_show_family')
        output('trait commands taking no arguments: riv_traits, riv_clear_fam_all')
    if addons['computer']:
        output('')

        output('check the computer for a menu called "Research on riv_rel.sim..." for explanations and help.')

    output('')
    output('the help menu is a little long, please scroll up!')


# random shit for riv


# gets mean of list
def mean(list_boi: List):
    if len(list_boi) == 0:
        return None
    else:
        return sum(list_boi) / len(list_boi)


# gets generational difference between the two sims
def generational_difference(sim_x: SimInfoParam, sim_y: SimInfoParam):
    x_ancestors = get_ancestors(sim_x)
    y_ancestors = get_ancestors(sim_y)
    direct_gen_diff = get_direct_rel(sim_x, sim_y, x_ancestors, y_ancestors)
    # [n]
    # n = 1 => x one gen lower than y
    indirect_rels = get_indirect_rel(sim_x, sim_y, x_ancestors, y_ancestors)
    # [(sim_z, sim_w, nx, ny, sib_strength)]
    # nx - ny = 1 => x one gen lower than y
    indirect_gen_diff = []
    for ituple in indirect_rels:
        nx = ituple[2]
        ny = ituple[3]
        indirect_gen_diff.append(nx - ny)
    gen_diff_list = direct_gen_diff + indirect_gen_diff
    mean_gd = mean(gen_diff_list)
    if mean_gd is not None:
        gen_diff = round(mean_gd, 3)  # average rounded to 3dp
    else:
        gen_diff = None
    return (gen_diff, gen_diff_list)


@sims4.commands.Command('riv_gen_diff', command_type=sims4.commands.CommandType.Live)
def riv_getgendiff(sim_x: SimInfoParam, sim_y: SimInfoParam, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    gen_diff_tuple = generational_difference(sim_x, sim_y)
    gen_diff = gen_diff_tuple[0]
    gen_diff_list = gen_diff_tuple[1]
    output('as a list: ' + str(gen_diff_list))
    output('the average generational difference is ' + str(gen_diff))
    output('(negative means sim_x is higher up in the family tree than sim_y)')


# SaveGameData = collections.namedtuple('SaveGameData', ('slot_id', 'slot_name', 'force_override', 'auto_save_slot_id'))
# self._save_game_data_proto = serialization.SaveGameData()
# (in __init__ of PersistenceService())
# trying to get the save slot ID
@sims4.commands.Command('riv_save_slot_id', command_type=sims4.commands.CommandType.Live)
def riv_getsaveslotid(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    try:
        per = services.get_persistence_service()
    except Exception as e:
        output('failed to get persistence service because ' + str(e))
        return
    output('str(per._save_game_data_proto.save_slot.slot_id) = ' + str(per._save_game_data_proto.save_slot.slot_id))
    output('riv_rel is currently using save slot id ' + hex_slot_id)


# ones that fail:
# EA.Sims4.Persistence.SaveSlotData.slot_id
# str( ^^ )
# per.get_save_slot_proto_guid()
# per._save_game_data_proto
# per._save_game_data_proto[1][0]
# str( ^^ )
# per._save_game_data_proto[1][1]
# str( ^^ )
# type(per._save_game_data_proto)
# str(per._save_game_data_proto.save_slot[slot_id])
# json.dump(per._save_game_data_proto, json_file)

# ones that work:
# str(per.get_save_slot_proto_guid())
# ^ came out as 3017080839
# str(per._save_game_data_proto.save_slot)
# ^ VERY VERY long boi
# str(per._save_game_data_proto.save_slot.slot_id)
# ^ came out as 14
# json.dump([str(per._save_game_data_proto)], json_file)
# used in ww:
# per._save_game_data_proto.get_save_slot_proto_buff().slot_id

# clear log except for errors and birth date records
@sims4.commands.Command('riv_rel_log_clear', command_type=sims4.commands.CommandType.Live)
def riv_clear_log(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    output('clearing non-error/birth record lines from riv_rel.log...')
    file_dir = Path(__file__).resolve().parent.parent
    file_name = 'riv_rel.log'
    file_path = os.path.join(file_dir, file_name)

    # grab old text as list
    with open(file_path, 'r') as log_file:
        # get log text line by line
        old_file = log_file.read()
    old_text = old_file.split('\n')
    old_line_num = len(old_text)

    # clear log_file
    with open(file_path, 'w') as log_file:
        # get log text line by line
        log_file.write('')

    # now redo all the error lines
    new_line_num = 0
    while old_text:
        line = old_text.pop(0)
        if 'error' in line or 'spawned' in line or 'game loaded' in line or 'save ID' in line:
            new_line_num += 1
            with open(file_path, 'a') as log_file:
                log_file.write(line + '\n')

    # add new line
    with open(file_path, 'a') as log_file:
        log_file.write('\n')

    output(f'done: gone from {old_line_num} lines to {new_line_num}.')


# test if two sims are an eligible couple
@lru_cache(maxsize=None)
def is_eligible_couple(x_id, y_id):
    # handle the funny case
    if x_id == y_id:
        return False, 'mate, that\'s just being single with extra steps'

    # make rivsims
    sim_x = get_rivsim_from_id(x_id)
    sim_y = get_rivsim_from_id(y_id)

    # make sims
    gsim_x = get_sim_from_rivsim(sim_x)
    gsim_y = get_sim_from_rivsim(sim_y)

    # check direct rel
    if drel_incest and get_direct_relation(sim_x, sim_y):
        return False, f'{sim_x.first_name} and {sim_y.first_name} ' \
                      f'are not an eligible couple: they are directly related'

    # check consanguinity
    xy_consang = consang(sim_x, sim_y)
    if xy_consang >= consang_limit:
        return False, f'{sim_x.first_name} and {sim_y.first_name} ' \
                      f'are not an eligible couple: over the consanguinity limit'

    # should be all good
    return True, f'{sim_x.first_name} and {sim_y.first_name} are an eligible couple with your settings!'


# eligible couple console command
@sims4.commands.Command('riv_is_eligible_couple', command_type=sims4.commands.CommandType.Live)
def console_is_eligible_couple(sim_x: SimInfoParam, sim_y: SimInfoParam, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    eligibility = is_eligible_couple(sim_x.sim_id, sim_y.sim_id)
    x_age = sim_x.age
    y_age = sim_y.age
    if x_age in [Age.BABY, Age.TODDLER, Age.CHILD] or y_age in [Age.BABY, Age.TODDLER, Age.CHILD]:
        output(f'{sim_x.first_name} and {sim_y.first_name} are not an eligible couple: '
               f'at least one is too young for romance')
    else:
        output(eligibility[1])
    try:
        eligibility2 = sim_x.incest_prevention_test(sim_y)
        if eligibility2:
            output('the game considers this as incest')
        else:
            output('the game does not consider this as incest')
    except Exception as e:
        riv_log(f'riv_is_eligible_couple couldn\'t check if this is ingame incest because {e}', 1)


# all eligible suitors console command (eligible couple + same age + sim_y is alive) TODO: test!
@sims4.commands.Command('riv_get_suitors', command_type=sims4.commands.CommandType.Live)
def console_get_suitors(sim_x: SimInfoParam, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    incest_rules = f'consanguinity under {round(100*consang_limit, 5)}%'
    if drel_incest:
        incest_rules = incest_rules + ', not directly related'
    output(f'all eligible partners for {sim_x.first_name}, i.e. different sims, same age, alive, '
           f'and their relationship wouldn\'t be incestuous ({incest_rules})')
    for sim_y in services.sim_info_manager().get_all():
        eligibility = is_eligible_couple(sim_x.sim_id, sim_y.sim_id)
        try:
            eligibility2 = sim_x.incest_prevention_test(sim_y)
        except Exception as e:
            riv_log(f'error: riv_get_suitors couldn\'t check if this is ingame incest because {e}', 1)
            eligibility2 = True  # x and True = x
        if eligibility[0] and eligibility2:  # this couple is eligible
            if sim_x.age == sim_y.age:  # this couple is the same age
                if not sim_y.is_ghost():  # sim_y isn't dead
                    output(f'{sim_y.first_name} {sim_y.last_name}, with '
                           f'consanguinity {round(100 * consang(sim_x, sim_y),5)}%')


# use my consanguinity in incest prevention test. n.b. True = not incest, so we want my result AND original
@inject_to(SimInfo, 'incest_prevention_test')
def riv_incest_prevention_test(original, self, sim_info_b):
    incest_prevention_tic = time.perf_counter()
    result = original(self, sim_info_b)

    # checks if this is already incest (i.e. False)
    if not result:
        return result

    # otherwise, might need to check consanguinity
    riv_result = True
    try:
        riv_result = is_eligible_couple(self.sim_id, sim_info_b.sim_id)[0]
        riv_log(f'incest test between {self.first_name} and {sim_info_b.first_name}: '
                f'original result is {result}, my mod says {riv_result}. __name__ = {__name__}', 3)
    except Exception as e:
        riv_log(f'error: didn\'t manage to influence incest settings because {e}')

    incest_prevention_toc = time.perf_counter()
    iptime = incest_prevention_toc - incest_prevention_tic

    if iptime > 1:
        ip_loglevel = 2
    else:
        ip_loglevel = 3

    riv_log(f'incest test between {self.first_name} and {sim_info_b.first_name} took {iptime}s', ip_loglevel)
    return riv_result

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

# PARENTHOOD
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

# DO NOT ADVERTISE YET


# despawns added
@inject_to(DeathTracker, 'set_death_type')
def riv_set_death_type(original, self, *args, **kwargs):
    result = original(self, *args, **kwargs)
    try:
        riv_log(f'dead sim: {self._sim_info.first_name} {self._sim_info.last_name} despawned {format_sim_date()}')
    except Exception as e:
        riv_log(f'error in riv_set_death_type: {e}')
    return result
