from collections import deque

from game.boss import Boss
from game.character import Character
from game.enemy import Enemy
from game.entity_item import EntityItem
from game.player import Player
from game.utils import Utils
from mgl2d.graphics.frames_store import FramesStore
from mgl2d.math.rect import Rect
from mgl2d.math.vector2 import Vector2

INTRO_DEBUG = 0
DEBUG = 0


# noinspection PyAttributeOutsideInit
class World:
    MAX_ENEMIES_ON_SCREEN = 1
    MAX_CORPSES_ON_THE_FLOOR = 30

    SCENE_NONE = 0
    SCENE_TITLE = 1
    SCENE_GAME = 10
    SCENE_GAME_OVER = 20
    MAX_ENEMY_FORCE = 6

    BOSS_THRESHOLD = 5000

    def __init__(self, bounds, debug=0):
        self.scene = self.SCENE_TITLE

        self.bounds = bounds
        self.debug = debug

        self.window_x = 0
        self.window_y = 0

        self.items = list()
        self.characters = list()
        self.players = set()
        self.enemies = set()
        self.corpses = deque(maxlen=self.MAX_CORPSES_ON_THE_FLOOR)

        self.item_frames = FramesStore()
        self.item_frames.load('resources/sprites/items', 'sprites.json')

        pizza = EntityItem(self, self.item_frames, 'pizza', 250, 220)
        self.items.append(pizza)

        self.enemy_frames = [
            FramesStore()
        ]
        self.enemy_frames[0].load('resources/sprites/cody', 'sprites.json')
        # self.enemy_frames[1].load('resources/sprites/bred', 'sprites.json')
        # self.enemy_frames[2].load('resources/sprites/jay', 'sprites.json')
        # self.enemy_frames[3].load('resources/sprites/jake', 'sprites.json')

        self.boss_frames = [
            FramesStore()
        ]
        # self.boss_frames[0].load('resources/sprites/damnd', 'sprites.json')
        # self.boss_sound = pygame.mixer.Sound('resources/sounds/boss_sound.wav')

        self.intro_timer = 0
        self.intro_enemy = 0
        self.intro_player = 0
        self.intro_state = 0

        self.game_over_timer = 0
        self.game_over_state = 0

        self._score = 0
        self.boss_spawn_point = 0
        self.boss_spawn_count = 0

    def set_stage(self, stage):
        self.stage = stage

    def restart_game(self):
        # This is not enough, you need to re-init players
        self.init(self.bounds, self.stage, self.debug)

    def skip_intro(self):
        if self.intro_state < 30:
            self.spawn_initial_enemies()
            for ch in self.characters:
                ch.say('', time=0)
        self.begin()

    def begin(self):
        self.scene = self.SCENE_GAME
        for character in self.characters:
            character.begin()

    def add_player(self, player):
        self.players.add(player)
        self.characters.append(player)
        player.position.x = self.stage.entity_pos('player1').x
        player.position.y = self.stage.entity_pos('player1').y
        return player

    def add_enemy(self, enemy):
        self.enemies.add(enemy)
        self.characters.append(enemy)

    def remove_character(self, character):
        self.enemies.discard(character)
        self.players.discard(character)
        try:
            self.characters.remove(character)
        except ValueError:
            pass
        self.corpses.append(character)

        if isinstance(character, Player):
            # make all enemies untarget the killed player
            for enemy in self.enemies:
                if enemy.targeted_player is character:
                    enemy.targeted_player = None

        if not self.players:
            # GAME OVER KUP SE ROWER!
            self.game_over()

    def other_characters(self, character):
        return [ch for ch in self.characters if ch is not character]

    def players_in_attack_range(self, character):
        players_in_row = [
            player for player in self.players
            if abs(player.position.y - character.position.y) < character.footprint.h * 0.9
            ]
        nearby_players = [
            (player.position.x - character.position.x, player)
            for player in players_in_row
            if abs(player.position.x - character.position.x) < character.attack_reach
            ]
        sorted_nearby_players = sorted(
            nearby_players,
            key=lambda dist_player: abs(dist_player[0]),
        )
        return [player for _, player in sorted_nearby_players]

    y_distance_perception_multiplier = 5

    def nearby_players(self, character):
        nearby_players = [
            (
                (
                    abs(player.position.x - character.position.x) +
                    abs(player.position.y - character.poistion.y) * self.y_distance_perception_multiplier
                ),
                player,
            )
            for player in self.players
            ]
        sorted_nearby_players = sorted(
            nearby_players,
            key=lambda dist_player: abs(dist_player[0]),
        )
        return [player for _, player in sorted_nearby_players]

    def nearby_item(self, position, max_distance=1000):
        best_match = None
        min_distance = 1000
        for item in self.items:
            distance = (item.position - position).length()
            if distance < max_distance and distance < min_distance:
                min_distance = distance
                best_match = item

        return best_match

    def players_worth_attacking(self, character):
        safe_div = lambda a, b: (a / b) if b else 0
        enemies_to_players_ratio = safe_div(len(self.enemies), len(self.players))
        players_with_stats = [
            (
                # [0] player
                player,
                # [1] perceived distance
                (
                    200 - min(
                        abs(player.position.x - character.position.x) + abs(
                            player.position.y - character.position.y) * self.y_distance_perception_multiplier,
                        200,
                    )
                ) / 200,
                # [2] damage ratio
                (player.ENERGY_MAX_ENERGY - player.energy) / player.ENERGY_MAX_ENERGY,
                # [3] enemy targeting pressure
                (safe_div(
                    enemies_to_players_ratio,
                    len(player.targeting_enemies()),
                ) or enemies_to_players_ratio * 2) / enemies_to_players_ratio,
                # [4] anger towards player
                character.anger_towards(player),
            )
            for player in self.players
            ]

        sort_key = lambda p: -sum((
            1.0 * p[1],  # distance
            1.5 * p[2],  # damages
            2.0 * p[3],  # targeting pressure
            3.0 * p[4],  # anger
        ))
        sorted_players = sorted(
            players_with_stats,
            key=sort_key,
        )

        if DEBUG:
            for p in players_with_stats:
                print(p[0].id, p[1:], '->', sort_key(p))
            print()

        return [p[0] for p in sorted_players]

    def spawn_initial_enemies(self):
        # return
        for _ in range(4):
            enemy = self.spawn_random_enemy(probability_of_left=0)
            direction = 1 if enemy.position.x < self.bounds.center_x else -1
            enemy.move(
                Vector2(
                    Utils.rand_int(5, 10) / 10.0 * direction,
                    Utils.rand_int(-4, 4) / 10.0,
                ),
            )

    def spawn_enemies(self):
        num_enemies = 1  # ((self.window_x / self.stage.get_width()) * self.MAX_ENEMIES_ON_SCREEN)
        if len(self.enemies) < num_enemies:
            self.spawn_random_enemy()

    def spawn_bosses(self):
        self.boss_spawn_count += 1
        boss_count = min(5, self.boss_spawn_count)

        for i in range(0, boss_count):
            boss = self.spawn_boss()

            # self.boss_sound.play()

    def spawn_boss(self):
        boss_frame = Utils.random.choice(self.boss_frames)
        boss = self.spawn_random_enemy(
            frame=boss_frame,
            footprint_dim=Rect(0, 0, 60, 14),
            attack_reach=100,
            enemy_class=Boss,
        )
        boss.energy *= (2 * self.boss_spawn_count)
        boss.attack_force *= (3 * self.boss_spawn_count)
        return boss

    def spawn_random_enemy(
            self,
            probability_of_left=0.4,
            frame=None,
            footprint_dim=Character.DEFAULT_FOOTPRINT_DIM,
            attack_reach=70,
            enemy_class=Enemy,
    ):
        if Utils.rand_int(0, 10) < 10 * probability_of_left:
            # spawn on the left
            enemy = self.spawn_enemy_at(
                x=self.bounds.left + self.window_x - Utils.rand_int(30, 100),
                y=Utils.rand_int(self.bounds.top, self.bounds.bottom),
                frame=frame,
                footprint_dim=footprint_dim,
                attack_reach=attack_reach,
                enemy_class=enemy_class,
            )
        else:
            # spawn on the right
            enemy = self.spawn_enemy_at(
                x=self.bounds.right + self.window_x + Utils.rand_int(30, 100),
                y=Utils.rand_int(self.bounds.top, self.bounds.bottom),
                frame=frame,
                footprint_dim=footprint_dim,
                attack_reach=attack_reach,
                enemy_class=enemy_class,
            )
        return enemy

    def spawn_enemy_at(
            self,
            x,
            y,
            frame=None,
            footprint_dim=Character.DEFAULT_FOOTPRINT_DIM,
            attack_reach=70,
            enemy_class=Enemy,
    ):
        frame = frame or Utils.random.choice(self.enemy_frames)
        enemy = enemy_class(
            self,
            frame,
            x,
            y,
            footprint_dim=footprint_dim,
            attack_reach=attack_reach,
        )
        self.add_enemy(enemy)
        enemy.attack_force = 1 + (self.window_x / self.stage.get_width()) * self.MAX_ENEMY_FORCE
        return enemy

    def update_window(self):
        scroll_amount = 0
        for p in self.players:
            if p.position.x - self.window_x > self.bounds.width - 70:
                scroll_amount = p.position.x - self.window_x - (self.bounds.width - 70)
            elif p.position.x - self.window_x < self.bounds.left + 70:
                if p.action != Character.ACTION_DIE:
                    return

        # self.window_x += scroll_amount
        # if self.window_x + self.bounds.width > self.stage.get_width():
        #     self.window_x = self.stage.get_width() - self.bounds.width

    def update(self, game_speed):
        self.stage.update(game_speed)

        for i in self.items:
            i.update(game_speed)

        for c in self.characters:
            c.update(game_speed)

        # Remove all the marked entities
        for c in self.characters:
            if c.should_be_removed:
                self.remove_character(c)
        for i in self.items:
            if i.should_be_removed:
                self.items.remove(i)

        self.update_window()
        self.spawn_enemies()

    def draw(self, screen):
        # render_surface.fill((0, 0, 0))

        self.stage.draw_background(screen, self.window_x, self.window_y)

        # Sort all objects using the Y coordinate
        objects = sorted(
            set(self.characters).union(self.corpses).union(self.items),
            key=lambda o: o.position.y,
        )
        for c in objects:
            c.draw(screen)

        self.stage.draw_foreground(screen, self.window_x, self.window_y)

        if self.scene in (self.SCENE_GAME, self.SCENE_GAME_OVER):
            pass
            # Draw score
            # Gfx.render_centered_text(
            #     render_surface,
            #     str(self._score),
            #     center_x=435,
            #     center_y=7,
            # )

        if self.scene == self.SCENE_GAME_OVER:
            pass
            # Gfx.render_centered_text(
            #     render_surface,
            #     'GAME OVER',
            #     size=48,
            #     center_x=render_surface.get_width() / 2,
            #     center_y=render_surface.get_height() * 0.30,
            # )

            game_over_interval = Utils.time_in_ms() - self.game_over_timer

            if game_over_interval > 3000 and self.game_over_state < 10:
                self.game_over_state = 10

                # if self.game_over_state >= 10 and game_over_interval % 1000 >= 500:
                #     Gfx.render_centered_text(
                #         render_surface,
                #         'Next time buy tickets.',
                #         size=18,
                #         center_x=render_surface.get_width() / 2,
                #         center_y=render_surface.get_height() * 0.50,
                #     )

    def game_over(self):
        self.scene = self.SCENE_GAME_OVER
        self.game_over_state = 0
        self.game_over_timer = Utils.time_in_ms()

        for ch in self.enemies:
            # walk away, nothing happened
            ch.move(Vector2(
                Utils.rand_int(5, 10) / 4.0 * (-1 if Utils.rand_int(0, 10) >= 5 else 1),
                Utils.rand_int(-4, 4) / 10.0,
            ))

    def is_game_over(self):
        return not self.players

    def increment_score(self, bonus):
        self._score += bonus
        self.boss_spawn_point += bonus
        if self.boss_spawn_point > World.BOSS_THRESHOLD:
            self.spawn_bosses()
            self.boss_spawn_point -= World.BOSS_THRESHOLD
