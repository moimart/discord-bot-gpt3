import fileinput
import discord

class ProfilePic:
    def __init__(self, nicknames):
        _path = "./pics/"
        self.nicknames = nicknames
        self._map = dict()
        for x in nicknames.keys():
            try:
                path = _path + x + ".jpg"
                fp = open(path, 'rb')
                pfp = fp.read()
                self._map[x] = pfp
            except Exception as e:
                print("Error: {}".format(e))
                continue
        
    async def change_picture(self, name, ctx):
        if name not in self._map:
            return
        try:
            await ctx.user.edit(avatar=self._map[name],username=self.nicknames[name])
        except Exception as e:
            print("Error: {}".format(e))
