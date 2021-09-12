# don't rename any of these files!

# ==== your details ====

# if there are any translations that need more complex logic, this is the value i'll test for before running other code
lang = 'EN'
# the name of your language, in that language
lang_name = 'English'
# name(s) of translators. "a, b, and c" will appear in the starting notif as "translated by: a, b, and c"
name = 'riv'

# ==== often used (high priority) ====

and_ = 'and'
and__ = f' {and_} '

# start of the main part of the "are we related?" notification. has space at the end
#   if this is gendered, let me know if it depends on the speaker's gender ("I") or the listener's ("you")
# also for the "are you related to this sim" notif (1st and 3rd person)
# also for the sim lookup (2nd and 3rd person)
x_is_ys = {
    '1.2': 'I\'m your ',
    '1..2': 'I\'m also your ',
    '1.3': ('I\'m his ', 'I\'m her '),
    '1..3': ('I\'m also his ', 'I\'m also her '),
    '2.3': ('You\'re his ', 'You\'re her '),
    '2..3': ('You\'re his ', 'You\'re her ')
}
#       I'm your second cousin and third cousin once removed. I'm also your brother in law.

