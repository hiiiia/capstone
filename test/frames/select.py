import os
import glob
import shutil

src_dir = '/home/wodbs/test/frames/'
dst_dir = '/home/wodbs/test/selected_frames/'

if not os.path.exists(dst_dir):
    os.makedirs(dst_dir)

images = glob.glob(os.path.join(src_dir, '*.png'))

selected_images = images[::50]

for fname in selected_images:
    shutil.copy(fname, dst_dir)


