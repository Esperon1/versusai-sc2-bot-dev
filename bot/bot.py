from sc2.bot_ai import BotAI
from sc2.data import Result
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.ids.upgrade_id import UpgradeId


class CompetitiveBot(BotAI):
    """Main bot class that handles the game logic."""

    def __init__(self):
        super().__init__()

    async def on_start(self):
        """
        This code runs once at the start of the game
        Do things here before the game starts
        """
        print("Game started")

    async def on_step(self, iteration: int):
        """
        This code runs continually throughout the game
        Populate this function with whatever your bot should do!
        """

        # Example: Build a Spawning Pool near the first townhall

        if self.supply_used >= 12 and self.structures(UnitTypeId.SPAWNINGPOOL).amount < 2:
            if self.can_afford(UnitTypeId.SPAWNINGPOOL):  # good practice to check if we can afford before building
                await self.build(
                    UnitTypeId.SPAWNINGPOOL,
                    near=self.townhalls.first,
                    max_distance=20,

                )
        if self.supply_left < 6 and self.can_afford(UnitTypeId.OVERLORD):
            print("Supply low, training Overlord")
            self.train(UnitTypeId.OVERLORD)

        if not self.structures(UnitTypeId.EXTRACTOR):
            if self.can_afford(UnitTypeId.EXTRACTOR) and self.workers.amount > 0:
                print("Building Extractor")
                self.workers.random.build_gas(self.vespene_geyser.closest_to(self.townhalls.first))

            # Making units (Zeglings, Roaches, etc.)
        if (self.structures(UnitTypeId.SPAWNINGPOOL).ready
                and self.larva
                and self.can_afford(UnitTypeId.ZERGLING)):
            print("Training Zerglings")
            # Make Overlord if supply is low
            self.train(UnitTypeId.ZERGLING,
                       # whatever amount of larva we have, we make that many Zerglings self.larva.amount
                       self.larva.amount,
                       closest_to=self.townhalls.first.position
                       )
        # Attack with Zerglings when we have more than 20
        if self.units(UnitTypeId.ZERGLING).ready and self.units(UnitTypeId.ZERGLING).amount > 20:
            for zergling in self.units(UnitTypeId.ZERGLING):
                zergling.attack(self.enemy_start_locations[0])

    async def on_end(self, result: Result):
        """
        This code runs once at the end of the game
        Do things here after the game ends
        """
        print("Game ended.")
