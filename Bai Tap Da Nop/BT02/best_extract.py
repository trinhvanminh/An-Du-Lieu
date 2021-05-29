
from bitarray import bitarray
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt


def extract(stego_img_file, extr_msg_file):
    '''
    Hàm rút trích tin mật đã được nhúng vào ảnh bằng phương pháp của Fridrich.
    
    Các tham số:
        stego_img_file (str): Tên file chứa stego image.
        extr_msg_file (str): Tên file chứa secret message được rút trích.
    '''
    # YOUR CODE HERE
    correct_stego_img = Image.open(stego_img_file)
    correct_stego_pixels = np.array(correct_stego_img)
    correct_stego_palette = correct_stego_img.getpalette()
    correct_stego_palette = np.array(correct_stego_palette, dtype=np.uint8).reshape(1, -1, 3)
    
    msg_bits = []
    for i in range(len(correct_stego_pixels)):
        for j in range(len(correct_stego_pixels[0])):
            rgb = correct_stego_palette[0][correct_stego_pixels[i][j]]
            msg_bits.append((int(rgb[0]) + int(rgb[1]) + int(rgb[2])) % 2) 

    #tim vi tri bit 1 đầu tiên tính từ đuôi
    k = -1
    while(msg_bits[k] == 0):
        k = k - 1
    
    # [0, 1, 0,.....] --> bitarray('010.....')
    msg_bits = bitarray(msg_bits[:k])
    # # bit to bytes to msg
    # msg = msg_bits.tobytes().decode('utf-8')
    # save
    with open(extr_msg_file,'wb') as f:
        f.write(msg_bits)



# TEST
extract('correct_baboon_stego.gif', 'extr_msg.txt')
with open('extr_msg.txt', 'r') as f:
    extr_msg = f.read()
with open('msg.txt', 'r') as f:
    correct_extr_msg = f.read()
assert extr_msg == correct_extr_msg