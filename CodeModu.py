from datetime import timedelta, date, datetime
from matplotlib import pyplot as plt 
import random 

def gametime(games, game_id):
    """Set the first kill time of a game as this game's time,
    Assume that if a game happens cross the 00:00, and one player being marked as a cheater for the second day, 
    I assumed that player is not a cheater for this game."""
    game_time = games[game_id][0][2]
    return game_time

class Motif_judgement:
    """A class to first generate the observer dictionary,
    then make a count of how many of them turns to be a cheater."""

    def __init__(self, games, cheaters):
        """Assume games and cheaters are both in dictionary type,
        create a new observer dictionary,
        and the count for observer-cheater motifs as 0"""
        self.games = games
        self.cheaters = cheaters
        self.observer = dict()
        self.count = 0
      
    def observer_add(self, player_id, game_time):
        """Record the first time a player observed a cheating behaviour, in case that a player 
        observed the cheating behaviour several times. We only record the very first time. """
        if player_id not in self.observer.keys():
            self.observer[player_id] = game_time
        else:
            if game_time < self.observer[player_id]:
                self.observer[player_id] = game_time
          
    def observer_judgement(self):
        """To generate the observer dictionary,
        Key: observer id,
        Value: first observation time"""
        for game_id in self.games.keys(): # iterate over games
            game_time = gametime(self.games, game_id)
            killers = dict() # generate a killer dictionary for one game
            for j in range(len(self.games[game_id])):
                killer_id = self.games[game_id][j][0] 
                death_id = self.games[game_id][j][1] 
                # check whether the killer is cheater
                if (killer_id in self.cheaters.keys()):
                    # only check the lower bound of gametime
                    # As if one cheater is banned, it is impossible that he still can play the game
                    if (game_time >= self.cheaters[killer_id][0]):
                        # Mark the player as observer if he/she is killed by the cheating player.
                        if killer_id not in killers.keys():
                            killers[killer_id] = [death_id]
                            if (death_id not in self.cheaters.keys()) or (game_time < self.cheaters[death_id][0]):
                                self.observer_add(death_id, game_time)
                        else:
                            # if killer killed 1, could enter in and come out with number of kill record:2.
                            # next time we have that cheater, meaning the third kill made by he/she is taking place.
                            if len(killers[killer_id]) < 2:
                                killers[killer_id].append(death_id)
                                if (death_id not in self.cheaters.keys()) or (game_time < self.cheaters[death_id][0]):
                                    self.observer_add(death_id, game_time)
                            else:
                                # At the moment that the cheater killed the third player,
                                # all the record after: non-cheater killer and non-cheater death will be marked as observer
                                # in other word, all the players left will turns to be observer.
                                killers[killer_id].append(death_id)
                                self.observer_add(death_id, game_time)
                                break
            # Once a cheater killed three players
            # anyone left will be count as observe
            if j < len(self.games[game_id])-1:
                for z in range(j+1, len(self.games[game_id])): # all the records after
                    killer_id = self.games[game_id][z][0]
                    death_id = self.games[game_id][z][1]
                    if killer_id not in self.cheaters.keys():
                        self.observer_add(killer_id, game_time)
                    else: 
                        # It is possible that the player is in cheater list
                        # but he/she has not turns to be a cheater at this point
                        if (game_time < self.cheaters[killer_id][0]):
                            self.observer_add(killer_id, game_time)
                    if death_id not in self.cheaters.keys():
                        self.observer_add(death_id, game_time)
                    else: 
                        if (game_time < self.cheaters[death_id][0]):
                            self.observer_add(death_id, game_time)
        return self.observer

    def motif_judgement(self):
        """To return the number of observer-cheater motifs if a observer start cheating 
        within five days since she/he observed a cheating behaviour for the first time. 
        As for the cheating time I regard them start at 00:00, I assume that if observation time 
        and start cheating are on the same date: I do not regard that player as observer-cheater motif. """
        for candidate in self.observer:
            if (candidate in self.cheaters.keys()):
                if (datetime.strptime(self.observer[candidate], '%Y-%m-%d %H:%M:%S.%f') + timedelta(days=5)).date() > (datetime.strptime(self.cheaters[candidate][0], '%Y-%m-%d')).date():
                    if (datetime.strptime(self.observer[candidate], '%Y-%m-%d %H:%M:%S.%f')).date() < (datetime.strptime(self.cheaters[candidate][0], '%Y-%m-%d')).date():
                        self.count +=1
        return self.count


# step 2 
def random_noncheaters(games, cheaters):
    """To randomize players excluding cheaters in a games""" 
    for game_id in games.keys():
        playerlst = []  # the non-cheater player list of a game
        for i in range(len(games[game_id])):
            killer_id = games[game_id][i][0]
            death_id = games[game_id][i][1]
            if killer_id not in cheaters.keys():
                playerlst.append(killer_id)
            else:
                if gametime(games, game_id) < cheaters[killer_id][0]:
                    playerlst.append(killer_id)

            if death_id not in cheaters.keys():
                playerlst.append(death_id)
            else:
                if gametime(games, game_id) < cheaters[death_id][0]:
                    playerlst.append(death_id)

        playerlst = list(set(playerlst))
        substitutelst = playerlst[:]
        random.shuffle(substitutelst)
        substitutedic = dict(zip(playerlst, substitutelst))
        # replacement of players
        for recordno in range(len(games[game_id])):
            if games[game_id][recordno][0] in substitutedic.keys():
                games[game_id][recordno][0] = substitutedic[games[game_id][recordno][0]]
            if games[game_id][recordno][1] in substitutedic.keys():
                games[game_id][recordno][1] = substitutedic[games[game_id][recordno][1]]
    return games