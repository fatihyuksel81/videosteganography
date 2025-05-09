from PIL import Image
import random

ISARETLEYICI_RENK = (255, 0, 255)

def createData(data):
    yeniveri = []
    for i in data.encode('utf-8'):
        yeniveri.append(format(i, '08b'))
    return yeniveri

def pixelDuzenle(pix, data):
    verilist = createData(data)
    lenveri = len(verilist)
    imveri = iter(pix)

    for i in range(lenveri):
        pixels = [value for value in imveri.__next__()[:3]+
                  imveri.__next__()[:3]+
                  imveri.__next__()[:3]]

        for j in range(0, 8):
            if (verilist[i][j] == '0' and pixels[j]%2 != 0):
                pixels[j] -= 1
            elif (verilist[i][j] == '1' and pixels[j]%2 == 0):
                if(pixels[j]!= 0):
                    pixels[j] -= 1
                else:
                    pixels[j] += 1

        if (i == lenveri - 1):
            if (pixels[-1] % 2 == 0):
                if(pixels[-1] != 0):
                    pixels[-1] -= 1
                else:
                    pixels[-1] += 1
        else:
            if (pixels[-1] % 2 != 0):
                pixels[-1] -= 1

        yield tuple(pixels[0:3])
        yield tuple(pixels[3:6])
        yield tuple(pixels[6:9])

def enc_gom(img, data):
    w = img.size[0]
    (x, y) = (0, 0)
    pixel_iterator = iter(img.getdata())
    next(pixel_iterator)
    x = 1
    for pixel in pixelDuzenle(pixel_iterator, data):
        img.putpixel((x, y), pixel)
        if (x == w - 1):
            x = 0
            y += 1
        else:
            x += 1

def encode(image_paths, message):
    if not image_paths:
        raise ValueError("Lütfen en az bir resim dosyası yolu belirtin.")
    if not message:
        raise ValueError('Gömülecek veri boş olamaz.')

    num_frames = len(image_paths)
    data_bayt = message.encode('utf-8')
    parca_boyutu = 1024 
    veri_parcalari = [data_bayt[i:i + parca_boyutu] for i in range(0, len(data_bayt), parca_boyutu)]
    parca_sayisi = len(veri_parcalari)

    if parca_sayisi > num_frames:
        raise ValueError(f"Veri çok büyük. Saklamak için {parca_sayisi} çerçeve gerekiyor, ancak {num_frames} çerçeve var.")

    saklanacak_indeksler = random.sample(range(num_frames), parca_sayisi)
    saklanacak_indeksler.sort()

    print(f"Veri şu çerçevelere saklanıyor: {saklanacak_indeksler}")

    for i, indeks in enumerate(saklanacak_indeksler):
        img_path = image_paths[indeks]
        img = Image.open(img_path).convert("RGB")
        parca = veri_parcalari[i].decode('utf-8', errors='ignore')
        img.putpixel((0, 0), ISARETLEYICI_RENK)
        enc_gom(img, parca)
        img.save(img_path)

def decode(image_paths):
        decoded_message = ''
        for img_path in image_paths:
            try:
                image = Image.open(img_path, 'r').convert("RGB")
                print(f"Dosya okunuyor: {img_path}")
                if image.getpixel((0, 0)) == ISARETLEYICI_RENK:
                    print(f"{img_path} dosyasında veri bulundu.")
                    imgdata = iter(image.getdata())
                    next(imgdata)
                    parca_bin_str = ''
                    while (True):
                        pixels = [value for value in imgdata.__next__()[:3] +
                                          imgdata.__next__()[:3] +
                                          imgdata.__next__()[:3]]
                        binstr = ''
                        for i in pixels[:8]:
                            if (i % 2 == 0):
                                binstr += '0'
                            else:
                                binstr += '1'
                        decoded_message += chr(int(binstr, 2))
                        print(f"Okunan binstr: {binstr}, Karakter: {decoded_message[-1]}")
                        if (pixels[-1] % 2 != 0):
                            print("Mesaj sonu bulundu.")
                            return decoded_message
                else:
                    print(f"{img_path} dosyasında işaretleyici renk bulunamadı.")
            except FileNotFoundError:
                print(f"Uyarı: {img_path} dosyası bulunamadı.")
            except Exception as e:
                print(f"Bir hata oluştu ({img_path}): {e}")
                print(f"Hata ayrıntıları: {str(e)}")
        return decoded_message