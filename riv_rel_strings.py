import enum

# notes:
#   the things that you want to replace are between ''
#   if you have an apostrophe ('), you need to write it as \'
#   variables (names, numbers, relations) will be inserted into sentences wherever {} is
#   some of these need a space at the start and/or end (if so, there'll be a comment next to it)
#   some of these need a line break - shown by \n - at the start and/or end (will also be in comments)
#   don't translate command or file names (basically anything starting with "riv_")
#   please let me know if
#       something doesn't quite work in your language
#           e.g. "step-parent" is a completely different word and not just "step" + "parent"
#           something is gendered in your language that isn't gendered in English
#       you need more context
#       the variables added in with {} will be in a different order than they are in English

# ==== often used (HIGH PRIORITY) ====
and_ = ' and '  # space at start and end

# ==== command outputs (MEDIUM PRIORITY) ====

# the variable name relates to the command, e.g. get_parents_0 is a string for riv_get_parents
get_parents_0 = '{}\'s parents not found'
# 		Bob's parents not found
get_parents_1 = '{} {} is {}\'s parent'
# 		Bob Pancakes is Iggy's parent

get_children_0 = '{}\'s children not found'
# 		Maple's children not found
get_children_1 = '{} {} is {}\'s child'
# 		Iggy Pancakes is Bob's child

get_ancestors_0 = '{}\'s ancestors not found'
# 		Bob's ancestors not found
get_ancestors_1 = '{} {} is {} {}\'s ancestor, {} generation back'
# 		Bob Pancakes is Iggy Pancakes's ancestor, 1 generation back
get_ancestors_2 = '{} {} is {} {}\'s ancestor, {} generations back'
# 		Bob Pancakes is Maple Pancakes's ancestor, 2 generations back

get_descendants_0 = '{}\'s descendants not found'
# 		Maple's descendants not found
get_descendants_1 = '{} {} is {} {}\'s descendant, {} generation forward'
# 		Iggy Pancakes is Bob Pancakes's descendant, 1 generation forward
get_descendants_2 = '{} {} is {} {}\'s descendant, {} generations forward'
# 		Maple Pancakes is Bob Pancakes's descendant, 2 generations forward

get_direct_rel_0 = 'no direct rel found between {} and {}'
#       no direct rel(ationship) found between Bob and Bella
get_direct_rel_1 = '{} {} is {} {}\'s {}.'
#       Bob Pancakes is Iggy Pancakes's father.

get_sib_strength_0 = '{} is {}.'
#       Bob is Bob.
#       appears if you use riv_get_sib_strength and enter the same name twice
get_sib_strength_1 = '{} and {} are full siblings.'
#       Maple and Syrup are full siblings. [two shared parents]
get_sib_strength_2 = '{} and {} are half siblings.'
#       Maple and Syrup are half siblings. [one shared parent]
get_sib_strength_3 = '{} and {} are not siblings.'
#       Maple and Syrup are not siblings. [no shared parents]
get_sib_strength_4 = 'something went wrong: sib_strength is {} when it should be 0, 0.5, or 1'
#       you don't need to translate "sib_strength", and the value in {} will be an unexpected number

get_indirect_rel_0 = '{} {} is {} {}\'s {} (relation found via {} {})'
#       Maple Pancakes is Syrup Pancake's half sister (relation found via Iggy Pancakes)
get_indirect_rel_1 = '{} {} is {} {}\'s {} (relation found via {} {} and {} {})'
#       Maple Pancakes is Syrup Pancake's sister (relation found via Iggy Pancakes and Orange Pancakes)
get_indirect_rel_2 = 'no indirect rel found between {} and {}'
#       no indirect rel(ation) found between Maple and Syrup

consang_0 = 'consanguinity between {} and {} is {}%'
#       consanguinity between Bob and Iggy is 50%
consang_1 = 'consanguinity: {}%'

is_eligible_couple_0 = 'mate, that\'s just being single with extra steps'
#       appears if you try to check if a sim could be in a relationship with themself
#       doesn't need to be exact, just something like "this is the same sim"
is_eligible_couple_1 = '{} and {} are not an eligible couple: they are directly related'
is_eligible_couple_2 = '{} and {} are not an eligible couple: over the consanguinity limit'
#       or "they are too closely related"
is_eligible_couple_3 = '{} and {} are an eligible couple with your settings!'

# for the main riv_rel command
rel_0 = '{} {} is {} {}'
#       Bob Pancakes is Bob Pancakes
#       entered the same sim twice
rel_1 = '{} is {}\'s {}'
#       Iggy is Bob's son
rel_2 = '{} and {} are not related.'
#       Bob and Bella are not related.

rel_rand_0 = 'relation with: {} {}'
#       relation with: Bob Pancakes

rel_rand_rand_0 = 'sims: {} {} and {} {}'
#       sims: Bob Pancakes and Bella Goth

rel_all_0 = 'relatives found for {}: {}'
#       relatives found for Bob Pancakes: 3

# TODO: riv_help line 3545 onwards

# ==== json command outputs (LOW PRIORITY) ====

# things used across multiple commands
all_done = 'all done'
#       [riv_save: all done]
#       appears when a command is done running

save_0 = 'the current sim time is {}, formatted as {}'
save_1 = '[this number appears with any sims that were added/updated this time]'
save_2 = 'saved sims.'
save_3 = 'saved parent rels. '  # space at end
save_4 = '\nif you\'re not using riv_auto, then to use these relations in riv_rel, type the following: '
#               \n at start, space at end; after this it says the command needed, e.g. "riv_load xyz"

load_0 = 'loaded in parent rels and {} sim mini-infos. '  # space at end
load_1 = '\nshowing a random sim and their parents:'  # \n at start
load_2 = 'an error occurred: '  # space at end
load_3 = 'something went wrong while loading these sims and rels; ' \
         'please check that these files exist in the same folder as riv_rel.ts4script:'
load_4 = 'if these files exist then please let me (rivforthesesh / riv#4381) know, and send over any relevant files'

mem_0 = 'showing a random sim:'
mem_1 = 'use riv_load xyz to load in sim info from riv_rel_xyz.json and riv_relparents_xyz.json'
#       leave in "riv_load xyz", "riv_rel_xyz.json", and "riv_relparents_xyz.json" as they are
mem_2 = 'showing a random sim\'s parents:'

clean_0 = 'this file contains {} sim mini-infos, {} of which are culled. cleaning...'
clean_1 = 'after removing duplicates, this file contains {} sim mini-infos.'
clean_2 = 'unculled {} sims'
#       this gives the number of sims that were previously marked as culled, but are no longer marked as culled
clean_3 = 'if you\'re currently using this file, please run riv_update '  # space at end
#       leave in "riv_update "

clear_0 = 'removed temporary file '
#       this only shows up when people use currentsession files, which is off by default
#       you could probably skip translating this and nobody would notice

update_0 = 'this file exists! loading this in'
update_1 = 'running save, clear, then load (updates sim/rel info in mem and .json file)...'

load_cfg_manually_0 = 'loaded in cfg settings for save {}'
#       the value in {} is a save ID as it appears in the save file name, e.g. 00000005
#       leave 'cfg' as is; it refers to the file extension (filename.cfg)
load_cfg_manually_1 = 'currently the game thinks your save ID is 0, or your last save was an MCCC autosave - ' \
                      'this can be fixed by saving the game and then running this command again.'
load_cfg_manually_2 = 'failed to load in cfg settings because of the below exception:'
#       exception = error in code
load_cfg_manually_3 = 'running riv_update {}...'
#       the value in {} is a keyword used for this save
load_cfg_manually_4 = 'there are no cfg settings for this save ID. run "riv_auto xyz" ' \
                      'with whatever keyword you want in place of xyz to set this up for this save ID.'

auto_0 = 'no .cfg file found. creating one...'
auto_1 = 'updating settings for Slot_{}.save to riv_rel - individual save settings.cfg...'
#       do not translate "Slot_{}.save" or "riv_rel - individual save settings.cfg"
auto_2 = 'adding settings for Slot_{}.save to riv_rel - individual save settings.cfg...'
#       do not translate "Slot_{}.save" or "riv_rel - individual save settings.cfg"
auto_3 = 'loading in new .cfg settings...'
auto_4 = 'loading in sims from file...'
auto_5 = 'loading in rels from file...'
auto_6 = 'running save, clear, clean, then load...'
auto_7 = 'the current game slot is an MCCC autosave slot'
auto_8 = 'blocked riv_auto (autosave slots aren\'t specific to saves so this could cause issues)'
auto_9 = 'please manually save your game to another slot and try again'

# ==== starting notif (MEDIUM PRIORITY [there's a lot of text!]) ====
notif_0 = 'failed to load in sims for this save ID: this usually happens when you\'ve just left CAS, ' \
          'you quit a different save without saving and then loaded this one, or you moved/deleted the ' \
          '.json files. \nif you have not (or aren\'t about to) set up auto .json file updates for this ' \
          'save ID please ignore this notification. \notherwise, please save your game and then enter the ' \
          'following into the command line (CTRL+SHIFT+C): \n\nriv_load_cfg_manually'
notif_1 = 'riv_rel issue'
#       notif_1 is the title
notif_2 = 'loaded in settings from riv_rel - individual save settings.cfg ' \
          'for save ID {} and keyword {}.\n\nsim mini-infos: '  # ends with space, followed by a number
notif_3 = 'you\'ve created settings for an MCCC autosave - this won\'t work properly!\n\n' \
          'please save your game to another slot and set up riv_auto again.'
notif_4 = 'riv_rel: auto json issue'
notif_5 = 'you\'ve loaded up an autosave slot! to use riv_auto backups, please save the game to another ' \
          'slot first (if you don\'t want to use riv_auto, you don\'t need to do this)\n\nnumber of sims: '  # space end
notif_6 = 'no sim/rel backups were found for this save - if you\'re expecting to see json file backups or want to ' \
          'set them up, enter riv_auto xyz into the cheat console for a keyword xyz!\n\nnumber of sims: '  # space end
notif_7 = 'you have other files in the same folder as my mod - i would recommend putting all files starting riv_rel ' \
          'in their own subfolder (i.e. in Mods/riv_rel/) if you encounter any additional lag on save/load. '
notif_8 = '\n\nfound MCCC autosave slots (my mod will continue to see the save slot as {} if the actual save slot ' \
          'changes to one of these): {}'
notif_9 = '\n\nyou can see more information and help in the "Research on riv_rel.sim" menu on the computer'
notif_10 = '\n\nyou\'ve downloaded the GT addon without the traits addon - ' \
           'please either download riv_rel_addon_traits or remove riv_rel_addon_GT ' \
           'or you may face glitches with clubs being unable to find my family traits!'
notif_11 = '\n\nif this is the wrong file, run riv_clear, save your game, and run riv_load_cfg_manually.'
notif_12 = '\n\nthank you for using my mod! '
notif_13 = '\n\ntranslated into [language] by [username]'
#       e.g. translated into English by riv; traducido al castellano por riv

# ==== relationships (HIGH PRIORITY) ====
# examples used:
# Bob Pancakes, Iggy Pancakes, Maple Pancakes (Iggy's future kid), Syrup Pancakes (maybe Maple's sibling)

# == direct ==
d_great = 'great'
d_grand = 'grand'
mother = 'mother'
father = 'father'
daughter = 'daughter'
son = 'son'
#       father, grandmother, great-granddaughter, great(x2)-grandson [great-great-grandson]

self = 'self'
#   this one is rarely going to come up, but it'll appear as "Bob Pancakes is Bob Pancakes's self"

# == indirect (non-cousins) ==
half = 'half '  # keep a space at the end
i_great = 'great'
i_grand = 'grand'
aunt = 'aunt'
uncle = 'uncle'
sister = 'sister'
brother = 'brother'
niece = 'niece'
nephew = 'nephew'
#       sister, brother, aunt, granduncle, great-grandniece, great(x2)-grandnephew

# == indirect (cousins) ==
first = 'first '  # keep a space at the end
second = 'second '  # keep a space at the end
third = 'third '  # keep a space at the end
th = 'th '  # keep a space at the end
cousin = 'cousin'
#       first cousin, second cousin, third cousin, 4th cousin, 5th cousin, ...
once = ' once '  # space at start and end
twice = ' twice '  # space at start and end
n_times = ' {} times '  # space at start and end
removed = 'removed'
#       first cousin once removed, first cousin twice removed, first cousin 3 times removed, ...

# == inlaw ==
wife = 'wife'
husband = 'husband'
in_law = ' in law'  # space at start
#       added to the end of the relation, e.g. brother in law, grandmother in law

# == step ==
step = 'step '  # space at end
#       added to the start of the relation, e.g. step sister, step uncle


# ==== tuples (HIGH PRIORITY, but you can set max_n to a low number to have most show up as "n-tuple") ====
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
n_tuple = '{}-tuple '  # space at the end

# ==== notification text (LOW PRIORITY; if you don't want to translate it, just change it to '') ====

# start of the notification
#   you can add or remove strings from each list if you want!
#   this is just flavour text, so it doesn't need to be exact

strings_dict = {

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
