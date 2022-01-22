import pymongo as mdb
import slippi as slp

def group_will_get_hit(db, characters, time, game_range="ALL"):
    """
    characters a list of two strings. The first one represents the character that will get hit the second one the one that lands it.
    time an integer. It represents the amount of time beofre the attack is done.
    game_range a list of two integers or "ALL". The first integer determines which game we start looking at and second one where we stop. 
    
    This function will group all of the times that character[0] is hit by character[1] and will make a separate document for each move. 
    It will include information like the position of the characters, the states they are in (to possibly analize whiff punishes or dimilsr things).
    """

    if game_range=="ALL":
        game_range=[]
        game_range.append(0)
        game_range.append(db.games.count({}))
    group=db.frames.aggregate([
        {"$match":{
            "$and":[
                {"$and":[{"game":{"$gte":game_range[0]}},{"game":{"$lte":game_range[1]}}]},
                {"$or":[{
                "players.0.character":characters[0], 
                "players.1.character":characters[1], 
                "players.0.will_get_hit_by.time":time},
                {"players.1.character":characters[0], 
                "players.0.character":characters[1], 
                "players.1.will_get_hit_by.time":time}]}
            ]
        }
        },
        {"$project":{"data":{"$cond":{
            "if":{"$eq":[characters[0],{"$arrayElemAt":["$players.character",0]}]},
                "then":{
                    "will_get_hit_by":{"$arrayElemAt":["$players.will_get_hit_by.move",0]},
                    "count":{"$sum":1},
                    "game":"$game",
                    "state_1":{"$arrayElemAt":["$players.state",0]},
                    "state_2":{"$arrayElemAt":["$players.state",1]},
                    "position_1":{"$arrayElemAt":["$players.position",0]},
                    "position_2":{"$arrayElemAt":["$players.position",1]},
                    "relative_position":{"$arrayElemAt":["$players.relative_position",0]},
                    "damage_1":{"$arrayElemAt":["$players.damage",0]},
                    "damage_2":{"$arrayElemAt":["$players.damage",1]},
                    "shield_size":{"$arrayElemAt":["$players.shield_size",0]},
                    "speed_1":{"$arrayElemAt":["$players.speed",0]},
                    "speed_2":{"$arrayElemAt":["$players.speed",1]},
                    "hitstun":{"$arrayElemAt":["$players.hitstun",0]}},
            "else":{
                "$cond":{
                    "if":{"$eq":[characters[0],{"$arrayElemAt":["$players.character",1]}]},
                        "then":{
                            "will_get_hit_by":{"$arrayElemAt":["$players.will_get_hit_by.move",1]},
                            "count":{"$sum":1},
                            "game":"$game",
                            "state_1":{"$arrayElemAt":["$players.state",1]},
                            "state_2":{"$arrayElemAt":["$players.state",0]},
                            "position_1":{"$arrayElemAt":["$players.position",1]},
                            "position_2":{"$arrayElemAt":["$players.position",0]},
                            "relative_position":{"$arrayElemAt":["$players.relative_position",1]},
                            "damage_1":{"$arrayElemAt":["$players.damage",1]},
                            "damage_2":{"$arrayElemAt":["$players.damage",0]},
                            "shield_size":{"$arrayElemAt":["$players.shield_size",1]},
                            "speed_1":{"$arrayElemAt":["$players.speed",1]},
                            "speed_2":{"$arrayElemAt":["$players.speed",0]},
                            "hitstun":{"$arrayElemAt":["$players.hitstun",1]}},
                    "else":None}
            }
        }}
        }},
        {"$group":{
            "_id":{"will_get_hit_by":"$data.will_get_hit_by"},
            "count":{"$sum":"$data.count"},
            "game":{"$push":"$data.game"},
            "game_range":[{"$min":"$data.game"}, {"$max":"$data.game"}],
            "state_1":{"$push":"$data.state_1"},
            "state_2":{"$push":"$data.state_2"},
            "position_1":{"$push":"$data.position_1"},
            "position_2":{"$push":"$data.position_2"},
            "relative_position":{"$push":"$data.relative_position"},
            "damage_1":{"$push":"$data.damage_1"},
            "damage_2":{"$push":"$data.damage_2"},
            "shield_size":{"$push":"$data.shield_size"},
            "speed_1":{"$push":"$data.speed_1"},
            "speed_2":{"$push":"$data.speed_2"},
            "hitstun":{"$push":"$data.hitstun"}}
        },
        {"$project":{
            "_id":0,
            "will_get_hit_by":"$_id.will_get_hit_by",
            "character_1":characters[0],
            "character_2":characters[1],
            "frames_to_hit":str(time),
            "count":1,
            "stat_type":"will_get_hit_stats",
            "game":1,
            "game_range":1,
            "state_1":1,
            "state_2":1,
            "position_1":1,
            "position_2":1,
            "relative_position":1,
            "damage_1":1,
            "damage_2":1,
            "shield_size":1,
            "speed_1":1,
            "speed_2":1,
            "hitstun":1}
        }
    ], allowDiskUse=True)
    db.stats.insert_many(group)



def trajectories(db, characters, move, time, game_range="ALL"):
    if game_range=="ALL":
        game_range=[]
        game_range.append(0)
        game_range.append(db.games.count({}))
    matches=db.frames.aggregate([
        {"$match":{
            "$and":[
                {"$and":[{"game":{"$gte":game_range[0]}},{"game":{"$lte":game_range[1]}}]},
                {"$or":[{
                "players.0.character":characters[0], 
                "players.1.character":characters[1], 
                "players.0.will_get_hit_by.time":time,
                "players.0.will_get_hit_by.move":move},
                {"players.1.character":characters[0], 
                "players.0.character":characters[1], 
                "players.1.will_get_hit_by.time":time,
                "players.1.will_get_hit_by.time":move}]}
            ]
        }
        },
        {"$project":{
            "_id":0,
            "game":1,
            "time":{"$sum":["$frame",time]}
            }
        }
    ])
    games={}
    trajectories={}
    trajectories["stat_type"]="Trajectories"
    trajectories["character_1"]=characters[0]
    trajectories["character_2"]=characters[1]
    trajectories["move"]=move
    trajectories["time"]=time
    trajectories["game_range"]=game_range
    trajectories["game"]=[]
    trajectories["trajectory_1"]=[]
    trajectories["trajectory_2"]=[]
    trajectories["state_1"]=[]
    trajectories["state_2"]=[]
    for match in matches:
        games[match["game"]]=set()
        games[match["game"]].add(match["time"])
    for game in games.keys():
        for frame in games[game]:
            trajectory=db.frames.aggregate([
                {"$match":{
                    "game":game,
                    "$and":[{"frame":{"$gte":frame-time}},{"frame":{"$lte":frame}}]
                }},
                {"$project":{"data":{"$cond":{
                    "if":{"$eq":[characters[0],{"$arrayElemAt":["$players.character",0]}]},
                        "then":{
                            "position_1":{"$arrayElemAt":["$players.position",0]},
                            "position_2":{"$arrayElemAt":["$players.position",1]},
                            "state_1":{"$arrayElemAt":["$players.state",0]},
                            "state_2":{"$arrayElemAt":["$players.state",1]},
                        },
                        "else":{
                            "$cond":{
                                "if":{"$eq":[characters[0],{"$arrayElemAt":["$players.character",1]}]},
                                    "then":{
                                        "position_1":{"$arrayElemAt":["$players.position",1]},
                                        "position_2":{"$arrayElemAt":["$players.position",0]},
                                        "state_1":{"$arrayElemAt":["$players.state",1]},
                                        "state_2":{"$arrayElemAt":["$players.state",0]},
                                    },
                                "else":None
                            }
                        }
                    }
                }}},
                {"$group":{
                    "_id":None,
                    "trajectory_1":{"$push":"$data.position_1"},
                    "trajectory_2":{"$push":"$data.position_2"},
                    "state_1":{"$push":"$data.state_1"},
                    "state_2":{"$push":"$data.state_2"}
                }
                }
            ])
            trajectory=next(iter(list(trajectory)), {"game":None, "trajectory_1":None, "trajectory_2":None, "state_1":None, "state_2":None})
            trajectories["game"].append(game)
            trajectories["trajectory_1"].append(trajectory["trajectory_1"])
            trajectories["trajectory_2"].append(trajectory["trajectory_2"])
            trajectories["state_1"].append(trajectory["state_1"])
            trajectories["state_2"].append(trajectory["state_2"])
    db.stats.insert_one(trajectories)