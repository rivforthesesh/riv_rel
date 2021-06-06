# don't rename any of these files!

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
