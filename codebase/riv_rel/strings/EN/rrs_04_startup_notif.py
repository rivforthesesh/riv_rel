# don't rename any of these files!

# ==== starting notif (medium [there's a lot of text, but everyone using .json files will see this]) ====

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
