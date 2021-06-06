# don't rename any of these files!

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

gen_diff_list = 'as a list: '  # space at the end; followed by a list of numbers with generational differences
gen_diff_avg = 'the average generational difference is '  # space at the end; average of the numbers above
gen_diff_sign = '(negative means sim_x is higher up in the family tree than sim_y)'
#       i.e. if the generational difference is a negative number, then sim_x is an ancestor of sim_y

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
