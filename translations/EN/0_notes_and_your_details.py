# don't rename any of these files!

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
