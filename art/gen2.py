import math
W,H=27,21
EYE_OPEN = ["..#####..",
            ".#.....#.",
            "#.......#",
            "#...##..#",
            "#..###..#",
            "#..###..#",
            "#.......#",
            ".#.....#.",
            "..#####.."]
EYE_SHUT = ["..#####..",
            ".#.....#.",
            "#.......#",
            "#.......#",
            "#.#...#.#",
            "#..###..#",
            "#.......#",
            ".#.....#.",
            "..#####.."]
def blank(): return [[0]*W for _ in range(H)]
def ell(g,cx,cy,rx,ry):
    for a in range(3600):
        t=a/1800*math.pi; x=round(cx+rx*math.cos(t)); y=round(cy+ry*math.sin(t))
        if 0<=x<W and 0<=y<H: g[y][x]=1
def stamp(g,x0,y0,rows,clear=True):
    for j,r in enumerate(rows):
        for i,c in enumerate(r):
            inside = r.find('#')<=i<=r.rfind('#')
            if c=='#': g[y0+j][x0+i]=1
            elif clear and inside: g[y0+j][x0+i]=0
def frog(awake):
    g=blank(); c=13
    ell(g,c,13,13,7)
    for ex in (1,17): stamp(g,ex,0,EYE_OPEN if awake else EYE_SHUT)
    if awake:
        for x in range(6,21):
            y=13+round(2*(1-((x-c)/7.0)**2)); g[y][x]=1
        g[12][5]=g[12][21]=1
    else:
        for x in range(10,17): g[15][x]=1
        g[14][9]=g[14][17]=1
    g[10][11]=g[10][15]=1
    for fx in (5,21):
        for dx in (-2,0,2): g[H-1][fx+dx]=1
        g[H-2][fx-1]=g[H-2][fx+1]=1
    return g
out=[]
for name,aw in (('AWAKE',True),('ASLEEP',False)):
    g=frog(aw); out.append(name+' = """\n'+'\n'.join(''.join('#' if v else '.' for v in r) for r in g)+'\n"""')
open('frog_gen.py','w').write('\n'.join(out)+'\n'); print('\n'.join(out))
