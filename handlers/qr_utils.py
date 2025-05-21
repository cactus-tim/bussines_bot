"""
QR Code Generator
Stylish QR code with gradient background and central logo.
"""

import os
from io import BytesIO

import qrcode
from PIL import Image, ImageDraw, ImageColor


# --------------------------------------------------------------------------------


def create_styled_qr_code(data: str) -> BytesIO:
    """
    Generate a stylish QR code with gradient background and embedded logo.

    Args:
        data (str): Data to encode into the QR code.

    Returns:
        BytesIO: PNG image of the QR code in memory.
    """
    bg_top = "#8F2EFF"
    bg_bottom = "#A259FF"
    qr_color = "#FFFFFF"
    box_size = 12
    border = 4
    finder_radius = 6
    logo_ratio = 0.25
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")

    # --------------------------------------------------------------------------------

    qr = qrcode.QRCode(
        version=4,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    qr_size = len(matrix)
    img_px_size = (qr_size + 2 * border) * box_size

    # --------------------------------------------------------------------------------

    qr_img = Image.new("RGBA", (img_px_size, img_px_size))
    draw = ImageDraw.Draw(qr_img)

    for y in range(img_px_size):
        ratio = y / img_px_size
        r = int(ImageColor.getrgb(bg_top)[0] * (1 - ratio)
                + ImageColor.getrgb(bg_bottom)[0] * ratio)
        g = int(ImageColor.getrgb(bg_top)[1] * (1 - ratio)
                + ImageColor.getrgb(bg_bottom)[1] * ratio)
        b = int(ImageColor.getrgb(bg_top)[2] * (1 - ratio)
                + ImageColor.getrgb(bg_bottom)[2] * ratio)
        draw.line([(0, y), (img_px_size, y)], fill=(r, g, b))

    # --------------------------------------------------------------------------------

    finder_positions = [(0, 0), (0, qr_size - 7), (qr_size - 7, 0)]

    def is_finder(i: int, j: int) -> bool:
        """
        Check if the given coordinates belong to a finder pattern.

        Args:
            i (int): Row index in QR matrix.
            j (int): Column index in QR matrix.

        Returns:
            bool: True if coordinates are in a finder pattern.
        """
        return any(
            fx <= i < fx + 7 and fy <= j < fy + 7
            for fx, fy in finder_positions
        )

    # --------------------------------------------------------------------------------

    for i in range(qr_size):
        for j in range(qr_size):
            if matrix[i][j]:
                x = (j + border) * box_size
                y = (i + border) * box_size
                box = [x, y, x + box_size - 1, y + box_size - 1]

                if is_finder(i, j):
                    draw.rounded_rectangle(box, radius=finder_radius, fill=qr_color)
                else:
                    draw.rectangle(box, fill=qr_color)

    # --------------------------------------------------------------------------------

    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        logo_size = int(img_px_size * logo_ratio)
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

        mask = Image.new('L', (logo_size, logo_size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, logo_size, logo_size), fill=255)

        logo.putalpha(mask)

        pos = ((img_px_size - logo_size) // 2, (img_px_size - logo_size) // 2)
        qr_img.paste(logo, pos, mask=logo)

    # --------------------------------------------------------------------------------

    output = BytesIO()
    qr_img.save(output, format="PNG")
    output.seek(0)

    return output
