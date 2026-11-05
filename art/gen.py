import math
W,H=29,21
def blank(): return [[0]*W for _ in range(H)]
def ellipse_outline(g,cx,cy,rx,ry,val=1):
    for a in range(0,3600):
        t=a/1800*math.pi; x=round(cx+rx*math.cos(t)); y=round(cy+ry*math.sin(t))
        if 0<=x<W and 0<=y<H: g[y][x]=val
def disc(g,cx,cy,r,val):
    for y in range(H):
        for x in range(W):
            if (x-cx)**2+(y-cy)**2<=r*r: g[y][x]=val
def frog(awake):
    g=blank(); cx=14
    ellipse_outline(g,cx,13,13.5,6.6)            # head/body
    for ex in (6,22):
        disc(g,ex,5,4.6,0)                       # eyes sit in front of head
        ellipse_outline(g,ex,5,4.4,4.4)
        if awake:
            disc(g,ex,5,2.1,1); g[4][ex-1]=0      # pupil + highlight
        else:
            for y in range(1,5): pass
            disc(g,ex,6.6,4.0,0)                 # clear lower eye
            for x in range(ex-3,ex+4): g[5][x]=1 # closed lid
            g[6][ex-1]=g[6][ex]=g[6][ex+1]=1; g[5][ex]=0  # slight droop
            g[5][ex-4]=g[5][ex+4]=1
    # mouth
    if awake:
        for x in range(7,22):
            y=13+round(1.6*(1-((x-cx)/7.5)**2)); g[y][x]=1
        g[12][6]=g[12][22]=1
    else:
        for x in range(11,18): g[14][x]=1
        g[13][10]=g[13][18]=1
    g[10][12]=g[10][16]=1                          # nostrils
    # front feet
    for fx in (6,22):
        for dx in (-2,0,2): g[H-1][fx+dx]=1
        g[H-2][fx-1]=g[H-2][fx+1]=1
    return g
for name,aw in (('AWAKE',True),('ASLEEP',False)):
    g=frog(aw)
    print(name+' = """'); [print(''.join('#' if v else '.' for v in r)) for r in g]; print('"""')
