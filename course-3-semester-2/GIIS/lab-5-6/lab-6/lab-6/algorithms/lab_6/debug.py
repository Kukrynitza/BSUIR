from algorithms.lab_6.edge_table import build_edge_table, build_edge_table_with_ymax
from algorithms.lab_6.seed import fill_seed_simple as seed_simple_impl
from algorithms.lab_6.seed import fill_seed_scanline as seed_scanline_impl


def fill_scanline_basic_debug(points):
    edge_table, min_y, max_y = build_edge_table(points)
    
    steps = []
    pixels = []
    
    for y in range(min_y, max_y + 1):
        x_intersections = edge_table[y][:]
        x_intersections.sort()
        
        step = {
            'y': y,
            'intersections': list(x_intersections),
            'intervals': [],
            'pixels': []
        }
        
        for i in range(0, len(x_intersections) - 1, 2):
            x1 = int(x_intersections[i] + 0.5)
            x2 = int(x_intersections[i + 1] + 0.5)
            
            interval_pixels = []
            for x in range(x1, x2 + 1):
                pixels.append((x, y, 1.0))
                interval_pixels.append((x, y))
            
            step['intervals'].append((x1, x2))
            step['pixels'].append(interval_pixels)
        
        steps.append(step)
    
    return pixels, steps


def fill_scanline_aet_debug(points):
    edge_table, min_y, max_y = build_edge_table_with_ymax(points)
    
    aet = []
    pixels = []
    steps = []
    
    for y in range(min_y, max_y + 1):
        for edge in edge_table[y]:
            aet.append(list(edge))
        
        aet = [e for e in aet if e[2] > y]
        
        aet.sort(key=lambda e: e[0])
        
        step = {
            'y': y,
            'aet_before': [(e[0], e[1], e[2]) for e in aet],
            'intervals': [],
            'pixels': []
        }
        
        for i in range(0, len(aet) - 1, 2):
            x1 = int(aet[i][0])
            x2 = int(aet[i + 1][0])
            
            interval_pixels = []
            for x in range(x1, x2 + 1):
                pixels.append((x, y, 1.0))
                interval_pixels.append((x, y))
            
            step['intervals'].append((x1, x2))
            step['pixels'].append(interval_pixels)
        
        for edge in aet:
            edge[0] += edge[1]
        
        step['aet_after'] = [(e[0], e[1], e[2]) for e in aet]
        steps.append(step)
    
    return pixels, steps


def fill_seed_simple_debug(points, seed):
    fill_color = 0.5
    boundary_color = 1.0
    
    min_x = min(int(p[0]) for p in points)
    max_x = max(int(p[0]) for p in points)
    min_y = min(int(p[1]) for p in points)
    max_y = max(int(p[1]) for p in points)
    
    width = max_x - min_x + 1
    height = max_y - min_y + 1
    
    bitmap = [[0.0 for _ in range(width)] for _ in range(height)]
    
    for i in range(len(points)):
        p1 = points[i]
        p2 = points[(i + 1) % len(points)]
        
        x0 = int(p1[0]) - min_x
        y0 = int(p1[1]) - min_y
        x1 = int(p2[0]) - min_x
        y1 = int(p2[1]) - min_y
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while True:
            if 0 <= x0 < width and 0 <= y0 < height:
                bitmap[y0][x0] = boundary_color
            
            if x0 == x1 and y0 == y1:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
        
        if 0 <= x1 < width and 0 <= y1 < height:
            bitmap[y1][x1] = boundary_color
    
    stack = [(seed[0] - min_x, seed[1] - min_y)]
    
    pixels = []
    steps = []
    
    step_num = 0
    visited = set()
    
    while stack:
        x, y = stack.pop()
        
        if x < 0 or x >= width or y < 0 or y >= height:
            continue
        
        if (x, y) in visited:
            continue
        visited.add((x, y))
        
        if bitmap[y][x] != 0.0:
            continue
        
        step_num += 1
        step = {
            'step': step_num,
            'current': (x + min_x, y + min_y),
            'stack_size': len(stack)
        }
        
        bitmap[y][x] = fill_color
        pixels.append((x + min_x, y + min_y, 1.0))
        step['filled'] = [(x + min_x, y + min_y)]
        
        neighbors = []
        for nx, ny in [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]:
            if 0 <= nx < width and 0 <= ny < height and bitmap[ny][nx] == 0.0 and (nx, ny) not in visited:
                neighbors.append((nx, ny))
        
        step['neighbors'] = [(n[0] + min_x, n[1] + min_y) for n in neighbors]
        
        for nx, ny in neighbors:
            stack.append((nx, ny))
        
        steps.append(step)
    
    return pixels, steps


def fill_seed_scanline_debug(points, seed):
    min_x = min(int(p[0]) for p in points)
    max_x = max(int(p[0]) for p in points)
    min_y = min(int(p[1]) for p in points)
    max_y = max(int(p[1]) for p in points)
    
    width = max_x - min_x + 1
    height = max_y - min_y + 1
    
    bitmap = [[0.0 for _ in range(width)] for _ in range(height)]
    
    for i in range(len(points)):
        p1 = points[i]
        p2 = points[(i + 1) % len(points)]
        
        x0 = int(p1[0]) - min_x
        y0 = int(p1[1]) - min_y
        x1 = int(p2[0]) - min_x
        y1 = int(p2[1]) - min_y
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while True:
            if 0 <= x0 < width and 0 <= y0 < height:
                bitmap[y0][x0] = 1.0
            
            if x0 == x1 and y0 == y1:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
    
    stack = [(seed[0] - min_x, seed[1] - min_y)]
    pixels = []
    steps = []
    
    step_num = 0
    visited = set()
    
    while stack:
        x, y = stack.pop()
        
        if x < 0 or x >= width or y < 0 or y >= height:
            continue
        
        if (x, y) in visited:
            continue
        visited.add((x, y))
        
        if bitmap[y][x] != 0.0:
            continue
        
        step_num += 1
        step = {
            'step': step_num,
            'current': (x + min_x, y + min_y),
            'stack_size': len(stack)
        }
        
        left = x
        while left > 0 and bitmap[y][left - 1] == 0.0 and (left - 1, y) not in visited:
            left -= 1
        
        right = x
        while right < width - 1 and bitmap[y][right + 1] == 0.0 and (right + 1, y) not in visited:
            right += 1
        
        interval_pixels = []
        for px in range(left, right + 1):
            if bitmap[y][px] == 0.0:
                bitmap[y][px] = 0.5
                pixels.append((px + min_x, y + min_y, 1.0))
                interval_pixels.append((px + min_x, y + min_y))
        
        step['interval'] = (left + min_x, right + min_x)
        step['filled'] = interval_pixels
        
        new_seeds = []
        for px in range(left, right + 1):
            if y > 0 and bitmap[y - 1][px] == 0.0 and (px, y - 1) not in visited:
                bitmap[y - 1][px] = 0.5
                new_seeds.append((px, y - 1))
            if y < height - 1 and bitmap[y + 1][px] == 0.0 and (px, y + 1) not in visited:
                bitmap[y + 1][px] = 0.5
                new_seeds.append((px, y + 1))
        
        step['new_seeds'] = [(s[0] + min_x, s[1] + min_y) for s in new_seeds]
        
        for nx, ny in new_seeds:
            stack.append((nx, ny))
        
        steps.append(step)
    
    return pixels, steps
