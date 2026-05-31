import cv2
import numpy as np
from braille_map import decode_braille_sequence


def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    thresh = cv2.adaptiveThreshold(
        denoised, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        blockSize=15, C=4
    )
    return thresh


def detect_dots(thresh_img, original_img):
    contours, _ = cv2.findContours(thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    dots = []
    annotated = original_img.copy()
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 20 or area > 2000:
            continue
        perimeter = cv2.arcLength(cnt, True)
        if perimeter == 0:
            continue
        circularity = 4 * np.pi * area / (perimeter ** 2)
        if circularity < 0.4:
            continue
        M = cv2.moments(cnt)
        if M['m00'] == 0:
            continue
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        radius = int(np.sqrt(area / np.pi))
        dots.append((cx, cy, radius))
        cv2.circle(annotated, (cx, cy), max(radius, 4), (0, 255, 0), 2)
    return dots, annotated


def estimate_cell_size(dots):
    """
    Better estimation using nearest-neighbor gaps only.
    """
    if len(dots) < 2:
        return None

    xs = sorted([d[0] for d in dots])
    ys = sorted([d[1] for d in dots])

    clustered_x = _cluster_positions(xs, 4)
    clustered_y = _cluster_positions(ys, 4)

    x_gaps = [clustered_x[i+1] - clustered_x[i] for i in range(len(clustered_x) - 1) if clustered_x[i+1] - clustered_x[i] > 3]
    y_gaps = [clustered_y[i+1] - clustered_y[i] for i in range(len(clustered_y) - 1) if clustered_y[i+1] - clustered_y[i] > 3]

    if not x_gaps or not y_gaps:
        return None

    def _select_spacing(gaps, axis):
        gaps = sorted(gaps)
        dot_spacing = max(3, int(np.percentile(gaps, 25)))
        if axis == 'x':
            candidates = [gap for gap in gaps if gap >= dot_spacing * 2 and gap <= dot_spacing * 3.5]
            if candidates:
                cell_spacing = int(np.median(candidates))
            else:
                cell_spacing = int(dot_spacing * 2.4)
        else:
            candidates = [gap for gap in gaps if gap >= dot_spacing * 1.2 and gap <= dot_spacing * 2.5]
            if candidates:
                cell_spacing = int(np.median(candidates))
            else:
                cell_spacing = int(dot_spacing * 3.4)
        return dot_spacing, cell_spacing

    dot_spacing_x, cell_spacing_x = _select_spacing(x_gaps, 'x')
    dot_spacing_y, cell_spacing_y = _select_spacing(y_gaps, 'y')

    return dot_spacing_x, dot_spacing_y, cell_spacing_x, cell_spacing_y


def _cluster_positions(coords, threshold):
    coords = sorted(set(int(round(c)) for c in coords))
    clusters = []
    for x in coords:
        if not clusters or x - clusters[-1][-1] > threshold:
            clusters.append([x])
        else:
            clusters[-1].append(x)
    return [int(round(np.mean(cluster))) for cluster in clusters]


def _assign_axis_line_positions(lines, dot_spacing, cell_spacing, local_offsets):
    if not lines:
        return []

    best_assignments = None
    best_error = None
    tolerance = max(2.0, dot_spacing * 0.4)

    for origin_offset in local_offsets:
        origin = lines[0] - origin_offset
        assignments = []
        total_error = 0.0
        valid = True

        for line in lines:
            rel = line - origin
            cell = int(round(rel / cell_spacing))
            local = rel - cell * cell_spacing
            closest_offset = min(local_offsets, key=lambda o: abs(local - o))
            error = abs(local - closest_offset)
            if error > tolerance:
                valid = False
                break
            assignments.append((cell, local_offsets.index(closest_offset)))
            total_error += error

        if valid:
            if best_assignments is None or total_error < best_error:
                best_assignments = assignments
                best_error = total_error

    if best_assignments is not None:
        return best_assignments

    # Fallback: naive alternating assignment for sparse or noisy rows.
    assignments = []
    current_cell = 0
    current_local = 0
    if len(lines) > 1 and lines[1] - lines[0] > dot_spacing * 1.4:
        current_local = 1 if len(local_offsets) > 1 else 0
    assignments.append((current_cell, current_local))
    for i in range(1, len(lines)):
        gap = lines[i] - lines[i - 1]
        if gap <= dot_spacing * 1.4:
            current_local = (current_local + 1) % len(local_offsets)
            if current_local == 0:
                current_cell += 1
        else:
            current_cell += 1
            current_local = 0
        assignments.append((current_cell, current_local))
    return assignments


def _assign_x_line_positions(x_lines, dot_spacing, cell_spacing):
    return _assign_axis_line_positions(x_lines, dot_spacing, cell_spacing, [0, dot_spacing])


def _assign_y_line_positions(y_lines, dot_spacing, cell_spacing):
    return _assign_axis_line_positions(y_lines, dot_spacing, cell_spacing, [0, dot_spacing, 2 * dot_spacing])


def cluster_dots_into_cells(dots, cell_params):
    if not dots or not cell_params:
        return {}

    dot_spacing_x, dot_spacing_y, cell_spacing_x, cell_spacing_y = cell_params

    x_threshold = max(2, min(4, dot_spacing_x // 2))
    y_threshold = max(2, min(4, dot_spacing_y // 2))

    x_lines = _cluster_positions([cx for cx, _, _ in dots], x_threshold)
    y_lines = _cluster_positions([cy for _, cy, _ in dots], y_threshold)

    if len(x_lines) < 2 or len(y_lines) < 2:
        return {}

    x_positions = _assign_x_line_positions(x_lines, dot_spacing_x, cell_spacing_x)
    y_positions = _assign_y_line_positions(y_lines, dot_spacing_y, cell_spacing_y)

    if not x_positions or not y_positions:
        return {}

    cells = {}
    for (cx, cy, _) in dots:
        x_idx = min(range(len(x_lines)), key=lambda i: abs(cx - x_lines[i]))
        y_idx = min(range(len(y_lines)), key=lambda i: abs(cy - y_lines[i]))

        cell_col, local_x = x_positions[x_idx]
        cell_row, local_y = y_positions[y_idx]

        cell_key = (cell_row, cell_col)
        cells.setdefault(cell_key, set()).add((local_x, local_y))

    return cells


def cell_to_dot_pattern(local_dots):
    """
    Map (col, row) positions to standard Braille dot numbers:
      col0,row0=1   col1,row0=4
      col0,row1=2   col1,row1=5
      col0,row2=3   col1,row2=6
    """
    mapping = {
        (0, 0): 1, (1, 0): 4,
        (0, 1): 2, (1, 1): 5,
        (0, 2): 3, (1, 2): 6,
    }
    pattern = []
    for (lx, ly) in local_dots:
        dot_num = mapping.get((lx, ly))
        if dot_num:
            pattern.append(dot_num)
    return tuple(sorted(pattern))


def image_to_braille_text(image_bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return {"error": "Could not decode image", "text": "",
                "guidance": "Please upload a valid image."}

    h, w = img.shape[:2]
    guidance = []

    if w < 300 or h < 300:
        guidance.append("Image too small — move closer.")
    if w > 4000 or h > 4000:
        scale = 2000 / max(w, h)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))

    gray_check = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mean_brightness = np.mean(gray_check)
    if mean_brightness < 50:
        guidance.append("Too dark — improve lighting.")
    elif mean_brightness > 220:
        guidance.append("Overexposed — reduce brightness.")

    thresh = preprocess_image(img)
    dots, annotated = detect_dots(thresh, img)

    if len(dots) == 0:
        guidance.append("No Braille dots detected — ensure Braille surface is in frame.")
        return {
            "text": "", "dot_count": 0, "cell_count": 0,
            "guidance": " ".join(guidance) if guidance else "No dots found.",
            "annotated_image": _encode_image(annotated),
        }

    cell_params = estimate_cell_size(dots)
    if not cell_params:
        guidance.append("Could not estimate cell size — try a clearer image.")
        return {
            "text": "", "dot_count": len(dots), "cell_count": 0,
            "guidance": " ".join(guidance) if guidance else "Cell estimation failed.",
            "annotated_image": _encode_image(annotated),
        }

    cells = cluster_dots_into_cells(dots, cell_params)
    sorted_cell_keys = sorted(cells.keys())
    patterns = [cell_to_dot_pattern(cells[k]) for k in sorted_cell_keys]
    text = decode_braille_sequence(patterns)

    if not text.strip():
        guidance.append("Dots detected but pattern unclear — adjust angle or lighting.")
    else:
        guidance.append("Braille detected successfully!")

    return {
        "text": text if text.strip() else "(unrecognized pattern)",
        "dot_count": len(dots),
        "cell_count": len(cells),
        "guidance": " ".join(guidance),
        "annotated_image": _encode_image(annotated),
    }


def _encode_image(img):
    import base64
    _, buffer = cv2.imencode('.jpg', img)
    return base64.b64encode(buffer).decode('utf-8')