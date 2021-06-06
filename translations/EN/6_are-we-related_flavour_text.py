# don't rename any of these files!

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
