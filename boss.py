#Boss/minionfactoryfunctions(keepsbattle.pyclean)
def make_boss():
    #The"type"fieldletsbattle.pydrawbossdifferentlyandapplysummonlogic
    return {
        "name": "Zombie Boss",
        "type": "boss",
        "hp": 170,
        "max_hp": 170,
        "energy": 100,
        "max_energy": 100,
        "summon_every": 5#Every5rounds,bosssummonsminions
    }


def make_minion(i=1):
    #Minionsarespawnedmid-battlebytheboss
    return {
        "name": f"Zombie {i}",
        "type": "minion",
        "hp": 40,
        "max_hp": 40,
        "energy": 20,
        "max_energy": 20
    }

