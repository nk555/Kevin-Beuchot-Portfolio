import pymongo as mdb
import slippi as slp
import argparse
import json
import os

def get_slp(path):
    """
    path str   path to directory containing slippi files.

    returns slippi_files   list of strings to all slippi files.
    """

    _, _, slp_files = next(os.walk(path),(None, None, []))
    slp_files=[path+"/"+f for f in slp_files]
    return slp_files

def slp_to_mongoDB(path, db, state_dict={}, index=0, print_every=None, stop_at=None, start_at=0):
    """
    path str  path contianing slippi games.
    db Mongo Client instance that connects to our database
    Given a path to a slippi file it will open it and convert relevant information to json 
    so that it can be stored in a MongoDB database.
    index is an optional argument used to set the id of our games and not have them coincide
    """
    slp_files=get_slp(path)
    slp_files=slp_files[start_at:]
    count=0
    for f in slp_files:
        count+=1
        index+=1
        game=slp.Game(f)
        player_ports=get_ports(game)
        game_json=slp_game_to_json(game, player_ports, index=index)
        try:
            db.games.update_one({"game":game_json["game"]},{"$set":game_json},upsert=True)
        except:
            pass
        prev_frame_hits=[None,None,None,None]
        hit_land_frames=[None,None]
        for frame in range(game.metadata.duration):
            slp_json, prev_frame_hits, hit_land_frames=slp_frame_to_json(game, frame, player_ports, hit_land_frames=hit_land_frames, prev_frame_hits=prev_frame_hits, state_dict=state_dict, index=index)
            try:
                db.frames.update_one({"game":slp_json["game"], "frame":slp_json["frame"]}, {"$set": slp_json}, upsert=True)
            except:
                pass
        if print_every!= None:
            if count % print_every==0:
                print("Transfered "+str(count)+" slippi files to database.")
        if index==stop_at:
            break

def slp_game_to_json(game, player_ports, index=0):
    """
    game Slippi Game

    return game_json dict  slippi game changed into a json format.
    """
    game_json={}
    player1_json={}
    player2_json={}
    player1=game.start.players[player_ports[0]]
    player2=game.start.players[player_ports[1]]
    game_json["game"]=index
    game_json["duration"]=game.metadata.duration
    player1_json["character"]=str(player1.character).split(".")[1].lower()
    player2_json["character"]=str(player2.character).split(".")[1].lower()
    player1_json["tag"]=player1.tag
    player2_json["tag"]=player2.tag
    player1_json["stocks"]=game.frames[game.metadata.duration-1].ports[player_ports[0]].leader.post.stocks
    player2_json["stocks"]=game.frames[game.metadata.duration-1].ports[player_ports[1]].leader.post.stocks
    if player1_json["stocks"]!=0 and player2_json["stocks"]!=0:
        if game.end.lras_initiator!=None:  #If someone quitted the game
            if player_ports.index(game.end.lras_initiator)==0:
                player1_json["stocks"]=0
            else:
                player2_json["stocks"]=0
        else:
            game_json["timeout"]=True
    game_json["players"]=[player1_json, player2_json]
    return game_json

def slp_frame_to_json(game, frame, player_ports, hit_land_frames=[None,None], prev_frame_hits=None, state_dict={}, index=0):
    """
    game Slippi Game
    index int

    This function generates a json file for a given frame of a slippi game.
    
    returns slp_json   slippi file transformed to json file that will have relevant information transformed
    """
    slp_json={}
    player1_json={}
    player2_json={}
    original_game=game
    game=game.frames[frame]
    player1=game.ports[player_ports[0]]
    player2=game.ports[player_ports[1]]
    slp_json["game"]=index
    slp_json["frame"]=frame
    player1_json["character"]=str(player1.leader.post.character).split(".")[1].lower()
    player2_json["character"]=str(player2.leader.post.character).split(".")[1].lower()
    player1_json["position"]=[player1.leader.post.position.x, player1.leader.post.position.y]
    player2_json["position"]=[player2.leader.post.position.x, player2.leader.post.position.y]
    player1_json["hitstun"]=getattr(player1.leader.post, "hitstun", None)
    player2_json["hitstun"]=getattr(player2.leader.post, "hitstun", None)
    player1_json["jumps"]=player1.leader.post.jumps
    player2_json["jumps"]=player2.leader.post.jumps
    player1_json["direction"]=str(player1.leader.post.direction).split(".")[1].lower()
    player2_json["direction"]=str(player2.leader.post.direction).split(".")[1].lower()
    player1_json["damage"]=player1.leader.post.damage
    player2_json["damage"]=player2.leader.post.damage
    player1_json["shield_size"]=player1.leader.post.shield
    player2_json["shield_size"]=player2.leader.post.shield
    player1_json["lcancel"]=getattr(player1.leader.post, "lcancel", None)
    player2_json["lcancel"]=getattr(player2.leader.post, "lcancel", None)
    player1_json["relative_position"], player2_json["relative_position"]=calc_rel_pos(player1, player2)
    player1_json["state"]=convert_state(player1, state_dict)
    player2_json["state"]=convert_state(player2, state_dict)
    player1_json["state_age"]=player1.leader.post.state_age
    player2_json["state_age"]=player2.leader.post.state_age
    player1_json["inputs"]=convert_inputs(player1)
    player2_json["inputs"]=convert_inputs(player2)
    player1_json["speed"]=calc_speed(player1)
    player2_json["speed"]=calc_speed(player2)

    get_hit=frames_to_get_hit(frame,original_game,player_ports,prev_frame_hits=prev_frame_hits,max_len=300)
    player1_json["will_get_hit_by"]={}
    player1_json["will_get_hit_by"]["time"]=get_hit[0]
    player1_json["will_get_hit_by"]["move"]=get_hit[3]
    player2_json["will_get_hit_by"]={}
    player2_json["will_get_hit_by"]["time"]=get_hit[2]
    player2_json["will_get_hit_by"]["move"]=get_hit[1]

    player1_json["will_land_hit"]={}
    player1_json["will_land_hit"]["time"]=get_hit[2]
    player1_json["will_land_hit"]["move"]=get_hit[1]
    player2_json["will_land_hit"]={}
    player2_json["will_land_hit"]["time"]=get_hit[0]
    player2_json["will_land_hit"]["move"]=get_hit[3]

    player1_json["last_hit_landed"]={}
    if "damage" in str(player2_json["state"]):
        player1_json["last_hit_landed"]["time"]=frame
        hit_land_frames[0]=frame
    else:
        player1_json["last_hit_landed"]["time"]=hit_land_frames[0]
    if player1.leader.post.last_attack_landed!=None and player1.leader.post.last_attack_landed!=0:
        player1_json["last_hit_landed"]["move"]=str(player1.leader.post.last_attack_landed).split(".")[-1].lower()
    else:
        player1_json["last_hit_landed"]["move"]=None
    player2_json["last_hit_landed"]={}
    if "damage" in str(player1_json["state"]):
        player2_json["last_hit_landed"]["time"]=frame
        hit_land_frames[1]=frame
    else:
        player2_json["last_hit_landed"]["time"]=hit_land_frames[1]
    if player2.leader.post.last_attack_landed!=None and player2.leader.post.last_attack_landed!=0:
        player2_json["last_hit_landed"]["move"]=str(player2.leader.post.last_attack_landed).split(".")[-1].lower()
    else:
        player2_json["last_hit_landed"]["move"]=None

    player1_json["last_hit_by"]={}
    if "damage" in str(player1_json["state"]):
        player1_json["last_hit_by"]["time"]=frame
        hit_land_frames[0]=frame
    else:
        player1_json["last_hit_by"]["time"]=hit_land_frames[1]
    if player1.leader.post.last_hit_by!=None and player1.leader.post.last_hit_by!=0:
        player1_json["last_hit_by"]["move"]=str(player1.leader.post.last_hit_by).split(".")[-1].lower()
    else:
        player1_json["last_hit_by"]["move"]=None
    player2_json["last_hit_by"]={}
    if "damage" in str(player2_json["state"]):
        player2_json["last_hit_by"]["time"]=frame
        hit_land_frames[0]=frame
    else:
        player2_json["last_hit_by"]["time"]=hit_land_frames[0]
    if player2.leader.post.last_hit_by!=None and player2.leader.post.last_hit_by!=0:
        player2_json["last_hit_by"]["move"]=str(player2.leader.post.last_hit_by).split(".")[-1].lower()
    else:
        player2_json["last_hit_by"]["move"]=None

    slp_json["players"]=[player1_json,player2_json]

    return slp_json, get_hit, hit_land_frames

def get_ports(game):
    """
    game Slippi Game

    This function takes a game and returns a list of the ports used by the players

    return player_ports
    """
    player_ports=[]
    for i in range(4):
        if game.start.players[i] != None:
            player_ports.append(i)
    return player_ports

def calc_rel_pos(player1, player2):
    """
    player1 slippi Port
    player2 slippi Port

    Given our players we will compute the relative position between themselves.
    returns rel_pos_1, rel_pos_2
    """
    rel_pos_1=((player1.leader.post.position.x-player2.leader.post.position.x)*int(player1.leader.post.direction), player1.leader.post.position.y-player2.leader.post.position.y)
                                                #here we multiply times where player1 is facing to know whether the other player is in front of him or on the back
    rel_pos_2=((player2.leader.post.position.x-player1.leader.post.position.x)*int(player2.leader.post.direction), player2.leader.post.position.y-player1.leader.post.position.y)
    return rel_pos_1, rel_pos_2

def convert_state(player, state_dict):
    """
    player slippi Port
    state_dict dict
    
    Given a player we will convert its current state to a readable state

    return updated player
    """
    if "." not in str(player.leader.post.state):
        return None
    state=str(player.leader.post.state).split(".")[1].replace("_", "").lower()
    state=state_dict.get(state)
    return state

def convert_inputs(player):
    """
    player slippi Port

    Given a player we will convert its input into readable inputs

    return updated player
    """
    inputs={}
    inputs[str(player.leader.pre.buttons.logical).split(".")[1]]=1
    inputs[str(player.leader.pre.buttons.physical).split(".")[1]]=1
    inputs["Joystick"]=player.leader.pre.joystick
    inputs["Cstick"]=player.leader.pre.cstick
    if player.leader.pre.triggers.physical.l>.5 or player.leader.pre.triggers.physical.r>.5:
        inputs["Triggers"]=1

def calc_speed(player):
    """
    player slippi Port

    Given a player we compute its current speed

    return speed
    """
    speed=(player.leader.post.position.x-player.leader.pre.position.x, player.leader.post.position.y-player.leader.pre.position.y)
    return speed
    
def frames_to_get_hit(in_frame,game,player_ports,prev_frame_hits=[None,None,None,None],max_len=300):   #notice that the other way around is useful to know when they land a hit
    """
    in_frame int   current frame we are analyzing
    game Slippi Game
    prev_frame_hits int array    if in_frame is not 0 we will take the output of this function for the last frame
    max_len int   length of frames we lookout for a hit

    This function will take a game and a current frame and analyze next frames to see if a player got hit and when.

    returns player1_frame, player2_frame
    """
    player1_frame=None
    player1_attack=None
    player2_frame=None
    player2_attack=None
    found_1=False
    found_2=False
    if in_frame==0 or"DAMAGE" in str(game.frames[in_frame].ports[player_ports[0]].leader.post.state) or "DAMAGE" in str(game.frames[in_frame].ports[player_ports[1]].leader.post.state):
        #We check if a player gets hit in this frame, if they do then we know we need to update the information otherwise 
        #we can use the information of the previous frame to know when it will get hit.
        in_frame+=1
        for frame in range(max_len):
            if in_frame+frame >= game.metadata.duration:
                break
            current=game.frames[in_frame+frame]
            if "DAMAGE" in str(current.ports[player_ports[0]].leader.post.state) and "WALL_DAMAGE" not in str(current.ports[player_ports[0]].leader.post.state):
                if str(current.ports[player_ports[1]].leader.post.last_attack_landed) !="None":
                    if not found_1:
                        player1_frame=frame
                        player2_attack=str(current.ports[player_ports[1]].leader.post.last_attack_landed).split(".")
                        player2_attack=player2_attack[1].lower()
                        found_1=True
            if "DAMAGE" in str(current.ports[player_ports[1]].leader.post.state) and "WALL_DAMAGE" not in str(current.ports[player_ports[1]].leader.post.state):
                if str(current.ports[player_ports[0]].leader.post.last_attack_landed) !="None":
                    if not found_2:
                        player2_frame=frame
                        player1_attack=str(current.ports[player_ports[0]].leader.post.last_attack_landed).split(".")
                        player1_attack=player1_attack[1].lower()
                        found_2=True
            if found_1 and found_2:
                break
        return [player1_frame, player1_attack, player2_frame, player2_attack]
    else: #Same hit considered as last move
        if prev_frame_hits[0]!= None:
            prev_frame_hits[0]-=1
        if prev_frame_hits[2]!=None:
            prev_frame_hits[2]-=1
        return prev_frame_hits

if __name__=="__main__":
    parser=argparse.ArgumentParser(description="Program to send slippi files into a database")
    parser.add_argument("--database", "-d", type=str, dest="db_uri", help="URI for MongoDB database.")
    parser.add_argument("--path", "-p", type=str, dest="path", help="Path to folder containing slippi games.")
    parser.add_argument("--index", "-i", type=int, dest="index", default=0, help="Game ID to start storing at.")
    parser.add_argument("--states", "-s", type=str, dest="states", help="Path to states dictionary used to convert to readable states.")
    parser.add_argument("--print_every", type=int, dest="print_every", default=None, help="Variable to display how many games have been converted into our database.")
    parser.add_argument("--stop_at", type=int, dest="stop_at", default=None, help="Variable to stop after transfering x amount of files.")
    parser.add_argument("--start_at", type=int, dest="start_at", default=0, help="Variable to decide which file number to start at.")
    args=parser.parse_args()
    index=args.index
    if index==0 and args.start_at!=0:  #I assume that if you do not start at 0 then you want your index to be the same as start_at unless you give a custom index.
        index=args.start_at
    client=mdb.MongoClient(args.db_uri)
    db=client.slippi
    with open(args.states) as json_file: 
        state_dict=json.load(json_file)
    slp_to_mongoDB(args.path, db, state_dict=state_dict[0], index=index, print_every=args.print_every, stop_at=args.stop_at, start_at=args.start_at)
