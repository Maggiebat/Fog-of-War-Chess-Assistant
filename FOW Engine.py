import chess
import chess.engine
import darkchess
import typing
import re
import bidict
import time

engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\17749\PycharmProjects\pythonProject3\stockfish\stockfish-windows-x86-64-avx2.exe")
board = chess.Board()
fens=[board.fen()]
pieceLocations={}
pieceNames=["P1","P2","P3","P4","P5","P6","P7","P8","Q","K","R1","R2","B1","B2","N1","N2"]
pieceLocations={"P1":"a2","P2":"b2","P3":"c2","P4":"d2","P5":"e2","P6":"f2","P7":"g2","P8":"h2","Q":"d1","K":"e1","R1":"a1","R2":"h1","B1":"c1","B2":"f1","N1":"b1","N2":"g1"}
pieceLocations=bidict.bidict(pieceLocations)
fenDups={}
fenDups[fens[0]]=True


while not board.is_game_over():
    #input("Press Enter to continue...")
    rDict={}
    nList=[]
    for i in fens:
        x = chess.Board(i)
        for j in x.legal_moves:
            j2 = str(x.san(j))
            x.push(j)
            d=False
            while d==False:
                try:
                    s = engine.analyse(x, chess.engine.Limit(time=0.001))["score"].white()
                    d=True
                except Exception as e:
                    print(str(e))
                    engine=1
                    time.sleep(1)
                    engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\17749\PycharmProjects\pythonProject3\stockfish\stockfish-windows-x86-64-avx2.exe")
                    
            if s.is_mate()==False:
                s=int(str(s))
                x.push(chess.Move.null())
                #weight to extra move avaliability ~= visibility
                c = 0
                for q in x.legal_moves:
                    c = c + 1
                x.pop()
                s = s + c
            else:
                s=-100000
            try:
                if s<rDict[j]:
                    rDict[j] = s
            except:
                try:
                    board.parse_san(j2)
                    nList.append(j)
                    rDict[j] = s
                except:
                    pass
            x.pop()
    hs=-100000
    dMove=""
    for i in nList:
        if hs<rDict[i]:
            dMove=i
            hs=rDict[i]


            #add key:move value:score to rDict if smaller than current value

    resultm = dMove
    board.push(resultm)
    pieceLocations[pieceLocations.inverse[str(resultm)[0:2]]]=str(resultm)[2:4]
    #update piece locations



    #info = engine.analyse(board, chess.engine.Limit(time=0.01))
    result = engine.play(board, chess.engine.Limit(time=0.001))
    print(board)
    board.push(result.move)
    print("\n")
    print(board)
    print(board.pseudo_legal_moves)
    print(rDict[dMove])
    for i in range(len(fens)):
        x=(chess.Board(fens[0]))
        x.push(resultm)
        fens[0]=x.fen()
        mList=chess.Board(fens[0]).legal_moves
        for j in mList:
            y=chess.Board(fens[0])
            y.push(j)
            #duplicates
            """
            try:
                fenDups[y.fen()]=True
            except:
                fenDups[y.fen()]=True
                    """
            fens.append(y.fen())
        #del fenDups[fens[0]]
        fens.pop(0)

    #generate known square values to compare to theoretical boards
    ioff = 0
    knownS=[]
    for j in board.legal_moves:
        x = str(j)[2:4]
        t = str(board.piece_at(chess.square(int(ord(x[0]) - 97), int(x[1]) - 1)))
        knownS.append([chess.square(int(ord(x[0]) - 97), int(x[1]) - 1),t])

    #deal with pawn vision

    for i in pieceNames:
        if i[0]!="P":
            continue
        else:
            square = chess.square(int(ord(pieceLocations[i][0])) - 97, int(pieceLocations[i][1]) - 1)
            fsquare = square + 8
            if str(board.piece_at(fsquare)).islower()==True and int(fsquare)<64:
                print("yay")
                knownS.append([fsquare,"Some"])
            if int(square) % 8 != 0:
                dlsquare = square + 7
                if str(board.piece_at(dlsquare)) == "None":
                    knownS.append([dlsquare, "None"])
            if int(square)%8!=7:
                drsquare=square+9
                if str(board.piece_at(drsquare))=="None":
                    knownS.append([drsquare,"None"])


    #deal with self piece taken
    c=0
    for i in pieceNames:
        square=chess.square(int(ord(pieceLocations[i][0])) - 97, int(pieceLocations[i][1])-1)
        if str(board.piece_at(square)).islower():
            pieceNames.pop(c)
            c-=1
            del pieceLocations[i]
            knownS.append([square,"Some"])
        c+=1

    #check known squares
    for i in range(len(fens)):
        pas=True
        i=i-ioff
        for j in knownS:
            #make double sure later
            r = str(chess.Board(fens[i]).piece_at(j[0]))
            if j[1]!=r and j[1]!="Some":
                pas=False
                break
            elif j[1]=="Some" and (r=="None" or r.isupper()):
                pas=False
                break

        if pas==False:
            fens.pop(i)
            ioff+=1
    print(len(fens))
    #for i in board.pieces(chess.PAWN,chess.WHITE):
        #print(i)
engine.quit()

