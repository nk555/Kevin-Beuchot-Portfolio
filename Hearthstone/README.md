# Hearthstone

This is a project I have been wanting to work on for a while. Hearthstone is a card game I have played for many years and which I really enjoy. 

The first idea to pop up would be likely to train an agent to play the game, and while I might end up creating such an agent it is not my main focus.

My main focus on this project is to make a deck generator. The objective would be that it generates top tier decks (decks with the best results).

Currently I will work on two slightly different approaches and compare their results.

1. Use data from decks existing already and their different winning percentages to classify decks by score and by style. Hearthstone players would usually classify decks, cards and turns as different styles. These being aggro, tempo, midrange, control or value.
Although I could try to do these classifications by hand I want to train a network whihc classifies properties of the cards and then determines scores. For example setting up certain common scenarios like facing two huge minions, facing 5 small minions, an empty board, etc. and using the impact they made on the turn as a variable and then use unsupervised classification algorithms to get different clusters.
Then the idea would be to use certain generator (possibly a GAN) that could take on different styles and work on this assumption to generate a deck with a high score on this particular style.

2. This idea is similar in most of the process but the way to score decks instead of coming from player's data would be from a trained agent.
Using Sabberstone (an app made by the hearthsim team) we are able to make agents play the game and train them. We would train an AI to play.
An important part of what I would like to implement in this AI is to augment the data of its reward functions or Q functions, to contain style. 
As sometimes the same action but being played in a different style would give different scores and this is more important for another step which is how to complete the empty spaces.
By empty spaces I mean that it is unlikely we can train the agent for all actions and all possible states of a game.
So part of the decision the agent will do is that it will have an action state that includes style and it will assign scores to states and actions not seen before based on the nearest neighbors on the state times action space.
I made this decision based on what I as an experienced player (reached legend multiple times around top 1000) would describe my process when playing the game is and also of some experience hearing other good players.

Comments: One of the things I noticed while thinking about the game is how hard it is to not put in bias of what I know about the game, especially in the way of the metagame. 
Any experienced player will know how the metagame affects which decks are considered good. So much that even without introducing new cards decks that seemed great are suddenly bad in the metagame because they are bad against the top played decks and might win agains other decks.
This is something that I consider might happen when training an agent ignorat of the metagame where it might develop its own metagame that does not translate well. 
However, this is not really an issue. But is more of my game design/analysis part of me coming into play as I came to the realization that in most games what we consider to be best is not neccesarily the best but is the collectively best known which we don't realize how far from optimal it could be.

To end it I just want to say that it looks like something interesting could be said in the case that all of these agents had good abilities. 
For example if we could see that output decks do not work well but then we somehow feed it the information of the metagame it develops better or maybe makes specific tweaks could tell more about how we think about the process of a metagame as an evolutionary process.