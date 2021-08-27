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
        f_xs = (f_xs + coefs[i] * xs_pow_i % p) % p
    
    return f_xs

def split(p, s, n, k):
    '''
    Hàm phân chia tin mật s thành n phần sao cho chỉ khi có ít nhất là k phần (k <= n)
    thì mới tái tạo được s, còn ít hơn k phần thì sẽ không biết gì về s.
    
    Các tham số:
        s (int): Tin mật cần chia sẻ.
        n (int): Số phần cần phân chia.
        k (int): Ngưỡng k (k <= n).
    Giá trị trả về:
        2 mảng numpy một chiều: Gọi 2 mảng này là xs và ys,
                                n phần được phân chia:  phần thứ 1 là (xs[0], ys[0]),
                                                        phần thứ 2 là (xs[1], ys[1]),
                                                        ...
                                với ys[i] = f(xs[i]).
    '''
    # Tạo ra k hệ số của hàm f bậc k-1, 
    # trong đó hệ số bậc 0 [ứng với f(0)] bằng s.
    # TODO
    coefs = np.random.randint(0, p, k)
    coefs[0] = s
    
    # Tính f(1), f(2), ..., f(n)
    # TODO
    xs = np.arange(n) + 1
    ys = compute_polynomial(p, coefs, xs)
    
    return xs, ys  


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
                delta = delta * (((x - xs[j]) % p) * compute_inv(p, (xs[i] - xs[j]) % p) % p) % p
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

# Phân chia tin mật
p = 101
s = 100
k = 3
n = 5
xs, ys = split(p, s, n, k)

# Chọn ngẫu nhiên n' phần để tái tạo tin mật
rand_idxs = np.random.permutation(np.arange(len(xs)))
n_prime = k - 1
rec_s = join(p, xs[rand_idxs[:n_prime]], ys[rand_idxs[:n_prime]], k)
print(rec_s)
n_prime = k
rec_s = join(p, xs[rand_idxs[:n_prime]], ys[rand_idxs[:n_prime]], k)
print(rec_s)
n_prime = k + 1
rec_s = join(p, xs[rand_idxs[:n_prime]], ys[rand_idxs[:n_prime]], k)
print(rec_s)



# Phân chia tin mật
p = 101
s = 100
k = 25
n = 50
xs, ys = split(p, s, n, k)

# Chọn ngẫu nhiên n' phần để tái tạo tin mật
rand_idxs = np.random.permutation(np.arange(len(xs)))
n_prime = k
rec_s = join(p, xs[rand_idxs[:n_prime]], ys[rand_idxs[:n_prime]], k)
print(rec_s)