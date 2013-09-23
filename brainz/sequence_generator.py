import game
from random import choice

def generate(maxTrials):
       return gen_seq(maxTrials,[-1]*maxTrials,[0]*3,[False]*3,1,0)

def moveZ(pos,mo):
        if mo == game.Game.G_JUMP:
                return pos
        elif mo==game.Game.G_RIGHT:
                return pos+1
        else:
                return pos-1
        

def gen_seq(maxTrials,moves,counts,tried,zombiePos,pos):
        if pos==maxTrials:#base case
                return moves,False
        else:
                next,tried,err=getNext(zombiePos,tried) 
                if err:
                        return moves,True
                elif counts[next]<maxTrials/3:
                        moves[pos]=next+1
                        counts[next]+=1
                        tried=[False]*3
                        print "Current %s"%moves
                        res,err = gen_seq(maxTrials,moves,counts,tried,moveZ(zombiePos,moves[pos]),pos+1)
                        if not err:
                                return res,False
                return gen_seq(maxTrials,moves,counts,tried,zombiePos,pos)


def getNext(zombiePos,tried):
        possible=[i for i,x in enumerate(tried) if x == False]
        print "get next Tried: %s"%tried
        print "get next pos: %s"%zombiePos
        if len(possible)==0:
                return -1,[True]*3,True
        elif zombiePos==0:
                if game.Game.G_LEFT-1 in possible:
                        del possible[possible.index(game.Game.G_LEFT-1)]
                        tried[game.Game.G_LEFT-1]=True
                if len(possible)==0:
                        return -1,[True]*3,True
        elif zombiePos==2:
                if game.Game.G_RIGHT-1 in possible:
                        del possible[possible.index(game.Game.G_RIGHT-1)]
                        tried[game.Game.G_RIGHT-1]=True
                if len(possible)==0:
                        return -1,[True]*3,True

        print possible
        next=choice(possible) 
        print "next : %i"%(next+1)
        #raw_input('Pause:')
        tried[next]=True
        return next,tried,False






seq,err=generate(30)
print err
print seq
print len([i for i,x in enumerate(seq) if x == 1])
print len([i for i,x in enumerate(seq) if x == 2])
print len([i for i,x in enumerate(seq) if x == 3])
