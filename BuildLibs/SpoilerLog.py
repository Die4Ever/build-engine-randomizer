import traceback
from BuildLibs import *

class SpoilerLog:
    def __init__(self, filename):
        self.filename = filename
        self.file = None
        self.currentFile = ''
        self.FinishRandomizingFile()

    def __enter__(self):
        self.file = open(self.filename, 'w')
        self.WriteHeader()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_value:
            text = "".join(traceback.format_exception(exc_type, exc_value, tb))
            self._WriteHtml('error', text)
        self.WriteFooter()
        self.file.close()

    def WriteHeader(self):
        html = """<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Build Engine Randomizer Spoiler Log</title>
    <style>
        body {
            background: #111;
            color: #ddd;
            font-size: 125%;
            padding: 1rem;
        }
        .SetFilename {
            cursor: pointer;
            padding: 1rem;
            border-left: 4px solid;
            border-left-color: #bdb;
        }
        .SetFilename:nth-child(even) {
            border-left-color: #555;
        }
        .FileSection {
            cursor: auto;
            padding: 1rem;
        }
        .collapsed .FileSection {
            display: none;
        }
        .error {
            color: #f44;
        }
    </style>

    <script>
        function ClickFile(e) {
            el = e.currentTarget;
            if(el != e.target) return;
            if(el.classList.contains('collapsed'))
                el.classList.remove('collapsed');
            else
                el.classList.add('collapsed');
        }

        function OnLoad() {
            els = document.body.querySelectorAll('.SetFilename');
            for(var i in els) {
                els[i].onclick = ClickFile;
            }
        }

        document.addEventListener('DOMContentLoaded', OnLoad, false);
    </script>
  </head>
  <body>\n"""
        self.file.write(html)

    def WriteFooter(self):
        html = '\n</body></html>'
        self.file.write(html)

    def write(self, text):
        info(text)
        self._WriteHtml('write', text)

    def _WriteHtml(self, classname, text):
        self.file.write('<div class="'+classname+'">' + text.replace('\n', '<br/>') + '</div>\n')

    def Change(self, var, old, new):
        text = '    ' + var + ' changed from ' + str(old) + ' to ' + str(new)
        trace(text)
        self._WriteHtml('Change', text)

    def AddSprite(self, type, sprite):
        text = '    added ' + type + ' ' + self.DescribeSprite(sprite)
        trace(text)
        #self._WriteHtml('AddSprite', text)

    def DelSprite(self, type, sprite):
        text = '    deleted ' + type + ' ' + self.DescribeSprite(sprite)
        trace(text)
        #self._WriteHtml('DelSprite', text)

    def GetPicnumName(self, picnum: int) -> str:
        valname = None
        if self.gameMapSettings and picnum in self.gameMapSettings.swappableItems:
            valname = self.gameMapSettings.swappableItems[picnum]
        if self.gameMapSettings and picnum in self.gameMapSettings.swappableEnemies:
            valname = self.gameMapSettings.swappableEnemies[picnum]
        if valname:
            return valname + ' ('+str(picnum)+')'
        return str(picnum)

    def DescribeSprite(self, sprite) -> str:
        name = self.GetPicnumName(sprite.picnum)
        # tuple gives parens so it looks better than a list
        pos = tuple(sprite.pos)
        return name + ' ' + str(pos)

    def SwapSprites(self, spritetype, s1, s2):
        text = '    swapping ' + spritetype + ' ' + self.DescribeSprite(s1) + ' with ' + self.DescribeSprite(s2)
        trace(text)
        #self._WriteHtml('SwapSprites', text)

    def ListSprites(self, spritetype, sprites):
        for sprite in sprites:
            text = '    ' + spritetype + ' ' + self.DescribeSprite(sprite)
            self._WriteHtml('ListSprites', text)

    def SpriteChangedTag(self, tagname: str, sprite, tagval):
        # tuple gives parens so it looks better than a list
        pos = str(tuple(sprite.pos))
        tagval = self.GetPicnumName(tagval)
        text = '    set ' + tagname + ' to ' + tagval + ' on trigger (' + str(sprite.picnum) + ') at ' + pos
        trace(text)
        self._WriteHtml('SpriteChangedTag', text)

    # which file is currently being randomized
    def SetFilename(self, filename):
        self.currentFile = filename
        text = 'Starting randomizing file: ' + filename
        debug(text)
        self.file.write(
            '\n<br/><div class="SetFilename collapsed">' + text + '<br/>\n'
            + '(Click to expand and collapse)<br/>\n'
            + '<div class="FileSection">\n'
        )

    def FinishRandomizingFile(self):
        if self.currentFile:
            text = 'Finished randomizing file: ' + self.currentFile
            debug(text)
            self.file.write(
                '<div class="FinishRandomizingFile">' + text + '</div>\n'
                + '</div></div>\n'
            )
        self.currentFile = ''
        self.conSettings = {}
        self.gameMapSettings = {}

    def SetConSettings(self, conSettings):
        self.conSettings = conSettings

    def SetGameMapSettings(self, gameMapSettings):
        self.gameMapSettings = gameMapSettings

