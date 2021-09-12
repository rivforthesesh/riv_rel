# NO LANGUAGE STRINGS ALLOWED

from typing import List
from server_commands.argument_helpers import SimInfoParam
# TODO: do not lock these to EN
from strings.EN.rrs_00_your_details import *
from strings.EN.rrs_01_main_commands import *
from strings.EN.rrs_02_help_commands import *
from strings.EN.rrs_03_json_commands import *
from strings.EN.rrs_04_startup_notif import *
from strings.EN.rrs_05_relations import *
from strings.EN.rrs_06_are_we_related_flavour_text import *
from strings.EN.rrs_07_trait_commands import *

new_parser = True


# set up parsing
def p(st: str or tuple, is_female=False):
    if isinstance(st, str):
        # language specific customisations - used for Spanish
        if '@' in st:
            if is_female:
                return st.replace('@', 'a')
            else:
                return st.replace('@', 'o')

        # if none of the above, then
        return st
    elif isinstance(st, tuple):
        # False = male = 0, True = female = 1
        return st[is_female]
    else:
        raise Exception


# direct rel
def direct(gens: List, gender: bool):
    rl = []
    if new_parser:
        # new version
        for n in gens:
            if n in d.keys():
                rel_str = p(d[n], gender)  # gets direct rel for that number then parses it
            elif n < d_anc:
                mult = '(x' + str(d_anc - n) + ')-' if d_anc - n > 1 else '-'
                rel_str = d_great + mult + p(d[d_anc], gender)
            elif n > d_des:
                mult = '(x' + str(n - d_des) + ')-' if n - d_des > 1 else '-'
                rel_str = d_great + mult + p(d[d_des], gender)
            else:
                rel_str = '?'
            rl.append(rel_str)
    else:
        # old version
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
            rl.append(rel_str)
    return rl


# indirect rel
def indirect(xy_indirect_rels: List, gender: bool):
    rl = []
    if new_parser:

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

            if nth == 0:  # pibling/sibling/nibling
                if nce in i1.keys():
                    rel_str = p(i1[nce], gender)  # gets indirect then parses
                elif nce < d_anc:
                    mult = '(x' + str(i1_anc - nce) + ')-' if i1_anc - nce > 1 else '-'
                    rel_str = i_great + mult + p(i1[i1_anc], gender)
                elif n > d_des:
                    mult = '(x' + str(nce - i1_des) + ')-' if nce - i1_des > 1 else '-'
                    rel_str = i_great + mult + p(i1[i1_des], gender)
                else:
                    rel_str = '?'
            else:  # cousin
                # nth cousin m times removed
                # TODO: spanish ver
                rel_str = p(nth_cousin, gender).format(
                    nth=p(h[nth], gender) if nth in h.keys() else p(th(nth), gender),
                    cousin=cousin
                )
                # k times removed if needed
                if abs(nce) > 0:
                    rel_str = p(nth_cousin_m_times_removed, gender).format(
                        nth_cousin=rel_str,
                        m_times_removed=p(v[nce], gender) if nce in v.keys()
                        else p(m_times, gender).format(num=abs(nce))
                    )

            # apply half bit (note rel_str will already be formatted)
            if sib_strength == 0.5:
                rel_str = half_rel.format(half=p(half, gender), rel=rel_str)

            rl.append((rel_str, sim_z, sim_w))

        return rl

    else:

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
                    # nth
                    if nth % 10 == 1 and nth != 11:
                        rel_str += str(nth) + 'st '
                    elif nth % 10 == 2 and nth != 12:
                        rel_str += str(nth) + 'nd '
                    elif nth % 10 == 3 and nth != 13:
                        rel_str += str(nth) + 'rd '
                    else:
                        rel_str += str(nth) + 'th '
                rel_str += 'cousin'
                if nce > 0:
                    if nce == 1:
                        rel_str += ' once '
                    elif nce == 2:
                        rel_str += ' twice '
                    else:
                        rel_str += ' {num} times '.format(num=str(nce))
                    rel_str += 'removed'
            rl.append((rel_str, sim_z, sim_w))

        return rl


def inlaw(xy_inlaw_rels: List, sim_x: SimInfoParam):
    rl = []
    if new_parser:

        for rel in xy_inlaw_rels:
            try:
                if rel[0] == 0:  # spouse
                    try:
                        rl.append((p(spouse, sim_x.is_female), 0))
                    except Exception as e:
                        riv_log(f'error in adding/appending spouse relation ({e})')
                elif rel[0] == 1:  # direct-rel-in-law
                    try:
                        for drel in direct([rel[1]], sim_x.is_female):  # = [str,...]
                            try:
                                rl.append((p(rel_in_law, sim_x.is_female).format(rel=drel, in_law=in_law), rel[3]))
                            except Exception as e:
                                riv_log(f'error in appending direct-rel-in-law ({e})')
                    except Exception as e:
                        riv_log(f'error in adding direct-rel-in-law ({e})')
                elif rel[0] == 2:  # indirect rel-in-law
                    try:
                        for irel in indirect([rel[1]], sim_x.is_female):  # = [(str, sim_z, sim_w),...]
                            try:
                                rl.append((p(rel_in_law, sim_x.is_female).format(rel=irel[0], in_law=in_law), rel[3]))
                            except Exception as e:
                                riv_log(f'error in appending indirect-rel-in-law ({e})')
                    except Exception as e:
                        riv_log(f'error in adding indirect-rel-in-law ({e})')
                elif rel[0] == -1:  # error
                    rl.append((rel[1], 1))
            except Exception as e:
                riv_log(f'error in formatting inlaw rels ({e})')
        return rl

    else:

        # old version
        for rel in xy_inlaw_rels:
            try:
                if rel[0] == 0:  # spouse
                    try:
                        if sim_x.is_female:
                            rl.append(('wife', 0))
                        else:
                            rl.append(('husband', 0))
                    except Exception as e:
                        riv_log(f'error in adding/appending spouse relation ({e})')
                elif rel[0] == 1:  # direct-rel-in-law
                    try:
                        for drel in format_direct_rel_gender([rel[1]], sim_x.is_female):  # = [str,...]
                            try:
                                rl.append((drel + ' in law', rel[3]))
                            except Exception as e:
                                riv_log(f'error in appending direct-rel-in-law ({e})')
                    except Exception as e:
                        riv_log(f'error in adding direct-rel-in-law ({e})')
                elif rel[0] == 2:  # indirect rel-in-law
                    try:
                        for irel in format_indirect_rel_gender([rel[1]],
                                                               sim_x.is_female):  # = [(str, sim_z, sim_w),...]
                            try:
                                rl.append((irel[0] + ' in law', rel[3]))
                            except Exception as e:
                                riv_log(f'error in appending indirect-rel-in-law ({e})')
                    except Exception as e:
                        riv_log(f'error in adding indirect-rel-in-law ({e})')
                elif rel[0] == -1:  # error
                    rl.append((rel[1], 1))
            except Exception as e:
                riv_log(f'error in formatting inlaw rels ({e})')
        return rl


def step(xy_step_rels: List, sim_x: SimInfoParam):
    rl = []
    if new_parser:

        for step_rel in xy_step_rels:
            try:
                sim_xz = step_rel[0]
                sim_zy = step_rel[1]
                rel_list = step_rel[2]
                for rel in rel_list:
                    try:
                        if isinstance(rel, int):
                            rel_str = direct([rel], sim_x.is_female)[0]
                            # str from [str]
                        else:
                            rel_str = indirect([rel], sim_x.is_female)[0][0]
                            # str from [(str, sim_z, sim_w)]
                        rl.append((p(step_rel, sim_x.is_female).format(
                            step=p(step, sim_x.is_female),
                            rel=rel_str
                        ), sim_xz, sim_zy))
                    except Exception as e:
                        riv_log(f'error in formatting step rel {rel} ({e})')
            except Exception as e:
                riv_log(f'error in formatting step rels {step_rel} ({e})')
        return rl

    else:

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
                        rl.append(('step ' + rel_str, sim_xz, sim_zy))
                    except Exception as e:
                        riv_log(f'error in formatting step rel {rel} ({e})')
            except Exception as e:
                riv_log(f'error in formatting step rels {step_rel} ({e})')

        return rl


# outputs a string with the prefix for relation multiplicity and a space after if it is a word
# show_single = 0 if you want 1 -> '', instead of 1 -> 'single'
def tup(n: int, show_single: int):

    if n < 1:
        return '?'
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
        return n_tuple.format(n=n)
