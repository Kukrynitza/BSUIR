from algorithms.lab_6.edge_table import build_edge_table, build_edge_table_with_ymax


def fill_scanline_basic(points):
    edge_table, min_y, max_y = build_edge_table(points)
    pixels = []
    for y in range(min_y, max_y + 1):
        x_intersections = edge_table[y]
        if len(x_intersections) < 2:
            continue
        x_intersections.sort()
        
        for i in range(0, len(x_intersections) - 1, 2):
            x1 = int(x_intersections[i] + 0.5)
            x2 = int(x_intersections[i + 1] + 0.5)
            for x in range(x1, x2 + 1):
                pixels.append((x, y, 1.0))
    return pixels


def fill_scanline_with_aet(points):
    edge_table, min_y, max_y = build_edge_table_with_ymax(points)
    aet = []
    pixels = []
    
    for y in range(min_y, max_y + 1):
        for edge in edge_table[y]:
            aet.append(edge)
        
        aet = [e for e in aet if e[2] > y]
        aet.sort(key=lambda e: e[0])
        
        for i in range(0, len(aet) - 1, 2):
            x1 = int(aet[i][0])
            x2 = int(aet[i + 1][0])
            for x in range(x1, x2 + 1):
                pixels.append((x, y, 1.0))
        for edge in aet:
            edge[0] += edge[1]
    return pixels
