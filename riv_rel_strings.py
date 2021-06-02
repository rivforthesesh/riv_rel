# don't rename this file!

# notes before you start translating:

#   the things that you want to replace are between ''
#       if you see something like x = 'some text here '\
#                                     'then more text here'
#       then x will show up as 'some text here then more text here'
#   if you have an apostrophe ('), you need to write it as \'
#   variables (names, numbers, relations) will be inserted into sentences between {}
#       the variable name is here, e.g. '{x_firstname} is {y_firstname}\'s parent'
#   any line starting with # is a comment
#   some of these need a space at the start and/or end (if so, there'll be a comment next to it)
#   some of these need a line break - shown by \n - at the start and/or end (will also be in comments)
#   don't translate
#       command names (basically anything starting with "riv_")
#       file names
#       anything between {}

#   if you're translating something that is gendered, put it in a tuple with (male ver, female ver)
#   an example with one sim:
#       cousin = 'cousin'               # EN
#       cousin = ('primo', 'prima')     # ES

#   there is also this shortcut to use 'o' if male and 'a' if female:
#       cousin = 'prim@'

#   more gendering
#   an example with multiple sims, where only one sim's gender matters (please make a note of which in the comments)
#       get_parents_1 = '{y_firstname} {y_lastname} is {x_firstname}\'s parent'
#       get_parents_1 = ('{y_firstname} {y_lastname} es el padre de {x_firstname}', '{y_firstname} {y_lastname} es la madre de {x_firstname}')     # use gender: sim_y
#   an example with multiple sims
#       get_sib_strength_1 = '{x_firstname} and {y_firstname} are full siblings.'
#       get_sib_strength_1 = '{x_firstname} y {y_firstname} son herman@s complet@s' # first version is used if one is male, and the second if both female

#   please let me know if
#       something doesn't quite work in your language
#           e.g. "step-parent" is a completely different word and not just "step" + "parent"
#       you need more context
#       there are more than two gendered versions
#           it depends on both sims' genders separately
#           your language has three+ grammatical genders

# ==== your details ====

# if there are any translations that need more complex logic, this is the value i'll test for before running other code
lang = 'EN'
# the name of your language, in that language
lang_name = 'English'
# name(s) of translators. "a, b, and c" will appear in the starting notif as "translated by: a, b, and c"
name = 'riv'

# ==== often used (high priority) ====

and_ = 'and'

# ==== command outputs (high priority) ====

# the variable name relates to the command, e.g. get_parents_0 is a string for riv_get_parents
get_parents_0 = '{x_firstname}\'s parents not found'
# 		Bob's parents not found
get_parents_1 = '{y_firstname} {y_lastname} is {x_firstname}\'s parent'
# 		Bob Pancakes is Iggy's parent

get_children_0 = '{x_firstname}\'s children not found'
# 		Maple's children not found
get_children_1 = '{y_firstname} {y_lastname} is {x_firstname}\'s child'
# 		Iggy Pancakes is Bob's child

get_ancestors_0 = '{x_firstname}\'s ancestors not found'
# 		Bob's ancestors not found
get_ancestors_1 = '{y_firstname} {y_lastname} is {x_firstname} {x_lastname}\'s ancestor, {n} generation back'
# 		Bob Pancakes is Iggy Pancakes's ancestor, 1 generation back
get_ancestors_2 = '{y_firstname} {y_lastname} is {x_firstname} {x_lastname}\'s ancestor, {n} generations back'
# 		Bob Pancakes is Maple Pancakes's ancestor, 2 generations back

get_descendants_0 = '{x_firstname}\'s descendants not found'
# 		Maple's descendants not found
get_descendants_1 = '{y_firstname} {y_lastname} is {x_firstname} {x_lastname}\'s descendant, {n} generation forward'
# 		Iggy Pancakes is Bob Pancakes's descendant, 1 generation forward
get_descendants_2 = '{y_firstname} {y_lastname} is {x_firstname} {x_lastname}\'s descendant, {n} generations forward'
# 		Maple Pancakes is Bob Pancakes's descendant, 2 generations forward

get_direct_rel_0 = 'no direct rel found between {x_firstname} and {y_firstname}'
#       no direct rel(ationship) found between Bob and Bella
get_direct_rel_1 = '{x_firstname} {x_lastname} is {y_firstname} {y_lastname}\'s {rel}.'
#       Bob Pancakes is Iggy Pancakes's father.

get_sib_strength_self = '{x_firstname} is {y_firstname}.'
#       Bob is Bob.
#       appears if you use riv_get_sib_strength and enter the same name twice
get_sib_strength_full = '{x_firstname} and {y_firstname} are full siblings.'
#       Maple and Syrup are full siblings. [two shared parents]
get_sib_strength_half = '{x_firstname} and {y_firstname} are half siblings.'
#       Maple and Syrup are half siblings. [one shared parent]
get_sib_strength_none = '{x_firstname} and {y_firstname} are not siblings.'
#       Maple and Syrup are not siblings. [no shared parents]
get_sib_strength_error = 'something went wrong: sib_strength is {num} when it should be 0, 0.5, or 1'
#       you don't need to translate "sib_strength", and the value in {num} will be an unexpected number

get_indirect_rel_0 = 'no indirect rel found between {x_firstname} and {y_firstname}'
#       no indirect rel(ation) found between Maple and Syrup
get_indirect_rel_1 = '{x_firstname} {x_lastname} is {y_firstname} {y_lastname}\'s {rel} (relation found via {z_firstname} {z_lastname})'
#       Maple Pancakes is Syrup Pancake's half sister (relation found via Iggy Pancakes)
get_indirect_rel_2 = '{x_firstname} {x_lastname} is {y_firstname} {y_lastname}\'s {rel} (relation found via {z_firstname} {z_lastname} and {w_firstname} {w_lastname})'
#       Maple Pancakes is Syrup Pancake's sister (relation found via Iggy Pancakes and Orange Pancakes)

consang_0 = 'consanguinity'
consang_1 = 'consanguinity between {x_firstname} and {y_firstname} is {num}%'
#       consanguinity between Bob and Iggy is 50%

isc_not_elig = '{x_firstname} and {y_firstname} are not an eligible couple: '  # space at end
isc_directly_related = 'they are directly related'
isc_consang = 'over the consanguinity limit'
#       or "they are too closely related"
isc_elig = '{x_firstname} and {y_firstname} are an eligible couple with your settings!'
isc_age = 'at least one is too young for romance'
isc_incest = 'the game considers this as incest'
isc_not_incest = 'the game does not consider this as incest'
isc_same_sim = 'mate, that\'s just being single with extra steps'
#       appears if you try to check if a sim could be in a relationship with themself
#       doesn't need to be exact, just something like "this is the same sim"

# for the main riv_rel command
rel_same_sim = '{x_firstname} {x_lastname} is {y_firstname} {y_lastname}'
#       Bob Pancakes is Bob Pancakes
#       entered the same sim twice
rel_exists = '{x_firstname} is {y_firstname}\'s {rel}'
#       Iggy is Bob's son and fourth cousin.
rel_nexists = '{x_firstname} and {y_firstname} are not related.'
#       Bob and Bella are not related.

rel_rand_0 = 'relation with: {y_firstname} {y_lastname}'
#       relation with: Bob Pancakes

rel_rand_rand_0 = 'sims: {x_firstname} {x_lastname} and {y_firstname} {y_lastname}'
#       sims: Bob Pancakes and Bella Goth

rel_all_0 = 'relatives found for {y_firstname}: {num_rels}'
#       relatives found for Bob Pancakes: 3

# ==== help commands (high priority) ====

help_GT = ' (fam and inc can be used as club requirements)'  # space at start
#       this text shows up if someone has the trait and GT addons
#       change fam and inc to whatever you've named the traits
help_features = 'biological, in-law, and (optional) step relations, console commands, social interaction, ' \
         'auto .json files, optional computer help menu, optional traits'
#       a list of features (help_0 is added to the end of this; consanguinity is already translated)
help_settings = 'all settings can be edited by opening the .cfg files (in the same folder as riv_rel) in notepad++'
help_siminfoparam = 'sims can be typed as firstname lastname (use "" if there is a space in the first/last name, ' \
         'e.g. J "Huntington III") or as the sim ID'
help_contact = 'if you find an error, please send me (rivforthesesh / riv#4381) the error text and any relevant rels/files!'

help_twosims = 'commands taking two sims:'
#       this comes before a list of commands that you type two sims after, e.g. riv_consang Bob Pancakes Iggy Pancakes
help_onesim = 'commands taking one sim:'
#       this comes before a list of commands with one sim after, e.g. riv_get_children Bob Pancakes

help_json = 'using .json files ' \
        '[replace xyz by whatever you want to create/use the files riv_rel_xyz.json and riv_relparents_xyz.json]:'
help_auto = 'sets up save to run riv_update xyz on every zone load or sim birth or save'  # description for riv_auto

help_json_debug = '.json files debug commands: '  # space at end
help_save = 'save sim info to .json files'  # description for riv_save
help_load = 'load sim info from .json files'  # description for riv_load
help_clean = 'removes duplicates from .json file'  # description for riv_clean
help_mem = 'shows no. mini sim-infos in memory'  # description for riv_mem; 'no.' = 'number'
help_clear = 'clears memory'  # description for riv_clear
help_update = 'runs save, clear, then load'  # desciption for riv_update
help_ssi = 'shows current save ID'  # description for riv_save_slot_id

help_trait_simletter = 'trait commands taking one sim, and a letter from A to H:'
help_trait_sim = 'trait commands taking one sim:'
help_trait_letter = 'trait commands taking a letter from A to H:'
help_trait_none = 'trait commands taking no arguments:'
#       for commands like riv_traits, where you just type the command name

help_computer = 'check the computer for a menu called "Research on riv_rel.sim..." for explanations and help.'
help_scrollup = 'the help menu is a little long, please scroll up!'

gen_diff_list = 'as a list: '  # space at the end; followed by a list of numbers with generational differences
gen_diff_avg = 'the average generational difference is '  # space at the end; average of the numbers above
gen_diff_sign = '(negative means sim_x is higher up in the family tree than sim_y)'
#       i.e. if the generational difference is a negative number, then sim_x is an ancestor of sim_y

save_slot_id_used = 'riv_rel is currently using save slot id '  # space at end; will be followed by a save slot number

# ==== json / misc command outputs (low priority) ====

# things used across multiple commands
all_done = 'all done'
#       [riv_save: all done]
#       appears when a command is done running

save_time = 'the current sim time is {num}, formatted as {datetime}'
save_abs_tick = '[this number appears with any sims that were added/updated this time]'
#       after this there'll be a number
save_sims_done = 'saved sims.'
save_rels_done = 'saved parent rels.'
save_cmd = 'if you\'re not using riv_auto, then to use these relations in riv_rel, type the following: '
#               space at end; after this it says the command needed, e.g. "riv_load xyz"

load_done = 'loaded in parent rels and {num} sim mini-infos.'
load_random = 'showing a random sim and their parents:'
load_error_0 = 'an error occurred'  # space at end
load_error_1 = 'something went wrong while loading these sims and rels; ' \
         'please check that these files exist in the same folder as riv_rel.ts4script:'
load_error_2 = 'if these files exist then please let me (rivforthesesh / riv#4381) know, and send over any relevant files'

mem_randsim = 'showing a random sim:'
mem_load = 'use riv_load xyz to load in sim info from riv_rel_xyz.json and riv_relparents_xyz.json'
#       leave in "riv_load xyz", "riv_rel_xyz.json", and "riv_relparents_xyz.json" as they are
mem_randrel = 'showing a random sim\'s parents:'

clean_start = 'this file contains {n} sim mini-infos, {c} of which are culled. cleaning...'
clean_end = 'after removing duplicates, this file contains {n} sim mini-infos.'
clean_uncull = 'unculled {m} sims'
#       this gives the number of sims that were previously marked as culled, but are no longer marked as culled
clean_update = 'if you\'re currently using this file, please run riv_update'  # space at end
#       leave in "riv_update "

clear_0 = 'removed temporary file '
#       this only shows up when people use currentsession files, which is off by default
#       you could probably skip translating this and nobody would notice

update_exists = 'this file exists! loading this in'
update_desc = 'running save, clear, then load (updates sim/rel info in mem and .json file)...'

load_cfg_save = 'loaded in cfg settings for save {slot_id}'
#       the value in {slot_id} is a save ID as it appears in the save file name, e.g. 00000005
#       leave 'cfg' as is; it refers to the file extension (filename.cfg)
load_cfg_save0 = 'currently the game thinks your save ID is 0, or your last save was an MCCC autosave - ' \
                      'this can be fixed by saving the game and then running this command again.'
load_cfg_error = 'failed to load in cfg settings because of the below exception:'
#       exception = error in code
load_cfg_update = 'running riv_update {keyword}...'
#       the value in {keyword} is the keyword used for this save in riv_auto
load_cfg_nexists = 'there are no cfg settings for this save ID. run "riv_auto xyz" ' \
                      'with whatever keyword you want in place of xyz to set this up for this save ID.'

auto_makecfg = 'no .cfg file found. creating one...'
auto_update = 'updating settings for Slot_{num}.save to riv_rel - individual save settings.cfg...'
#       do not translate "Slot_{num}.save" or "riv_rel - individual save settings.cfg"
auto_add = 'adding settings for Slot_{num}.save to riv_rel - individual save settings.cfg...'
#       do not translate "Slot_{num}.save" or "riv_rel - individual save settings.cfg"
auto_load_cfg = 'loading in new .cfg settings...'
auto_load_sim = 'loading in sims from file...'
auto_load_rel = 'loading in rels from file...'
auto_sccl = 'running save, clear, clean, then load...'
auto_blocked0 = 'the current game slot is an MCCC autosave slot'
auto_blocked1 = 'blocked riv_auto (autosave slots aren\'t specific to saves so this could cause issues)'
auto_blocked2 = 'please manually save your game to another slot and try again'

# ==== starting notif (medium [there's a lot of text, but everyone using .json files will see this]) ====
# TODO: rename variables

notif_notfound = 'failed to load in sims for this save ID: this usually happens when you\'ve just left CAS, ' \
          'you quit a different save without saving and then loaded this one, or you moved/deleted the ' \
          '.json files. \nif you have not (or aren\'t about to) set up auto .json file updates for this ' \
          'save ID please ignore this notification. \notherwise, please save your game and then enter the ' \
          'following into the command line (CTRL+SHIFT+C): \n\nriv_load_cfg_manually'
notif_notfound_title = 'riv_rel issue'
#       notif_1 is the title
notif_found = 'loaded in settings from riv_rel - individual save settings.cfg ' \
          'for save ID {save_id} and keyword {keyword}.\n\nsim mini-infos: '  # ends with space, followed by a number
notif_autosave_error = 'you\'ve created settings for an MCCC autosave - this won\'t work properly!\n\n' \
          'please save your game to another slot and set up riv_auto again.'
notif_autosave_error_title = 'riv_rel: auto json issue'
notif_autosave = 'you\'ve loaded up an autosave slot! to use riv_auto backups, please save the game to another ' \
          'slot first (if you don\'t want to use riv_auto, you don\'t need to do this)\n\nnumber of sims: '  # space end
notif_nobackup = 'no sim/rel backups were found for this save - if you\'re expecting to see json file backups or want to ' \
          'set them up, enter riv_auto xyz into the cheat console for a keyword xyz!\n\nnumber of sims: '  # space end
notif_otherfiles = 'you have other files in the same folder as my mod - i would recommend putting all files starting riv_rel ' \
          'in their own subfolder (i.e. in Mods/riv_rel/) if you encounter any additional lag on save/load. '
notif_autosaves = '\n\nfound MCCC autosave slots (my mod will continue to see the save slot as {slot_id} if the actual save slot ' \
          'changes to one of these): {autosave_list}'
notif_computer = '\n\nyou can see more information and help in the "Research on riv_rel.sim" menu on the computer'
notif_GT_error = '\n\nyou\'ve downloaded the GT addon without the traits addon - ' \
           'please either download riv_rel_addon_traits or remove riv_rel_addon_GT ' \
           'or you may face glitches with clubs being unable to find my family traits!'
notif_debug = '\n\nif this is the wrong file, run riv_clear, save your game, and run riv_load_cfg_manually.'
notif_thank = '\n\nthank you for using my mod! '
notif_credit = '\n\ntranslated into {rrs.lang_name} by {rrs.name}'
#       this uses the values at the top of the file

# ==== relationships (high priority) ====
# examples used:
# Bob Pancakes, Iggy Pancakes, Maple Pancakes (Iggy's future kid), Syrup Pancakes (maybe Maple's sibling)

# == direct ==
# main bit works off of the number of generations away from the self
# add numbers as you need them
direct_rels = {
    -2: ('grandfather', 'grandmother'),
    -1: ('father', 'mother'),
    0: 'self',  # this one is very rarely going to come up, but it'll appear as "Bob Pancakes is Bob Pancakes's self"
    1: ('son', 'daughter'),
    2: ('grandson', 'granddaughter'),
}
# prefixes used to continue patterns - put the rules for it in comments
d_great = 'great'   # moves one generation away from self, e.g. great-grandson, great(x2)-grandson...

# == indirect (non-cousins) ==
half = 'half'
i_great = 'great'
i_grand = 'grand'
pibling = ('uncle', 'aunt')
sibling = ('brother', 'sister')
nibling = ('nephew', 'niece')
#       sister, half brother, aunt, granduncle, great-grandniece, great(x2)-grandnephew

# == cousins ==
cousin = 'cousin'

first = 'first'
second = 'second'
third = 'third'
th = ['st', 'nd', 'rd', 'th']
#       keep commas between strings, and please let me know when each of these is used
#           first cousin, second cousin, third cousin
#           4th, 5th, ..., 11th, ..., 21st, 22nd, 23rd cousin...
nth_cousin = '{rrs.nth} {rrs.cousin}'   # use for word order

once = 'once'
twice = 'twice'
m_times = '{num} times'
removed = 'removed'
m_times_removed = '{rrs.m_times} {rrs.removed}'  # use for word order
#       first cousin once removed, first cousin twice removed, first cousin 3 times removed, ...

nth_cousin_m_times_removed = '{rrs.nth_cousin} {rrs.m_times_removed}'  # use for word order

# == inlaw ==
spouse = ('husband', 'wife')
in_law = ' in law'  # space at start
#       added to the end of the relation, e.g. brother in law, grandmother in law

# == step ==
step = 'step '  # space at end
#       added to the start of the relation, e.g. step sister, step uncle

# ==== tuples (high priority, but you can set max_n to a low number to have most show up as "n-tuple") ====
#   used to show a relation is repeated
#   I've done this in English up to 100, and above that it just says something like "101-tuple"
#       when you go above 10, you add a prefix for the ones bit, e.g. "12 times" is duo(2) + decuple(10)
#   you can set a maximum below if you don't want to bother beyond a certain value; don't go above 100
max_n = 100  # for any number n that is greater than this, it will just display "n-tuple"

#   going up in ones, i.e. we want n: '<word for n-tuple>'
#       e.g. "double first cousin" = first cousin two different ways
#           (shares two pairs of grandparents, but no shared parents)
#           2: 'double'
leq_ten_tuple = {1: 'single', 2: 'double', 3: 'triple',
                 4: 'quadruple', 5: 'quintuple', 6: 'sextuple',
                 7: 'septuple', 8: 'octuple', 9: 'nonuple'}

#   going up in tens, i.e. we want n: '<word for (10*n)-tuple>'
#       e.g. "decuple 20th cousin" = 20th cousin 10 different ways
#       1: 'decuple'
tens_tuple = {1: 'decuple', 2: 'viguple', 3: 'triguple', 4: 'quadraguple', 5: 'quinquaguple',
              6: 'sexaguple', 7: 'septuaguple', 8: 'octoguple', 9: 'nonaguple', 10: 'centuple'}

#   prefixes, i.e. we want n: '<the bit that goes before tens_tuple above>'
#       e.g. "duodecuple 20th cousin" = 20th cousin 12 different ways
#       2: 'duo'                        [duo + decuple = 2 + 10 = 12]
prefix_tuple = {0: '', 1: 'un', 2: 'duo', 3: 'tre', 4: 'quattuor',
                5: 'quin', 6: 'sex', 7: 'septen', 8: 'octo', 9: 'novem'}

# if the number is too high (above max_n), just give up
n_tuple = '{n}-tuple '  # space at the end

# ==== notification text (low priority) ====

# start of the notification
#   you can add or remove strings from each list if you want!
#   this is just flavour text, so it doesn't need to be exact
#   if you want to skip a case, change the list to the below (where n is whatever number is previously there):
#       n: [''],

strings_dict = {

    # example of an empty list
    -1: [''],

    #  no relations
    0: ['Nope, we aren\'t related.',
        'We aren\'t related at all.',
        'I\'m not related to you. What gave you that idea?'],

    #   inlaw only
    1: ['I\'d hope we aren\'t related.',
        'We aren\'t related.',
        'We don\'t have any biological relation.'],

    #   biologically related
    2: ['Yeah, we\'re related.',
        'Of course we\'re related.'],

    #   inlaws AND biologically related
    3: ['Uh... we are related.',
        'Might as well start singing Sweet Home Appaloosa...',
        'This is a bit awkward.',
        'It\'s a little complicated...'],

    #   stepfamily
    4: ['We aren\'t exactly related.',
        'Technically, we aren\'t related.',
        'We\'re only stepfamily.'],

    #   stepfamily and inlaws
    5: ['We aren\'t technically related.',
        'I\'m one of your in-laws, but we\'re also stepfamily.',
        'Well... we aren\'t related!'],

    #   biologically related and stepfamily
    6: ['We\'re related, but also stepfamily, which is... odd.',
        'Yeah, we\'re related. Everything is kinda messy though.',
        'I mean, we are related, but we\'re stepfamily too.'],

    #   biologically related, stepfamily, and inlaws
    7: ['Oh llamas, our family relationship is an absolute mess!',
        'It\'s very complicated.',
        'Bit of an odd family...']
}

# middle of the notification
#   if this is gendered, let me know if it depends on the speaker's gender ("I") or the listener's ("you")
im_your = 'I\'m your '  # space at the end
im_also_your = 'I\'m also your '  # space at the end
#       I'm your second cousin and third cousin once removed. I'm also your brother in law.

# extra flavour, based on their relationship
#   these are all just a bit of fun!
#   you can put whatever you want, or leave it as '' (no spaces) if you don't want to translate it
despised_unrelated = 'I\'m so glad we aren\'t related.'
despised_related = ' Doesn\'t mean I want anything to do with you.'  # space at start
bromance = 'Bro... '  # space at end
birth_parent = 'What? I gave birth to you! '  # space at end
soulmate_unrelated = 'You\'re my soulmate! '  # space at end
soulmate_related = ' I can\'t help being deeply in love with you, though.'  # space at start
promised = 'I\'ve already promised myself to you, so it\'s a bit late to ask... '  # space at end
#       promised = teenagers who have decided to get married when they grow up
engaged = ' ...we\'re still on for the wedding, right?'  # space at start
married = 'Ah yes, the right time to double check is after we get married. '  # space at end
woohooed_recently = 'We JUST woohooed! '  # space at end
woohooed = 'We\'ve woohooed, and now you\'re asking? '  # space at end
first_kiss_recently = 'We literally just had our first kiss. '  # space at end
first_kiss = 'Maybe you should\'ve asked before we kissed? '  # space at end
exchanged_numbers = 'Checking to see if you should keep my number? '  # space at end
its_awkward = 'Things are already weird. '  # space at end
its_complicated = 'This relationship is already complicated. '  # space at end
its_very_awkward = 'Everything\'s already really weird... '  # space at end
its_very_complicated = 'This relationship is already SUPER complicated! '  # space at end
flirted = 'We\'ve already been flirting... it\'s a little late to ask. '  # space at end
coworkers = 'We work together. '  # space at end
acquaintances = 'Oh, right, you barely know me. '  # space at end

# TODO: ==== traits ====

