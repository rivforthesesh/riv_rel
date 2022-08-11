Hello!! If you're seeing this, welcome to the mess behind the scenes. I haven't looked at it for a year and I can't guarantee it's understandable (even by me lol, I've been using javascript for the past year so python isn't at the forefront of my mind), but this is from the latest version of the mod (gen 7)

The .ps1 file (run in powershell) will make all of the .ts4script files from .py files - if it doesn't work (maybe a different OS or you have a different python compiler) then what it does is
- compile all .py files (to get .pyc files)
- put the .pyc files into a .zip (note: only put in the .pyc files that would go into one .ts4script)
- rename the .zip file to end with .ts4script (it is literally just a zip file, this is safe to do)

Best of luck if you do want to do anything with this!!

I also recommend joining the creator musings discord, they helped me a lot while I was modding and there are a lot of resources to use: https://discord.gg/qxz5Kn5
