import math

def normalize_triangle(tri):
    pts = list(tri)
    pts.sort(key=lambda x: (x[0], x[1]))
    return tuple(pts)

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

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def delaunay(points):
    if len(points) < 3:
        return []
    
    try:
        import numpy as np
        from scipy.spatial import Delaunay
        points_array = np.array(points)
        tri = Delaunay(points_array)
        result = []
        for simplex in tri.simplices:
            t = normalize_triangle(tuple(tuple(points_array[i]) for i in simplex))
            if t not in result:
                result.append(t)
        return result
    except:
        return []
debug_steps = []

def delaunay_debug(points):
    global debug_steps
    debug_steps = []
    if len(points) < 3:
        return []
    try:
        import numpy as np
        from scipy.spatial import Delaunay
        points_array = np.array(points)
        tri = Delaunay(points_array)
        
        triangles = []
        for simplex in tri.simplices:
            t = normalize_triangle(tuple(tuple(points_array[i]) for i in simplex))
            if t not in triangles:
                triangles.append(t)
        
        debug_steps.append({
            'description': f'Начало: {len(points)} точек',
            'triangles': []
        })
        
        for i, t in enumerate(triangles):
            debug_steps.append({
                'description': f'Треугольник {i+1}/{len(triangles)}: {t}',
                'triangles': triangles[:i+1]
            })
        
        debug_steps.append({
            'description': f'Готово: {len(triangles)} треугольников',
            'triangles': triangles
        })
        return triangles
    except:
        return []












