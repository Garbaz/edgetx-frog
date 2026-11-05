import re
src=open('/home/tobi/tmp/fpvtune/pocket/SCRIPTS/TELEMETRY/frog.lua').read()
awake=re.search(r'local FROG_AWAKE = \{(.*?)\n\}',src,re.S).group(1)
rows=re.findall(r'"([.#]+)"',awake)
SPIRAL_A=["..#####..",
          ".#.....#.",
          "#..###..#",
          "#.#...#.#",
          "#.#.#.#.#",
          "#.#..##.#",
          "#..#....#",
          ".#..###.#"[:9],
          "..#####.."]
SPIRAL_A[7]=".#.....#."
def mirror(e): return [r[::-1] for r in e]
def flipv(e): return e[::-1]
SPIRAL_B=flipv(mirror(SPIRAL_A))           # 180 degree turn
def frame(eyeL,eyeR):
    g=[list(r) for r in rows]
    for j in range(9):
        for i in range(9):
            g[j][1+i]=eyeL[j][i]; g[j][17+i]=eyeR[j][i]
    for j in (12,13,14,15):                 # wipe smile
        for i in range(4,23): g[j][i]='.'
    for i in range(7,20):                   # wobbly mouth
        g[13 if (i//2)%2==0 else 14][i]='#'
    return [''.join(r) for r in g]
A=frame(SPIRAL_A,SPIRAL_B); B=frame(SPIRAL_B,SPIRAL_A)
for n,f in (('FROG_DIZZY_A',A),('FROG_DIZZY_B',B)):
    print(f'local {n} = {{'); [print(f'  "{r}",') for r in f]; print('}\n')
