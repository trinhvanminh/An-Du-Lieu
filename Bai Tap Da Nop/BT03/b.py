
from numpy.core.shape_base import block
import constants
from huffman import Huffman 
import jpeg_decoder

import struct 
import numpy as np
from scipy import fftpack
from PIL import Image
from bitarray import bitarray

def extract(stego_img_file, extr_msg_file):
    '''
    Hàm rút trích tin mật đã được nhúng vào ảnh jpeg.
    
    Các tham số:
        stego_img_file (str): Tên file chứa stego image.
        extr_msg_file (str): Tên file chứa secret message được rút trích.
    '''
    # Trong quá trình giải nén stego img file, lấy các hệ số quantized dct và bảng quatization
    quant_dct_coefs, quant_table = jpeg_decoder.get_quant_dct_coefs_and_quant_table(stego_img_file)
    # print(quant_dct_coefs.shape, quant_table.shape)
    
    # Phần còn lại là của bạn
    # YOUR CODE HERE
    embed_index = [
        4 , 5 , 6 , 7 ,
        11, 12, 13, 14,
        18, 19, 20, 21,
        25, 26, 27, 28,
        32, 33, 34, 35,
        40, 41, 42,
        48, 49,
        56
    ]
    quant_dct_coefs = quant_dct_coefs.reshape(-1, 64)
    extr_msg_bits = bitarray()
    for qdc in quant_dct_coefs:
        for i in embed_index:
            extr_msg_bits.extend([abs(qdc[i]) % 2])
    

    
    # Cắt đuôi '100...' ra khỏi msg bits
    extr_msg_bits = extr_msg_bits[:extr_msg_bits.to01().rfind('1')]
    
    # Ghi msg xuống file
    with open(extr_msg_file, 'wb') as f:
        f.write(extr_msg_bits)


# TEST
extract('stego.jpg', 'extr_msg.txt')
with open('extr_msg.txt', 'r') as f:
    extr_msg = f.read()
with open('msg.txt', 'r') as f:
    correct_extr_msg = f.read()
assert extr_msg == correct_extr_msg