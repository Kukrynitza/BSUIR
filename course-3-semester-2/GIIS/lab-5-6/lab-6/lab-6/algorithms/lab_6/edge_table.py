def build_edge_table(points):
    min_y = min(int(p[1]) for p in points)
    max_y = max(int(p[1]) for p in points)
    
    edge_table = {}
    for y in range(min_y, max_y + 1):
        edge_table[y] = []
    
    n = len(points)
    for i in range(n):
        p1 = points[i]
        p2 = points[(i + 1) % n]
        
        y1 = float(p1[1])
        y2 = float(p2[1])
        x1 = float(p1[0])
        x2 = float(p2[0])
        
        if y1 == y2:
            continue
        
        if y1 > y2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        
        dy = y2 - y1
        dx = x2 - x1
        dx_dy = dx / dy if dy != 0 else 0
        
        y_start = int(y1)
        y_end = int(y2)
        
        for y in range(y_start, y_end):
            t = (y - y1) / dy if dy != 0 else 0
            x = x1 + dx_dy * t
            edge_table[y].append(x)
    return edge_table, min_y, max_y


def build_edge_table_with_ymax(points):
    min_y = min(int(p[1]) for p in points)
    max_y = max(int(p[1]) for p in points)
    
    edge_table = {}
    for y in range(min_y, max_y + 1):
        edge_table[y] = []
    
    n = len(points)
    for i in range(n):
        p1 = points[i]
        p2 = points[(i + 1) % n]
        
        y1 = int(p1[1])
        y2 = int(p2[1])
        
        if y1 == y2:
            continue
        
        x1 = float(p1[0])
        x2 = float(p2[0])
        
        if y1 > y2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        
        dx = x2 - x1
        dy = y2 - y1
        dx_dy = dx / dy if dy != 0 else 0
        
        edge_table[y1].append([x1, dx_dy, y2])
    
    return edge_table, min_y, max_y
