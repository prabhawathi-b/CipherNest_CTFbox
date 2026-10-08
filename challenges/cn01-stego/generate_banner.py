from PIL import Image, ImageDraw

img = Image.new("RGB", (800, 400), (12, 42, 90))
d = ImageDraw.Draw(img)
d.rectangle([20, 20, 780, 380], outline=(255, 255, 255), width=3)
d.text((60, 150), "CeylonGov Secure", fill=(255, 255, 255))
d.text((60, 190), "Public Relations Archive - Staging Backup", fill=(200, 200, 200))
d.text((60, 230), "ceylongov_banner.png", fill=(150, 150, 150))

img.save("/build/banner_cover.png", "PNG")
print("Cover image generated.")
