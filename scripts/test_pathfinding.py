import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pygame as pg
pg.init()
pg.display.set_mode((1,1))
from src.core.managers.game_manager import GameManager

print('[TEST] Loading game...')
gm = GameManager.load('saves/game0.json')
if gm is None:
    print('[TEST] load failed')
else:
    print('[TEST] Game loaded')
    # Use loaded map; do not switch maps (switch_map schedules a change)
    from src.utils import GameSettings
    ts = GameSettings.TILE_SIZE
    start = (int(gm.player.position.x // ts), int(gm.player.position.y // ts))
    print('[TEST] player_pos', gm.player.position.x, gm.player.position.y)
    print('[TEST] teleports', [(int(tp.pos.x)//ts, int(tp.pos.y)//ts) for tp in gm.current_map.teleporters])
    goal = (16,30)
    print('[TEST] start', start, 'goal', goal)
    # Check if goal is blocked
    def is_blocked(tile):
        x,y = tile
        tile_rect = pg.Rect(x*16, y*16, 16, 16)
        for r in gm.current_map._collision_map:
            if r.colliderect(tile_rect):
                return True
        for t in gm.current_enemy_trainers:
            if tile_rect.colliderect(t.animation.rect):
                return True
        return False
    print('[TEST] goal_blocked', is_blocked(goal))
    # Try finding a nearby reachable goal within radius 8
    found = None
    for r in range(1,9):
        for dx in range(-r, r+1):
            for dy in range(-r, r+1):
                tx = start[0] + dx
                ty = start[1] + dy
                if tx < 0 or ty < 0 or tx >= gm.current_map.tmxdata.width or ty >= gm.current_map.tmxdata.height:
                    continue
                if not any(tx == t[0] and ty == t[1] for t in gm.current_map._collision_map):
                    p = gm.find_path_bfs(start, (tx,ty))
                    if p:
                        found = (tx,ty,p)
                        break
            if found:
                break
        if found:
            break
    print('[TEST] nearby_found', found is not None, 'goal', found[0:2] if found else None)
    if found:
        goal = (found[0], found[1])
        path = found[2]
        print('[TEST] path_len', len(path))
        ok = gm.auto_move_player_to(*goal)
        print('[TEST] auto_move_ok', ok)
        if ok:
            print('[TEST] first waypoint', gm.player.auto_move_path[0].x, gm.player.auto_move_path[0].y)
            # Simulate stepping until first waypoint reached
            wp = gm.player.auto_move_path[0]
            print('[TEST] player pos before', gm.player.position.x, gm.player.position.y)
            # simulate updates: move directly to waypoint
            gm.player.position = type(gm.player.position)(gm.player.position.x, gm.player.position.y)
            # call update with dt enough to move
            gm.player.update(0.2)
            print('[TEST] player pos after', gm.player.position.x, gm.player.position.y)

    # Test teleporter spot (use actual teleporter from current map)
    if len(gm.current_map.teleporters) > 0:
        tp0 = gm.current_map.teleporters[0]
        tele_goal = (int(tp0.pos.x)//ts, int(tp0.pos.y)//ts)
        print('[TEST] tele_goal', tele_goal)
        tele_is_tele = any((int(tp.pos.x)//ts, int(tp.pos.y)//ts) == tele_goal for tp in gm.current_map.teleporters)
        print('[TEST] tele_goal_is_tele', tele_is_tele)
        tele_path = gm.find_path_bfs(start, tele_goal)
        print('[TEST] tele_path_len', len(tele_path) if tele_path else None)
        # check neighbors
        neighs = [(tele_goal[0]+1, tele_goal[1]), (tele_goal[0]-1, tele_goal[1]), (tele_goal[0], tele_goal[1]+1), (tele_goal[0], tele_goal[1]-1)]
        for n in neighs:
            inb = 0 <= n[0] < gm.current_map.tmxdata.width and 0 <= n[1] < gm.current_map.tmxdata.height
            print('[TEST] neigh', n, 'in_bounds', inb)
            if inb:
                blocked = False
                tile_rect = pg.Rect(n[0]*ts, n[1]*ts, ts, ts)
                for r in gm.current_map._collision_map:
                    if r.colliderect(tile_rect):
                        blocked = True
                for t in gm.current_enemy_trainers:
                    if tile_rect.colliderect(t.animation.rect):
                        blocked = True
                print('[TEST] neigh blocked', blocked)
                p = gm.find_path_bfs(start, n)
                print('[TEST] path_to_neigh', len(p) if p else None)
        if tele_path:
            ok2 = gm.auto_move_player_to(*tele_goal)
            print('[TEST] tele_auto_move_ok', ok2)
            if ok2:
                print('[TEST] tele_first_wp', gm.player.auto_move_path[0].x, gm.player.auto_move_path[0].y)
    else:
        print('[TEST] no teleporters on map')

pg.quit()
