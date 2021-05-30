# IMPORTANT USAGE NOTES: GAME MUST BE PAUSED

# get irl datetime
from datetime import datetime

# commands
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
        self.children = [sim_id for sim_id in rel_dict.rels.keys()
                         if set(rel_dict.rels[sim_id]) == {int(sim_x.sim_id), int(sim_y.sim_id)}]
        # id
        if self.q is not None:
            self.fam_id = str(self.p.sim_id) + '000' + str(self.q.sim_id)
        else:
            self.fam_id = str(self.p.sim_id)

    def __str__(self):
        return f'<RivFamUnit {self.p} {self.q}>'

    def __repr__(self):
        return str(self)


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
    output('[1/10] got sims')

    # grab rels
    gedcom_rel_dict = RivRelDict()
    with open(rel_file_path, 'r') as json_file:
        gedcom_rel_dict.rels = json.load(json_file)
    output('[2/10] got rels')

    dt = datetime.now()
    file_name = 'riv_' + keyword + '_' + dt.strftime('%Y-%m-%d-%H-%M-%S') + '.ged'

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
                '1 DATE ' + dt.strftime('%d %b %Y') + '\n' \
                    '2 TIME ' + dt.strftime('%H:%M:%S') + '\n' \
                '1 FILE ' + file_name + '\n' \
                '1 LANG English\n'
    output('[3/10] constructed header')

    # TODO: see what caused unhashable type list error

    # get each fam unit (unique set of parent lists)
    parents = set(gedcom_rel_dict.rels.values())
    # turn into pairs
    parent_pairs = [p for p in parents if len(p) == 2] + \
                   [p + p for p in parents if len(p) == 1]
    # turn into fam units
    gedcom_fam_units = []
    for xy in parent_pairs:
        x = xy[0]
        y = xy[1]
        gedcom_fam_units.append(RivFamUnit(x, y, gedcom_rel_dict))
    # gedcom_fam_units = [RivFamUnit(x, y, gedcom_rel_dict) for [x, y] in parent_pairs
    output('[4/10] got family units (parents + children)')

    # maps sim ID to their gedcom entry
    gedcom_sim_dict = {}

    # add one sim at a time (main info)
    for sim in gedcom_sim_list.sims:
        # get gender marker TODO: destroy gender binary
        if sim.is_female:
            gender = 'F'
        else:
            gender = 'M'

        gedsim = f'0 @{sim.sim_id}@ INDI\n' \
                     f'1 NAME {sim.first_name} /{sim.last_name}/\n' \
                         f'2 GIVN {sim.first_name}\n' \
                         f'2 SURN {sim.last_name}\n' \
                     f'1 SEX {gender}\n'

        # add to dict
        gedcom_sim_dict[sim.sim_id] = gedsim

    output(f'[5/10] written gedcom entries for {len(gedcom_sim_list.sims)} sims')

    # maps fam ID to its gedcom entry
    gedcom_fam_dict = {}

    # add one fam at a time
    for fam in gedcom_fam_units:

        # parents segment
        if fam.q is None:
            # add parent to fam
            if fam.p.is_female:
                ged_parents = f'1 WIFE @{fam.p.sim_id}@\n'
            else:
                ged_parents = f'1 HUSB @{fam.p.sim_id}@\n'
            # add link to fam in sim record
            gedcom_sim_dict[fam.p.sim_id] = gedcom_sim_dict[fam.p.sim_id] + f'1 FAMS @{fam.p.sim_id}@\n'
        else:
            # add two parents to fam
            ged_parents = f'1 HUSB @{fam.q.sim_id}@\n' \
                          f'1 WIFE @{fam.p.sim_id}@\n'
            # add link to fam in sim records
            gedcom_sim_dict[fam.p.sim_id] = gedcom_sim_dict[fam.p.sim_id] + f'1 FAMS @{fam.p.sim_id}@\n'
            gedcom_sim_dict[fam.q.sim_id] = gedcom_sim_dict[fam.q.sim_id] + f'1 FAMS @{fam.q.sim_id}@\n'

        # kids
        ged_children = ''
        for child_id in fam.children:
            # add child to fam
            ged_children = ged_children + f'1 CHIL @{child_id}@\n'
            # add link to fam in sim record
            gedcom_sim_dict[child_id] = gedcom_sim_dict[child_id] + f'1 FAMS @{child_id}@\n'

        gedfam = f'@{fam.fam_id}@ FAM\n' \
                    + ged_parents \
                    + ged_children

        # add to dict
        gedcom_fam_dict[fam.fam_id] = gedfam

    output(f'[6/10] written gedcom entries for {len(gedcom_fam_dict)} fams')

    # construct trailer
    trailer = '0 TRLR'

    # sort lists
    sim_ids = list(gedcom_sim_dict.keys())
    sim_ids.sort()
    fam_ids = list(gedcom_fam_dict.keys())
    fam_ids.sort()

    # get file
    file_dir = Path(__file__).resolve().parent.parent
    file_path = os.path.join(file_dir, file_name)

    # add header
    with open(file_path, 'w') as file:
        file.write(header)
    output(f'[7/10] added header to {file_name}')

    # add sims
    for sim_id in sim_ids:
        with open(file_path, 'a') as file:
            file.write(gedcom_sim_dict[sim_id])
    output(f'[8/10] added sims to {file_name}')
            
    # add fams
    for fam_id in fam_ids:
        with open(file_path, 'a') as file:
            file.write(gedcom_fam_dict[fam_id])
    output(f'[9/10] added fams to {file_name}')

    # add trailer
    with open(file_path, 'a') as file:
        file.write(trailer)
    output(f'[10/10] added trailer to {file_name}')

    output('[riv_gedcom: all done!]')
