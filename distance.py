import math

def euclidean(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def min_hand_face_distance(hand_points, face_regions):
    min_dist = float("inf")
    closest = None

    for hx, hy in hand_points:
        for region, (fx, fy) in face_regions.items():
            d = euclidean((hx, hy), (fx, fy))
            if d < min_dist:
                min_dist = d
                closest = region

    return min_dist, closest
