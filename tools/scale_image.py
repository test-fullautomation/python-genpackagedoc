import os
import subprocess

IRFANVIEW_EXE = r"C:\Program Files\IrfanView\i_view64.exe"
SCALE_FACTORS = [95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45]

def scale_image_with_irfanview(image_path):
    folder, filename = os.path.split(image_path)
    name, ext = os.path.splitext(filename)
    ext = ext.lstrip('.')
    for factor in SCALE_FACTORS:
        out_name = f"{name}_{factor}.{ext}"
        out_path = os.path.join(folder, out_name)
        cmd = [
            IRFANVIEW_EXE,
            image_path,
            f"/resize=({factor}p,{factor}p)",
            "/resample",
            "/aspectratio",
            "/jpg_quality=100",
            f"/convert={out_path}"
        ]
        print(f"Skaliere auf {factor}%: {out_path}")
        subprocess.run(cmd, check=True)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python scale_image.py <image_path>")
        sys.exit(1)
    scale_image_with_irfanview(sys.argv[1])
