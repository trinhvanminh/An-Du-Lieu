import math
from PIL import Image
import numpy as np


def compute_polynomial(p, coefs, xs):
    '''
    Tính giá trị của hàm đa thức.

    Các tham số:
        coefs (mảng numpy một chiều): Các hệ số của hàm đa thức, 
                                        f(x) = coefs[0] + coefs[1]*x + coefs[2]*x^2 + ...
        xs (mảng numpy một chiều): Các giá trị x mà tại đó cần tính f(x).
    Giá trị trả về:
        Mảng numpy một chiều: Phần tử chỉ số i trong mảng này bằng f(xs[i]).
    '''
    # TODO
    f_xs = np.zeros(xs.shape, dtype=int)
    for i in range(len(coefs)):
        xs_pow_i = np.ones(xs.shape, dtype=int)
        for j in range(i):
            xs_pow_i = (xs_pow_i * xs) % p

        # lossy
        if coefs[i] > 250:
            coefs[i] = 250

        f_xs = (f_xs + coefs[i] * xs_pow_i % p) % p
        # print(f_xs)
        # input()

    return f_xs


def split(ori_image, split_image, n, k, p=251):
    '''
    Hàm phân chia ảnh mật ori_image m pixel thành k phần (k nhóm) sao cho chỉ khi có ít nhất là k phần (k <= n)
    thì mới tái tạo được ori_image, còn ít hơn k phần thì sẽ không biết gì về s.

    Các tham số:
        ori_image (*.bmp): Ảnh cần chia sẻ.
        n (int): Số phần cần phân chia.
        k (int): Ngưỡng k (k <= n).
    Giá trị trả về:
        n ảnh mang tên split_image$.bmp
    '''
    pixels = np.array(Image.open(ori_image))
    m = pixels.size
    # padding 0 -> m % k == 0
    padded_pixels = np.append(pixels, (k - m % k)*[0])
    # reshape into group
    padded_pixels = padded_pixels.reshape(-1, k)
    groups_len = padded_pixels.shape[0]
    # 2D array
    result_arr = np.zeros((groups_len, n), dtype=int)

    for i in range(groups_len):
        # Lấy các hệ số từ k pixels
        coefs = padded_pixels[i]
        xs = np.arange(n) + 1
        ys = compute_polynomial(p, coefs, xs)
        result_arr[i] = ys

    # input()

    for i in range(n):
        new_pixels = result_arr[:, i]
        print(new_pixels)
        # padding
        new_pixels = np.append(new_pixels, [0]*(262144 - len(new_pixels)))
        new_pixels = new_pixels.reshape(512, 512)
        print(new_pixels)
        input()
        # Ghi new pixels xuống file
        Image.fromarray(new_pixels, 'L').save(
            split_image.split('.')[0] + str(i + 1) + '.bmp')


def compute_inv(p, x):
    for i in range(p):
        if i * x % p == 1:
            return i
    return None


def compute_lagrange_interpolation(p, xs, ys, x):
    '''
    Tính nội suy Lagrange.

    Các tham số:
        xs, ys (2 mảng numpy có cùng len & len = bậc-của-f + 1): ys[i] = f(xs[i]).
        x (int): Giá trị x mà tại đó cần tính f(x) bằng nội suy Lagrange.
    Giá trị trả về:
        int: Giá trị f(x)
    '''
    # TODO
    f_x = 0
    for i in range(len(xs)):
        delta = 1
        for j in range(len(xs)):
            if j != i:
                delta = delta * \
                    (((x - xs[j]) % p) *
                     compute_inv(p, (xs[i] - xs[j]) % p) % p) % p
        f_x = (f_x + ys[i] * delta % p) % p

    return f_x


def join(p, xs, ys, k):
    '''
    Tái tạo tin mật s từ n' phần của tin mật (n' >= k).

    Các tham số:
        xs, ys (2 mảng numpy một chiều, len = n'): n' phần của tin mật: phần thứ 1 là (xs[0], ys[0]), 
                                                                        phần thứ 2 là (xs[1], ys[1]), 
                                                                        ...
        k (int): Ngưỡng k mà đã dùng khi phân chia tin mật.
    Giá trị trả về:
        int: Tin mật s được tái tạo,
                trong trường hợp không đủ số phần để tái tạo tin mật thì trả về None.
    '''
    # TODO
    if len(xs) < k:
        return None

    s = compute_lagrange_interpolation(p, xs[:k], ys[:k], 0)

    return s


def get_xs_ys(split_image, n, k, p=251):
    # kích thước ban đầu của part (chưa padding)
    ori_size = math.ceil(262144 / k)
    result_arr = np.zeros((n, ori_size), dtype=int)
    for i in range(n):
        pixels_part = np.array(Image.open(
            split_image.split('.')[0] + str(i + 1) + '.bmp'))
        # loại bỏ padding
        pixels_part = pixels_part.flatten()[:ori_size]
        result_arr[i] = pixels_part
    result_arr = result_arr.T
    print(result_arr)
    print(result_arr.size)
    print(result_arr.shape)


# get_xs_ys('part.bmp', 5, 3, 251)
split('cover.bmp', 'part.bmp', 5, 3, 251)


# # Chọn ngẫu nhiên n' phần để tái tạo tin mật
# rand_idxs = np.random.permutation(np.arange(len(xs)))
# n_prime = k - 1
# rec_s = join(p, xs[rand_idxs[:n_prime]], ys[rand_idxs[:n_prime]], k)
# print(rec_s)
# n_prime = k
# rec_s = join(p, xs[rand_idxs[:n_prime]], ys[rand_idxs[:n_prime]], k)
# print(rec_s)
# n_prime = k + 1
# rec_s = join(p, xs[rand_idxs[:n_prime]], ys[rand_idxs[:n_prime]], k)
# print(rec_s)


# # Phân chia tin mật
# p = 251
# s = 100 # byte
# k = 25
# n = 50
# xs, ys = split(p, s, n, k)

# # Chọn ngẫu nhiên n' phần để tái tạo tin mật
# rand_idxs = np.random.permutation(np.arange(len(xs)))
# n_prime = k
# rec_s = join(p, xs[rand_idxs[:n_prime]], ys[rand_idxs[:n_prime]], k)
# print(rec_s)
