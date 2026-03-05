def make_boss():
    #Factory function returning boss stats in a consistent dictionary format for the battle system
    return {
        "name": "Zombie Boss",
        "type": "boss",
        "hp": 250,
        "max_hp": 250,
        "energy": 100,
        "max_energy": 100,
        "summon_every": 5
    #Controls how often the boss summons minions (every N rounds)
    }


def make_minion(i=1):
    #Factory function for minions summoned during the boss fight(i=1):
    return {
        "name": f"Zombie {i}",
        "type": "minion",
        "hp": 40,
        "max_hp": 40,
        "energy": 20,
        "max_energy": 20
    }