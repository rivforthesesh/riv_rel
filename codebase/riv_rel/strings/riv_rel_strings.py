from strings.EN.rrs_00_your_details import *
from strings.EN.rrs_01_main_commands import *
from strings.EN.rrs_02_help_commands import *
from strings.EN.rrs_03_json_commands import *
from strings.EN.rrs_04_startup_notif import *
from strings.EN.rrs_05_relations import *
from strings.EN.rrs_06_are_we_related_flavour_text import *
from strings.EN.rrs_07_trait_commands import *


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
