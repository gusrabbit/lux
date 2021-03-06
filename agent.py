import math, sys
from lux.game import Game
from lux.game_map import Cell, RESOURCE_TYPES
from lux.constants import Constants
from lux.game_constants import GAME_CONSTANTS
from lux import annotate

DIRECTIONS = Constants.DIRECTIONS
game_state = None

def get_resource_tiles(game_state) -> list:
    """
    Returns list with all reasource tiles on a certain game_state.
    Args:
        game_state:

    Returns:
        resource_tiles: list
    """
    resource_tiles: list[Cell] = []
    for y in range(game_state.map.height):
        for x in range(game_state.map.width):
            cell = game_state.map.get_cell(x, y)
            if cell.has_resource():
                resource_tiles.append(cell)
    return resource_tiles

def get_closest_resource_tile(resource_tiles, player, unit):
    """
    Find the nearest resource tile checking for research capabilities first.
    Args:
        resource_tiles:

    Returns:
            closest_resource_tile
    """
    closest_dist = math.inf
    closest_resource_tile = None
    for resource_tile in resource_tiles:
        if resource_tile.resource.type == Constants.RESOURCE_TYPES.COAL and not player.researched_coal(): continue
        if resource_tile.resource.type == Constants.RESOURCE_TYPES.URANIUM and not player.researched_uranium(): continue
        dist = resource_tile.pos.distance_to(unit.pos)
        if dist < closest_dist:
            closest_dist = dist
            closest_resource_tile = resource_tile
    return closest_resource_tile

def get_closest_city_tile(player, unit):
    """
    Gets closest city tile.
    Args:
        player: which player should be considered
        unit: the unit from which we will get the closest city tile

    Returns:
        closest_city_tile
    """
    closest_dist = math.inf
    closest_city_tile = None
    for k, city in player.cities.items():
        for city_tile in city.citytiles:
            dist = city_tile.pos.distance_to(unit.pos)
            if dist < closest_dist:
                closest_dist = dist
                closest_city_tile = city_tile
    return closest_city_tile

def get_adjacent_tiles(pos):
    next_to_list = [(1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, -1)]
    adjacent_tiles = []
    for x,y in next_to_list:
        new_pos = pos
        new_pos.x += x
        new_pos.y += y
        new_tile = game_state.map.get_cell(new_pos.x, new_pos.y)
        adjacent_tiles.append(new_tile)
    return adjacent_tiles

def get_closest_tiles(tiles_list, unit):
    closest_dist = math.inf
    closest_tile = None
    for tile in tiles_list:
        dist = tile.pos.distance_to(unit.pos)
        if dist < closest_dist:
            closest_dist = dist
            closest_tile = tile
    return closest_tile


def get_closest_tile_for_new_city(player, unit):
    empty_cells = []
    for cities in player.cities:
        city = player.cities[cities]
        for city_tile in city.citytiles:
            adjacent = get_adjacent_tiles(city_tile.pos)
            for tile in adjacent:
                if tile.has_resource():
                   pass
                else: empty_cells.append(tile)
    closest_tile_for_new_city = get_closest_tiles(empty_cells, unit)
    return closest_tile_for_new_city

def agent(observation, configuration):
    global game_state

    ### Do not edit ###
    if observation["step"] == 0:
        game_state = Game()
        game_state._initialize(observation["updates"])
        game_state._update(observation["updates"][2:])
        game_state.id = observation.player
    else:
        game_state._update(observation["updates"])
    
    actions = []

    ### AI Code goes down here! ### 
    player = game_state.players[observation.player]
    opponent = game_state.players[(observation.player + 1) % 2]
    width, height = game_state.map.width, game_state.map.height

    resource_tiles = get_resource_tiles(game_state)

    # we iterate over all our units and do something with them
    for unit in player.units:
        if unit.is_worker() and unit.can_act():
            if unit.get_cargo_space_left() > 0:
                # if the unit is a worker and we have space in cargo, lets find the nearest resource tile and try to mine it
                closest_resource_tile = get_closest_resource_tile(resource_tiles, player, unit)
                if closest_resource_tile is not None:
                    actions.append(unit.move(unit.pos.direction_to(closest_resource_tile.pos)))
            else:
                if unit.cargo.wood == 100:
                    new_city_tile = get_closest_tile_for_new_city(player, unit)
                    if unit.pos.equals(new_city_tile.pos):
                        actions.append(unit.build_city())
                    if new_city_tile is not None:
                        move_dir = unit.pos.direction_to(new_city_tile.pos)
                        actions.append(unit.move(move_dir))

                    # if unit is a worker and there is no cargo space left, and we have cities, lets return to them
                    elif len(player.cities) > 0:
                        closest_city_tile = get_closest_city_tile(player, unit)
                        if closest_city_tile is not None:
                            move_dir = unit.pos.direction_to(closest_city_tile.pos)
                            actions.append(unit.move(move_dir))

    # you can add debug annotations using the functions in the annotate object
    # actions.append(annotate.circle(0, 0))
    
    return actions
