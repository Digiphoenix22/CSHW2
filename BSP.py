import cv2
import numpy as np
import os

class TreeNode:
    def __init__(self, line=None, identifier=None):
        self.line = line
        self.identifier = identifier
        self.front = None
        self.back = None
    


    def midpoint(self):
        if not self.line:
            return None
        x1, y1, x2, y2 = self.line
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        return (mx, my)

    

def detect_lines(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi/180, 200)

    detected_lines = []
    for idx, line in enumerate(lines):
        rho, theta = line[0]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))
        detected_lines.append(((x1, y1, x2, y2), idx + 1))  # Here idx+1 acts as an identifier

    return detected_lines

def partition_space(selected_line, remaining_lines):
    above_lines = []
    below_lines = []

    _, selected_line_y1, _, selected_line_y2 = selected_line[0]
    avg_y = (selected_line_y1 + selected_line_y2) / 2

    for line, identifier in remaining_lines:
        _, y1, _, y2 = line
        if y1 < avg_y and y2 < avg_y:
            above_lines.append((line, identifier))
        else:
            below_lines.append((line, identifier))

    return above_lines, below_lines

def build_bsp_tree(lines):
    if not lines:
        return None

    # For simplicity, we just take the first line as the partitioning line, but a smarter approach could be used.
    partitioning_line = lines.pop(0)

    node = TreeNode(partitioning_line[0], partitioning_line[1])

    above_lines, below_lines = partition_space(partitioning_line, lines)

    node.back = build_bsp_tree(above_lines)
    node.front = build_bsp_tree(below_lines)

    return node

def select_starting_line(detected_lines):
    for i, (line, identifier) in enumerate(detected_lines):
        print(f"{i+1}. Line {identifier} from ({line[0]}, {line[1]}) to ({line[2]}, {line[3]})")
    choice = int(input("Select the number of the starting line: "))
    return detected_lines[choice - 1]


def in_order_traversal(node, depth=0, parent=None):
    if node:
        # Print the connection to parent (if exists)
        connection = ""
        if parent:
            connection = f" -> From Parent {parent.identifier} ({parent.midpoint()})"
        # Print node details
        print("    " * depth + f"Node {node.identifier} ({node.midpoint()}){connection}")
        
        if node.back:
            in_order_traversal(node.back, depth+1, node)
        if node.front:
            in_order_traversal(node.front, depth+1, node)




def side_of_line(line, point):
    x1, y1, x2, y2 = line
    return (x2 - x1) * (point[1] - y1) - (y2 - y1) * (point[0] - x1)

def check_collision(node, start_point, end_point):
    if not node:
        return "MISS"  # If we reach an empty leaf node

    if node.line:  # If it's not a leaf
        start_side = side_of_line(node.line, start_point)
        end_side = side_of_line(node.line, end_point)
        if start_side > 0 and end_side > 0:  # Both on the front side
            return check_collision(node.front, start_point, end_point)
        elif start_side < 0 and end_side < 0:  # Both on the back side
            return check_collision(node.back, start_point, end_point)
        else:  # The line crosses the partition
            if start_side > 0:
                first = node.front
                second = node.back
            else:
                first = node.back
                second = node.front
            # Check the first side, then the second side
            first_result = check_collision(first, start_point, end_point)
            if first_result == "HIT":
                return "HIT"
            second_result = check_collision(second, start_point, end_point)
            if second_result == "HIT":
                return "HIT"
            return "MISS"
    else:
        # This is a leaf, and we assume all leaves in your scenario are solid.
        # In a more complex scenario, you might have an attribute in the node indicating if it's solid or not.
        return "HIT"



if __name__ == '__main__':
    
    image_path = r'Picture1.png'
    if not os.path.exists(image_path):
        raise ValueError(f"Image not found at path: {image_path}")
    detected_lines = detect_lines(image_path)
    starting_line = select_starting_line(detected_lines)
    remaining_lines = [line for line in detected_lines if line != starting_line]
    bsp_tree = build_bsp_tree([starting_line] + remaining_lines)
    print("\nIn-order Traversal of the BSP Tree:")
    in_order_traversal(bsp_tree)
    

    # Define the start and end points based on your image.
    # You'd typically compute these from the image, but for now, let's hardcode them.
    start_point = (100, 100)  # Adjust this to the start point in your image
    end_point = (400, 400)  # Adjust this to the end point in your image

    # Check for collisions
    result = check_collision(bsp_tree, start_point, end_point)
    if result == "HIT":
        print("\nThe line segment from", start_point, "to", end_point, "has a collision!")
    else:
        print("\nThe line segment from", start_point, "to", end_point, "does NOT have a collision!")

    