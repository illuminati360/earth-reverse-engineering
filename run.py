import streetview
import sys
from PIL import Image
import os.path

if __name__ == '__main__':
	if len(sys.argv) < 3: exit()
	lat, lon = map(lambda x: float(x), sys.argv[1:])
	filename = "/root/AltSpaceMREs/public/pano/" + "%s,%s.png" % (sys.argv[1], sys.argv[2])
	if os.path.exists(filename):
		print (True)
		exit()


	panoids = streetview.panoids(lat, lon)

	if len(panoids) < 1:
		print (False)
		exit()
	panoid = panoids[0]['panoid']
	panorama = streetview.download_panorama_v3(panoid, zoom=3, disp=False)
	im = Image.fromarray(panorama)
	# filename = "/root/AltSpaceMREs/public/pano/skybox.png"
	im.save(filename)
	print (True if os.path.isfile(filename) else False)