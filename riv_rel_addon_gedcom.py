# IMPORTANT USAGE NOTES: GAME MUST BE PAUSED

# get irl datetime
from datetime import datetime

# commands
import services
import sims4.commands

# grab .json files
import json
import os
from pathlib import Path

# recognise riv_rel
# Mods/riv_rel/riv_rel.ts4script/riv_rel.pyc
import sys

sys.path.append('../')
# https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
try:
    import riv_rel
    from riv_rel import RivSim, RivSimList, RivRelDict

    riv_rel.riv_log('riv_rel_addon_gedcom successfully imported riv_rel')
except Exception as e:
    riv_rel.riv_log('error - riv_rel_addon_gedcom failed to import riv_rel because ' + str(e))


# new rivlog
def riv_log(string):
    return riv_rel.riv_log('[gedcom] ' + str(string))


# family unit
class RivFamUnit:
    def __init__(self, sim_x: RivSim, sim_y: RivSim, rel_dict: RivRelDict):
        # if f+m then is_fm and p = f, q = m, else p = smaller and q = larger sim_id
        # one f one m
        if sim_x.is_female and not sim_y.is_female:
            self.is_fm = True
            self.p = sim_x
            self.q = sim_y
        elif not sim_x.is_female and sim_y.is_female:
            self.is_fm = True
            self.p = sim_y
            self.q = sim_x

        # two f or two m
        elif int(sim_x.sim_id) < int(sim_y.sim_id):
            self.is_fm = False
            self.p = sim_x
            self.q = sim_y
        elif int(sim_x.sim_id) > int(sim_y.sim_id):
            self.is_fm = False
            self.p = sim_y
            self.q = sim_x

        # only one parent
        else:
            self.is_fm = False
            self.p = sim_x
            self.q = None

        # parents
        self.parents = [sim_x.sim_id, sim_y.sim_id]
        # kids (every rivsim that has these two as parents)
        self.children = [RivSim(sim_id) for sim_id in rel_dict.rels.keys()
                         if set(rel_dict.rels[sim_id]) == {int(sim_x.sim_id), int(sim_y.sim_id)}]

    def __str__(self):
        return f'<RivFamUnit {self.p} {self.q}>'

    def __repr__(self):
        return str(self)

    # gets family id for gedcom
    def gedcom_id(self):
        return '@' + str(self.p.sim_id) + '000' + str(self.q.sim_id) + '@'


# write to gedcom file
@sims4.commands.Command('riv_gedcom', command_type=sims4.commands.CommandType.Live)
def write_gedcom(keyword: str, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    # locate files
    file_dir = Path(__file__).resolve().parent.parent
    sim_file_name = f'riv_rel_{keyword}.json'  # e.g. riv_rel_pine.json
    sim_file_path = os.path.join(file_dir, sim_file_name)
    rel_file_name = f'riv_relparents_{keyword}.json'  # e.g. riv_rel_pine.json
    rel_file_path = os.path.join(file_dir, rel_file_name)

    # grab sims
    gedcom_sim_list = RivSimList()
    with open(sim_file_path, 'r') as json_file:
        gedcom_sim_list.sims = [RivSim(sim) for sim in json.load(json_file)]

    # grab rels
    gedcom_rel_dict = RivRelDict()
    with open(rel_file_path, 'r') as json_file:
        gedcom_rel_dict.rels = json.load(json_file)

    # construct header
    header = '0 HEAD\n' \
                '1 GEDC\n' \
                    '2 VERS 5.5.5\n' \
                    '2 FORM LINEAGE-LINKED' \
                        '3 VERS 5.5.5' \
                '1 CHAR UTF-8\n' \
                '1 SOUR riv_rel gen ' + str(riv_rel.rr_gen) + '\n' \
                    '2 NAME ' + keyword + '\n' \
                    '2 VERS 5.5.5\n' \
                        '3 WWW rivforthesesh.itch.io/riv-rel\n' \
                '1 DATE ' + datetime.now().strftime('%d %b %Y') + '\n' \
                    '2 TIME ' + datetime.now().strftime('%H:%M:%S') + '\n' \
                '1 FILE riv_' + keyword + '.ged\n' \
                '1 LANG English\n'

    # get each fam unit (unique set of parent lists)
    parents = list(set(gedcom_rel_dict.rels.values()))
    # turn into pairs
    parent_pairs = [p for p in parents if len(p) == 2] + \
                   [p + p for p in parents if len(p) == 1]
    # turn into fam units
    fam_units = [RivFamUnit(x, y, gedcom_rel_dict) for [x, y] in parent_pairs]

    # add one fam unit at a time
    # TODO

    # go through any other ones

    # construct trailer
    trailer = '0 TRLR'
