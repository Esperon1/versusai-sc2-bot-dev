from sc2.bot_ai import BotAI
from sc2.data import Result
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.ids.upgrade_id import UpgradeId
from sc2.unit import Unit


class CompetitiveBot(BotAI):
    """Main bot class that handles the game logic."""

    def __init__(self):
        super().__init__()
        self.sent_action = False
        self.sent_attack = False

    async def on_start(self):
        """
        This code runs once at the start of the game
        Do things here before the game starts
        """
        print("Game started")

        await self.chat_send("Glory to the Swarm!", team_only=False)

        if self.units(UnitTypeId.OVERLORD).exists:
            scout = self.units(UnitTypeId.OVERLORD).first  # Select the first Overlord
            scout.move(self.enemy_start_locations[0])  # Move it to the enemy start location

    async def on_step(self, iteration: int):
        """
        This code runs continually throughout the game
        Populate this function with whatever your bot should do!
        """

        await self.distribute_workers()  # Distribute workers to minerals/gas
        if not self.structures(UnitTypeId.SPAWNINGPOOL).exists:
            if self.can_afford(UnitTypeId.SPAWNINGPOOL):  # good practice to check if we can afford before building
                await self.build(
                    UnitTypeId.SPAWNINGPOOL,
                    near=self.townhalls.first,
                    max_distance=20,
                )

        if (self.supply_left < 3
                and self.already_pending(UnitTypeId.OVERLORD) == 0
                and self.can_afford(UnitTypeId.OVERLORD)):
            self.train(UnitTypeId.OVERLORD)

        if not self.structures(UnitTypeId.EXTRACTOR):
            geysers = self.vespene_geyser.closer_than(10.0, self.townhalls.first)
            if self.can_afford(UnitTypeId.EXTRACTOR) and self.workers.amount > 0 and geysers.exists:
                self.workers.random.build_gas(target_geysir=self.vespene_geyser.closest_to(self.townhalls.first))

        if self.structures(UnitTypeId.SPAWNINGPOOL).ready.exists:
            if (self.can_afford(UpgradeId.ZERGLINGMOVEMENTSPEED)
                    and self.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED) == 0):
                await self.chat_send("Researching Zergling Speed. Now I can run faster!",
                                     team_only=False) if not self.sent_action else None
                self.research(UpgradeId.ZERGLINGMOVEMENTSPEED)
                self.sent_action = True

            if self.larva.exists and self.can_afford(UnitTypeId.ZERGLING):
                self.train(UnitTypeId.ZERGLING, self.larva.amount,
                           closest_to=self.townhalls.first.position)

        if self.units(UnitTypeId.ZERGLING).ready.exists and self.units(
                UnitTypeId.ZERGLING).amount == 12:
            await self.chat_send("All Zerglings are ready! Attacking now!",
                                 team_only=False) if not self.sent_attack else None
            self.sent_attack = True

            for zergling in self.units(UnitTypeId.ZERGLING):
                zergling.attack(self.enemy_start_locations[0])

    async def on_building_construction_complete(self, unit: Unit):

        if unit.type_id == UnitTypeId.EXTRACTOR:
            workers = self.workers.filter(lambda w: not w.is_carrying_vespene)

            for worker in workers:
                worker.gather(unit)

    async def on_end(self, result: Result):
        """
        This code runs once at the end of the game
        Do things here after the game ends
        """
        print("Game ended.")
