import streetview
import sys
from PIL import Image

if __name__ == '__main__':
	if len(sys.argv) < 3: exit()
	lat, lon = map(lambda x: float(x), sys.argv[1:])
	panoids = streetview.panoids(lat, lon)

	panoid = panoids[0]['panoid']
	panorama = streetview.download_panorama_v3(panoid, zoom=3, disp=False)
	im = Image.fromarray(panorama)
	im.save("/root/AltSpaceMREs/public/pano/" + "%f,%f.png" % (lat, lon))