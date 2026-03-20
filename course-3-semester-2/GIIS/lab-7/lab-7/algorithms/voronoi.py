import math


def circumcenter(a, b, c):
    ax, ay = a[0], a[1]
    bx, by = b[0], b[1]
    cx, cy = c[0], c[1]
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-10:
        return None
    ux = ((ax**2 + ay**2) * (by - cy) + (bx**2 + by**2) * (cy - ay) + (cx**2 + cy**2) * (ay - by)) / d
    uy = ((ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2) * (ax - cx) + (cx**2 + cy**2) * (bx - ax)) / d
    return (ux, uy)


def voronoi(points, triangles):
    vertices = {}
    for t in triangles:
        cc = circumcenter(t[0], t[1], t[2])
        if cc:
            vertices[t] = cc
    
    voronoi_vertices = list(vertices.values())
    voronoi_edges = []
    
    for i, t1 in enumerate(triangles):
        if t1 not in vertices:
            continue
        for t2 in triangles[i+1:]:
            if t2 not in vertices:
                continue
            if len(set(t1) & set(t2)) == 2:
                voronoi_edges.append((vertices[t1], vertices[t2]))
    
    return voronoi_edges, voronoi_vertices


debug_steps = []

def voronoi_debug(points, triangles):
    global debug_steps
    debug_steps = []
    
    debug_steps.append({
        'description': f'Начало: {len(triangles)} треугольников',
        'edges': [],
        'vertices': []
    })
    vertices = {}
    for i, t in enumerate(triangles):
        cc = circumcenter(t[0], t[1], t[2])
        if cc:
            vertices[t] = cc
            debug_steps.append({
                'description': f'Вершина {i+1}: ({cc[0]:.1f}, {cc[1]:.1f})',
                'edges': [],
                'vertices': list(vertices.values())
            })
    edges = []
    for i, t1 in enumerate(triangles):
        if t1 not in vertices:
            continue
        for t2 in triangles[i+1:]:
            if t2 not in vertices:
                continue
            if len(set(t1) & set(t2)) == 2:
                e = (vertices[t1], vertices[t2])
                edges.append(e)
                debug_steps.append({
                    'description': f'Ребро Вороного {len(edges)}',
                    'edges': list(edges),
                    'vertices': list(vertices.values())
                })
    debug_steps.append({
        'description': f'Готово: {len(edges)} рёбер',
        'edges': edges,
        'vertices': list(vertices.values())
    })
    return edges, list(vertices.values())




