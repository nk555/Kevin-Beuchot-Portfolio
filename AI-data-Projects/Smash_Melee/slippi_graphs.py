import pymongo as mdb
import slippi as slp
import numpy as np
import matplotlib.pyplot as plt

def print_trajectories(db, characters, move, time):
    response=db.stats.find({"stat_type":"Trajectories", "character_1":characters[0], "character_2":characters[1], "move":move, "time":time})
    response=list(response)[0]
    for i in range(len(response["trajectory_1"])):
        t1=np.array(response["trajectory_1"][i])
        t2=np.array(response["trajectory_2"][i])
        fig= plt.figure()
        ax=fig.add_subplot()
        ax.set_xlim((-150,150))
        ax.set_ylim((-100,100))
        ax.scatter(t1.T[0], t1.T[1], c=[i for i in range(len(t1.T[0]))], cmap="Blues", marker="s", alpha=0.25)
        ax.scatter(t2.T[0], t2.T[1], c=[i for i in range(len(t2.T[0]))], cmap="Reds", marker="s", alpha=0.25)
        plt.savefig("plots/"+characters[0]+"_"+characters[1]+"_"+move+"_"+"trajectory"+str(i)+".png")
        plt.close(fig)