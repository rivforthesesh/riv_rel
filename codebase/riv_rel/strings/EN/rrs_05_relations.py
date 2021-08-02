# don't rename any of these files!

# ==== relationships (high priority) ====
# examples used:
# Bob Pancakes, Iggy Pancakes, Maple Pancakes (Iggy's future kid), Syrup Pancakes (maybe Maple's sibling)

# == direct ==
# main bit works off of the number of generations away from the self
# add numbers as you need them
d = direct_rels = {
    -2: ('grandfather', 'grandmother'),
    -1: ('father', 'mother'),
    0: 'self',  # this one is very rarely going to come up, but it'll appear as "Bob Pancakes is Bob Pancakes's self"
    1: ('son', 'daughter'),
    2: ('grandson', 'granddaughter'),
}
# prefixes used to continue patterns - the below works like this
#   if they're further up the tree than the minimum number above (d_anc), we add one d_great for each gen
#   if they're further down the tree than the max number above (d_des), we add one d_great for each gen
d_great = 'great'
d_anc = min(d.keys())   # change to a fixed number if the pattern would be applied to a non-extreme
d_des = max(d.keys())   # change to a fixed number if the pattern would be applied to a non-extreme

# == indirect ==
# shows this relation is through one ancestor, rather than a couple, e.g. you share one parent with your half-sibling
half = 'half'
# use for word order - the p(rrs.half) just makes sure it uses 'half' from above
half_rel = '{half} {rel}'

# = siblings of direct rels / direct rels of siblings =
# add numbers as you need them
i1 = indirect_rels_1 = {
    -2: ('granduncle', 'grandaunt'),    # your grandparent's sibling
    -1: ('uncle', 'aunt'),              # your parent's sibling
    0: ('brother', 'sister'),           # your sibling
    1: ('nephew', 'niece'),             # your sibling's child
    2: ('grandnephew', 'grandniece'),   # your sibling's grandchild
}
# prefixes used to continue patterns - put the rules for it in comments
i_great = 'great'   # moves one generation away from self, e.g. great-grandniece, great(x2)-grandniece...
i1_anc = min(i1.keys())   # change to a fixed number if the pattern would be applied to a non-extreme
i1_des = max(i1.keys())   # change to a fixed number if the pattern would be applied to a non-extreme

# = cousins =  TODO: modify for Spanish-like version
cousin_up = 'cousin'    # any cousin relation that is a higher generation than you
cousin = 'cousin'       # any cousin relation that is on the same generation as you
cousin_down = 'cousin'  # any cousin relation that is a lower generation than you

# horizontal distance on family tree
# add numbers as you need them
h = horizontal_modifier = {
    1: 'first',         # closest shared relatives are grandparents
    2: 'second',        # closest shared relatives are great-grandparents
    3: 'third',         # closest shared relatives are great-great-grandparents
}


#   continued pattern for nth
#       please let me know when each suffix is used
#           e.g. 4th, 5th, ..., 11th, 12th, 13th, ..., 21st, 22nd, 23rd cousin...
#       i'll rewrite the function below as needed
def th(n):
    # words
    if n in h.keys():
        return h[n]  # has a word for it above

    # numbers
    if n % 10 == 1 and n % 100 != 11:
        return f'{n}st'  # ends in 1 but not in 11
    elif n % 10 == 2 and n % 100 != 12:
        return f'{n}nd'  # ends in 2 but not in 12
    elif n % 10 == 3 and n % 100 != 13:
        return f'{n}rd'  # ends in 3 but not in 13
    else:
        return f'{n}th'


nth_cousin = '{nth} {cousin}'   # use for word order

# vertical distance on family tree
# add numbers as you need them
v = vertical_modifier = {
    -2: 'twice removed',    # grandparent of your nth cousin
    -1: 'once removed',     # parent of your nth cousin
    0: '',                  # nth cousin
    1: 'once removed',      # child of your nth cousin
    2: 'twice removed',     # grandchild of your nth cousin
}
# used to continue patterns - if there's a number
m_times = '{num} times removed'
#       first cousin once removed, first cousin twice removed, first cousin 3 times removed, ...

nth_cousin_m_times_removed = '{nth_cousin} {m_times_removed}'  # use for word order

# == inlaw ==
spouse = ('husband', 'wife')
in_law = 'in law'
rel_in_law = '{rel} {in_law}'
#       e.g. brother in law, grandmother in law

# == step (this bit is really low priority since step rels very rarely show up) ==
step = 'step'
step_rel = '{step} {rel}'
#       e.g. step sister, step uncle

# ==== tuples (high priority, but you can set max_n to a low number to have most show up as "n-tuple") ====
#   used to show a relation is repeated
#   I've done this in English up to 100, and above that it just says something like "101-tuple"
#       used https://cosmosdawn.net/forum/threads/if-1-single-2-double-n-tuple-n-tuples.2735/
#       when you go above 10, you add a prefix for the ones bit, e.g. "12 times" is duo(2) + decuple(10)
#   you can set a maximum below if you don't want to bother beyond a certain value; don't go above 100
max_n = 100  # for any number n that is greater than this, it will just display "n-tuple"

# if this varies by gender I need to know!!!

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

# if the number is too high (above max_n), just use the number
n_tuple = '{n}-tuple '  # space at the end
