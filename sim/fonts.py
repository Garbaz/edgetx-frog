from PIL import Image
D='/tmp/edgetx/radio/src/fonts/std/'
# name: (file, cell width, step rows, glyph height)
SPEC={'SML':('font_04x06.png',5,7,6),'STD':('font_05x07.png',5,8,7),'MID':('font_08x10.png',8,12,12),'DBL':('font_10x14.png',10,16,16)}
class Font:
    def __init__(s,name):
        f,s.cw,s.step,s.h=SPEC[name]; s.name=name
        im=Image.open(D+f).convert('L'); s.im=im; s.per=im.size[0]//s.cw
    def glyph(s,c):
        g=ord(c)-32; r,cidx=divmod(g,s.per); x0=cidx*s.cw; y0=r*s.step
        cols=[]
        for i in range(s.cw):
            col=[s.im.getpixel((x0+i,y0+j))==0 for j in range(s.step)]
            if all(col): continue          # unused column marker (0xff)
            cols.append(col)
        return cols
    def width(s,c): return len(s.glyph(c))
    def textw(s,t): return sum(s.width(c)+1 for c in t)
FONTS={n:Font(n) for n in SPEC}
if __name__=='__main__':
    for n,f in FONTS.items():
        print(n, 'h',f.h, ' '.join(f'{c}:{f.width(c)}' for c in '0123456789%:. -ACDEFGHILMNORSTVWXYZ!'))
        print('   "100%"', f.textw('100%'), '"ACRO"',f.textw('ACRO'),'"ANGLE"',f.textw('ANGLE'),'"HORIZON"',f.textw('HORIZON'),'"FAILSAFE"',f.textw('FAILSAFE'),'"POCKET"',f.textw('POCKET'),'"DRONE"',f.textw('DRONE'))
