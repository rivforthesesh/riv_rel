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


# fam count (reset at the start of file creation)
fam_count = 0


# family unit
class RivFamUnit:
    def __init__(self, sim_x: RivSim, sim_y: RivSim, rel_dict: RivRelDict, fam_num=0):
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
        self.fam_id = f'fam{fam_num}'

    def __str__(self):
        return f'<RivFamUnit {self.p} {self.q}>'

    def __repr__(self):
        return str(self)


# write to gedcom file
@sims4.commands.Command('riv_gedcom', command_type=sims4.commands.CommandType.Live)
def write_gedcom(keyword='', _connection=None):
    output = sims4.commands.CheatOutput(_connection)

    global fam_count
    fam_count = 0

    if keyword:  # a file has been specified
        # locate files
        file_dir = Path(__file__).resolve().parent.parent
        sim_file_name = f'riv_rel_{keyword}.json'  # e.g. riv_rel_pine.json
        sim_file_path = os.path.join(file_dir, sim_file_name)
        rel_file_name = f'riv_relparents_{keyword}.json'  # e.g. riv_rel_pine.json
        rel_file_path = os.path.join(file_dir, rel_file_name)

        # check if exists
        output(f'[0/10] specified save {keyword}')
        if not os.path.isfile(sim_file_path):
            output(f'could not find files for keyword {keyword}; please try again')

        # grab sims
        gedcom_sim_list = RivSimList()
        with open(sim_file_path, 'r') as json_file:
            gedcom_sim_list.sims = [RivSim(sim) for sim in json.load(json_file)]
        output(f'[1/10] got {len(gedcom_sim_list.sims)} sims')

        # grab rels
        gedcom_rel_dict = RivRelDict()
        with open(rel_file_path, 'r') as json_file:
            gedcom_rel_dict.rels = json.load(json_file)
        output(f'[2/10] got rels')
    else:
        # use current sims
        output(f'[0/10] no save specified, using current save file ({riv_rel.hex_slot_id})')
        gedcom_sim_list = riv_rel.riv_sim_list
        output(f'[1/10] got {len(gedcom_sim_list.sims)} sims')
        gedcom_rel_dict = riv_rel.riv_rel_dict
        output(f'[2/10] got rels')
        # set up keyword
        keyword = riv_rel.hex_slot_id

    dt = datetime.now()
    file_name = 'riv_' + keyword + '_' + dt.strftime('%Y-%m-%d-%H-%M-%S') + '.ged'
    submitter = 'A. /Simmer/'  # TODO: username? active sim?

    # construct header
    header = '0 HEAD\n' \
                '1 GEDC\n' \
                    '2 VERS 5.5.5\n' \
                    '2 FORM LINEAGE-LINKED\n' \
                        '3 VERS 5.5.5\n' \
                '1 CHAR ASCII\n' \
                '1 SOUR riv_rel\n' \
                    '2 NAME ' + keyword + '\n' \
                    '2 VERS ' + str(riv_rel.rr_gen) + '\n' \
                '1 DATE ' + dt.strftime('%d %b %Y') + '\n' \
                    '2 TIME ' + dt.strftime('%H:%M:%S') + '\n' \
                '1 FILE ' + file_name + '\n' \
                '1 LANG English\n' \
                '1 SUBM @U@\n' \
            '0 @U@ SUBM\n' \
                '1 NAME ' + submitter + '\n'
    output('[3/10] constructed header')

    # get each fam unit
    # get all parent lists
    parents_tmp = list(gedcom_rel_dict.rels.values())
    # get unique ones
    parents = []
    for p in parents_tmp:
        # ensure smallest first if there are two
        if len(p) == 2:
            if p[1] < p[0]:
                p = [p[1], p[0]]
        # ensure it's the same repeated if only one
        elif len(p) == 1:
            p = p + p
        else:
            continue  # next p

        # add to parents if not added
        if p not in parents:
            parents.append(p)
    # cleanup
    del parents_tmp
    # turn into fam units
    gedcom_fam_units = []
    for xy in parents:  # each xy has two parents (even if it's a repeat)
        x = [rivsim for rivsim in gedcom_sim_list if rivsim.sim_id == xy[0]][0]
        y = [rivsim for rivsim in gedcom_sim_list if rivsim.sim_id == xy[1]][0]
        gedcom_fam_units.append(RivFamUnit(
            x,
            y,
            gedcom_rel_dict,
            fam_count
        ))
        # increment family ID
        fam_count += 1
    output('[4/10] got family units (parents + children)')

    # maps sim ID to their gedcom entry
    gedcom_sim_dict = {}

    # add one sim at a time (main info)
    for sim in gedcom_sim_list.sims:
        # get gender marker
        if sim.is_female:
            gender = 'F'
        else:
            gender = 'M'

        first_name = sim.first_name if sim.first_name else 'Nameless'
        last_name = sim.last_name if sim.first_name else f'Sim-{sim.sim_id}'

        gedsim = f'0 {sim.sim_id} INDI\n' \
                     f'1 NAME {first_name} /{last_name}/\n' \
                         f'2 GIVN {first_name}\n' \
                         f'2 SURN {last_name}\n' \
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
                ged_parents = f'1 WIFE {fam.p.sim_id}\n'
            else:
                ged_parents = f'1 HUSB {fam.p.sim_id}\n'
            # add link to fam in sim record
            gedcom_sim_dict[fam.p.sim_id] = gedcom_sim_dict[fam.p.sim_id] + f'1 FAMS {fam.fam_id}\n'
        else:
            # add two parents to fam
            ged_parents = f'1 HUSB {fam.q.sim_id}\n' \
                          f'1 WIFE {fam.p.sim_id}\n'
            # add link to fam in sim records
            gedcom_sim_dict[fam.p.sim_id] = gedcom_sim_dict[fam.p.sim_id] + f'1 FAMS {fam.fam_id}\n'
            gedcom_sim_dict[fam.q.sim_id] = gedcom_sim_dict[fam.q.sim_id] + f'1 FAMS {fam.fam_id}\n'

        # kids
        ged_children = ''
        for child_id in fam.children:
            # add child to fam
            ged_children = ged_children + f'1 CHIL {child_id}\n'
            # add link to fam in sim record
            gedcom_sim_dict[child_id] = gedcom_sim_dict[child_id] + f'1 FAMS {child_id}\n'

        gedfam = f'{fam.fam_id} FAM\n' \
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
