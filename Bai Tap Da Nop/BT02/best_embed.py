from math import sqrt
from bitarray import bitarray
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt


def embed(msg_file, cover_img_file, stego_img_file):
    '''
    Nhúng tin mật vào ảnh gif (ảnh palette-base) bằng phương pháp của Fridrich 
    (xem file slide "06-AnTinMatTrenAnh2.pdf", trang 24).
    
    Các tham số:
        msg_file (str): Tên file chứa secret message.
        cover_img_file (str): Tên file chứa cover image.
        stego_img_file (str): Tên file chứa stego image (kết quả sau khi nhúng).
    Giá trị trả về:
        bool: True nếu nhúng thành không, False nếu không đủ chỗ để nhúng. 
    '''
    # Đọc cover img file
    cover_img = Image.open(cover_img_file)
    cover_pixels = np.array(cover_img)
    palette = cover_img.getpalette() # Kết quả là list các giá trị Red, Green, Blue của các màu 
                                     # trong bảng màu, 3 giá trị liên tiếp ứng với một màu
    palette = np.array(palette, dtype=np.uint8).reshape(1, -1, 3) # Reshape lại dưới dạng ảnh RGB
    # plt.figure()
    # plt.yticks([])
    # plt.imshow(palette, aspect=20) # Uncomment để xem bảng màu
    # plt.show()



    # YOUR CODE HERE

    def get_msg_bits(msg_file):
        with open(msg_file,'rb') as mf:
            msg_bytes = mf.read()
        
        #Window - CRLF text endline format (\r\n) to linux(Unix - LF) text format (\n)
        msg_bytes = msg_bytes.replace(b'\r',b'')
        msg_bits = bitarray()
        msg_bits.frombytes(msg_bytes)
        return msg_bits
    


   
    #get msg_bits
    msg_bits = get_msg_bits(msg_file)
    m = len(msg_bits)
    n = cover_pixels.size
    #kiểm tra độ dài bit của cover_pixels có đủ để chứa tất cả msg_bits k
    if n < m + 2:
        return False
    
    #padding
    pad = [1]
    pad.extend([0]*(n - m - 1))
    msg_bits.extend(pad)



    def distance(c1, c2):
        return sqrt(np.sum((c1 - c2)**2))
    #----------------------------------
    s = 0
    lookup_table = dict()    
    for i in range(len(palette[0])):
        color = palette[0, i]
        color = np.array(color, dtype = int)
        closest_distance = float('inf')
        closest_idx = 0
        for idx, clr in enumerate(palette[0]):
            clr = np.array(clr, dtype=int)
            if np.sum(color)%2 != np.sum(clr)%2:
                d = distance(clr, color)
                if d < closest_distance:
                    closest_distance = d
                    closest_idx = idx
        s += closest_distance
        lookup_table[i] = closest_idx
    
    print('Giá trị trung bình của khoảng cách nhỏ nhất: ',s/len(palette[0]))
    
    b = 0 #index của msg_bits
    for i in range(cover_pixels.shape[0]):
        for j in range(cover_pixels.shape[1]):
            pixel = cover_pixels[i, j]
            color = np.array(palette[0, pixel], dtype = int)
            if np.sum(color)%2 != msg_bits[b]:
                cover_pixels[i, j] = lookup_table[pixel] 
                b += 1
            else:
                b += 1
    stego_pixels = cover_pixels

    # Ghi stego pixels cùng palette xuống file
    stego_img = Image.fromarray(stego_pixels)
    stego_img.putpalette(cover_img.getpalette())
    stego_img.save(stego_img_file)
   
    return True


result = embed('msg2.txt', 'lena.gif', 'lena_stego.gif')
assert result == False
# TEST             
result = embed('msg.txt', 'lena.gif', 'lena_stego.gif')
assert result == True
stego_img = Image.open('lena_stego.gif')
stego_pixels = np.array(stego_img)
stego_palette = stego_img.getpalette()
correct_stego_img = Image.open('correct_lena_stego.gif')
correct_stego_pixels = np.array(correct_stego_img)
correct_stego_palette = correct_stego_img.getpalette()
assert np.all(stego_pixels == correct_stego_pixels)
assert stego_palette == correct_stego_palette


# TEST             
result = embed('msg.txt', 'baboon.gif', 'baboon_stego.gif')
assert result == True
stego_img = Image.open('baboon_stego.gif')
stego_pixels = np.array(stego_img)
stego_palette = stego_img.getpalette()
correct_stego_img = Image.open('correct_baboon_stego.gif')
correct_stego_pixels = np.array(correct_stego_img)
correct_stego_palette = correct_stego_img.getpalette()
assert np.all(stego_pixels == correct_stego_pixels)
assert stego_palette == correct_stego_palette


