
from numpy.core.fromnumeric import ptp
from numpy.core.shape_base import block
from numpy.lib.function_base import _quantile_unchecked
import constants
from huffman import Huffman 
import jpeg_decoder

import struct 
import numpy as np
from scipy import fftpack
from PIL import Image
from bitarray import bitarray
# import bitarray


# YOUR CODE HERE (OPTION)


def dct2(pixels):
    '''
    Hàm biến đổi từ ma trận điểm ảnh sang ma trận hệ số DCT (2 ma trận có cùng shape).
    '''
    return fftpack.dct(fftpack.dct(pixels, axis=0, norm='ortho'), axis=1, norm='ortho')

def idct2(dct_coefs):
    '''
    Hàm biến đổi từ ma trận hệ số DCT sang ma trận điểm ảnh (2 ma trận có cùng shape).
    '''
    return fftpack.idct(fftpack.idct(dct_coefs, axis=0 , norm='ortho'), axis=1, norm='ortho')

def get_header(img_height, img_width, quant_table):
    '''
    Hàm tính chuỗi byte ứng với header của ảnh JPEG.
    (Code được điều chỉnh từ nguồn: https://github.com/reinhrst/pygreypeg.)
    '''
    buf = bytearray()

    def writebyte(val):
        buf.extend(struct.pack(">B", val))

    def writeshort(val):
        buf.extend(struct.pack(">H", val))

    # SOI
    writeshort(0xFFD8)  # SOI marker

    # APP0
    writeshort(0xFFE0)  # APP0 marker
    writeshort(0x0010)  # segment length
    writebyte(0x4A)     # 'J'
    writebyte(0x46)     # 'F'
    writebyte(0x49)     # 'I'
    writebyte(0x46)     # 'F'
    writebyte(0x00)     # '\0'
    writeshort(0x0101)  # v1.1
    writebyte(0x00)     # no density unit
    writeshort(0x0001)  # X density = 1
    writeshort(0x0001)  # Y density = 1
    writebyte(0x00)     # thumbnail width = 0
    writebyte(0x00)     # thumbnail height = 0

    # DQT
    quant_table = quant_table.reshape(-1)
    writeshort(0xFFDB)  # DQT marker
    writeshort(0x0043)  # segment length
    writebyte(0x00)     # table 0, 8-bit precision (0)
    for index in constants.zz:
        writebyte(quant_table[index])

    # SOF0
    writeshort(0xFFC0)  # SOF0 marker
    writeshort(0x000B)  # segment length
    writebyte(0x08)     # 8-bit precision
    writeshort(img_height)
    writeshort(img_width)
    writebyte(0x01)     # 1 component only (grayscale)
    writebyte(0x01)     # component ID = 1
    writebyte(0x11)     # no subsampling
    writebyte(0x00)     # quantization table 0

    # DHT
    writeshort(0xFFC4)                     # DHT marker
    writeshort(19 + constants.dc_nb_vals)  # segment length
    writebyte(0x00)                        # table 0 (DC), type 0 (0 = Y, 1 = UV)
    for node in constants.dc_nodes[1:]:
        writebyte(node)
    for val in constants.dc_vals:
        writebyte(val)

    writeshort(0xFFC4)                     # DHT marker
    writeshort(19 + constants.ac_nb_vals)
    writebyte(0x10)                        # table 1 (AC), type 0 (0 = Y, 1 = UV)
    for node in constants.ac_nodes[1:]:
        writebyte(node)
    for val in constants.ac_vals:
        writebyte(val)

    # SOS
    writeshort(0xFFDA)  # SOS marker
    writeshort(8)       # segment length
    writebyte(0x01)     # nb. components
    writebyte(0x01)     # Y component ID
    writebyte(0x00)     # Y HT = 0
    # segment end
    writebyte(0x00)
    writebyte(0x3F)
    writebyte(0x00)

    return buf

def embed(msg_file, cover_img_file, quant_table, stego_img_file):
    '''
    Nhúng tin mật vào ảnh jpeg (lossy) bằng phương pháp LSB với k = 1 
    (xem file slide "07-AnTinMatTrenAnh3.pdf", trang 13).
    Để đơn giản, ở đây ta sẽ giả định: ảnh là ảnh xám, 
                                       có chiều dài và chiều rộng chia hết cho 8.
    
    Các tham số:
        msg_file (str): Tên file chứa secret message.
        cover_img_file (str): Tên file chứa cover image.
        quant_table (mảng numpy 8x8): Bảng quantization (bảng các số chia ở bước quantization).
        stego_img_file (str): Tên file (*.jpg) chứa stego image (kết quả sau khi nhúng).
    Giá trị trả về:
        bool: True nếu nhúng thành không, False nếu không đủ chỗ để nhúng. 
    '''
    # I. Đọc cover img file
    # YOUR CODE HERE

    cover_img = Image.open(cover_img_file)
    cover_pixels = np.array(cover_img,dtype=int)
    width, height = cover_img.size
    max_bits_per_block = 26
    
    
    # II. Đọc msg file, chuyển msg thành msg bits, kiểm xem có đủ chỗ nhúng không, thêm 100... vào msg bits
    # YOUR CODE HERE
    
    # Đọc msg file
    with open(msg_file, 'r') as f:
        msg = f.read()
    msg_bits = bitarray()
    msg_bits.frombytes(msg.encode('utf-8'))
    
    # Kiểm xem có nhúng được không?
    capacity = max_bits_per_block*(cover_pixels.size//64)
    if len(msg_bits) + 1 > capacity:
        return False

    # Thêm '100...' vào msg bits
    msg_bits.extend('1' + '0' * (capacity - len(msg_bits) - 1))

    # III. Nén jpeg, trong quá trình nén thực hiện nhúng msg bits
    jpeg_bytes = bytearray()
    jpeg_bytes.extend(get_header(height, width, quant_table))
    huf = Huffman()
    
    # Lần lượt duyệt các khối ảnh 8x8 (theo thứ tự từ trái qua phải, từ trên xuống dưới)
    # Với mỗi khối:
    # (1) Trừ 128 rồi tính các hệ số DCT
    # (2) Tính các hệ số quantized DCT
    # (3) Nhúng msg bits vào các hệ số quantized DCT
    # (4) Nén các hệ số quantized DCT bằng thuật toán nén Huffman
    #     Để nén dùng câu lệnh `huf.encode_block(quant_dct_coefs, length)`
    #     Trong đó: 
    #     - `quant_dct_coefs` là mảng 1 chiều các hệ số quantized DCT 
    #       (có được bằng cách duyệt mảng 2 chiều theo thứ tự dích dắc:
    #       đầu tiên, kéo mảng 2 chiều thành mảng một chiều, 
    #       rồi duyệt mảng một chiều này theo mảng chỉ số `constants.zz` đã được định nghĩa sẵn cho bạn)
    #     - `length` là số lượng phần tử của mảng `quant_dct_coefs` tính
    #       từ phần tử đầu cho đến phần tử khác 0 cuối cùng 
    #       (lưu ý: có thể xảy ra trường hợp tất cả phần tử đều bằng 0)
    # YOUR CODE HERE
    
    k = 0   #duyệt từng bits

    #vị trí nhúng sau khi chuyển về mảng một chiều
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

    # cover_pixels.size = 8*8*blocks 
    # chia ảnh thành các khối 8x8
    for r in range(0,cover_pixels.shape[0] - 8 + 1, 8):
        for c in range(0,cover_pixels.shape[1] - 8 + 1, 8):
            block = cover_pixels[r:r+8,c:c+8]
            # (1) Trừ 128 rồi tính các hệ số DCT
            dct = dct2(block - 128)
            # (2) Tính các hệ số quantized DCT
            quantized = np.array(np.round(dct / quant_table), dtype=int)
            # (3) Nhúng msg bits vào các hệ số quantized DCT
            # Đưa về mảng 1 chiều
            quantized = quantized.flatten()
            # Nhúng msg_bits

            for idx in embed_index:
                quantized[idx] = ((quantized[idx]>>1<<1) | int(msg_bits[k]))
                k += 1
    
            
            # (4) Nén các hệ số quantized DCT bằng thuật toán nén Huffman
            # duyệt theo dạng zig-zag thành từng block rồi thêm block vào quant_dct_coefs
            
            quant_dct_coefs = []
            for i in constants.zz:
                quant_dct_coefs.append(quantized[i])

            try:
                # Lấy số lượng phần tử của mảng `quant_dct_coefs` tính từ phần tử đầu cho đến phần tử khác 0 cuối cùng         
                length = np.max(np.nonzero(quant_dct_coefs)) + 1
                huf.encode_block(quant_dct_coefs, length)
            except:
                pass
           
 
    # Kết thúc encode và lấy buffer cho vào jpeg_bytes
    jpeg_bytes.extend(huf.end_and_get_buffer())
    jpeg_bytes.extend(struct.pack(">H", 0xFFD9))  # EOI marker
    

    # IV. Ghi kết quả nén jpeg xuống file
    with open(stego_img_file, 'wb') as f:
        f.write(jpeg_bytes)

    return True

# TEST
quant_table = np.array([
    16, 11, 10, 16,  1,  1,  1,  1,
    12, 12, 14,  1,  1,  1,  1, 55,
    14, 13,  1,  1,  1,  1, 69, 56,
    14,  1,  1,  1,  1, 87, 80, 62,
     1,  1,  1,  1, 68, 109, 103, 77,
     1,  1,  1, 64, 81, 104, 113, 92,
     1,  1, 78, 87, 103, 121, 120, 101,
     1, 92, 95, 98, 112, 100, 103, 99
]).reshape(8, 8)
# result = embed('msg2.txt', 'cover.bmp', quant_table, 'stego.jpg')
# assert result == False

# TEST
result = embed('msg.txt', 'cover.bmp', quant_table, 'stego.jpg')
assert result == True

# assert np.all(np.array(Image.open('stego.jpg')) == np.array(Image.open('correct_stego.jpg')))


a = np.array(Image.open('stego.jpg'))
b = np.array(Image.open('correct_stego.jpg'))

with open('arr.txt','w') as f:
    for i in range(a.shape[0]):
        for j in range(a.shape[1]):
            f.write(str(a[i,j]) + ' ')
        f.write('\n')
with open('arr2.txt','w') as f:
    for i in range(b.shape[0]):
        for j in range(b.shape[1]):
            f.write(str(b[i,j]) + ' ')
        f.write('\n')


# print(a)
# print(b)