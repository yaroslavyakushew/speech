from PIL import Image
import numpy as np
import os
import math as m



folder = "green_frames_20"

os.makedirs(folder)

def generate_primes(n):
    primes = []
    candidate = 2
    while len(primes) < n:
        is_prime = True
        for p in primes:
            if p > m.sqrt(candidate):
                break
            if candidate % p == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(candidate)
        candidate += 1
    return primes

goldCut = (m.sqrt(5) - 1)/2
amp_sum = 0

FPS = 30
numFrames = 60
K = 20
Nx = 400
Ny = 400
g = 9.81
H_S = 0.8
primes = generate_primes(K)



P = [p for p in primes if p >=3][:K]
p_max = max(P)
K_N = []
fi = []
theta = []
amplitude = []
normalized_amp = []
omega = []

sigma_t = H_S / 4
alfa_t = 0.7
Lx = 10
Ly = 10
L0 = 40
k0 = (2 * m.pi) / L0
lambda_min = 0.5



for i, p in enumerate(P):
    kn = k0 * p
    K_N.append(kn)

    amplitude_n = (2 * m.pi) / pow(kn, alfa_t)
    amplitude.append(amplitude_n)

    theta_n = (2 * m.pi) * ((i * goldCut) % 1)
    theta.append(theta_n)

    omega_t = m.sqrt(g * kn)
    omega.append(omega_t)

    fi_n = (2 * m.pi) * ((p * m.e) % 1)
    fi.append(fi_n)

for i in amplitude:
    amp_sum += m.pow(i, 2)
x1 = np.linspace(0, Lx, Nx)
y1 = np.linspace(0, Ly, Ny)
X, Y = np.meshgrid(x1, y1)
sigma_raw = m.sqrt((1/2) * amp_sum)
c = sigma_t / sigma_raw

for i in amplitude:
     amplitude_norm = c * i
     normalized_amp.append(amplitude_norm)


eta = []
for frame_num in range(1, 61):
   delta_x = Lx / Nx
   delta_y = Ly / Ny
   delta_t = (frame_num - 1) / FPS
   eta = np.zeros((Nx, Ny), dtype=np.float32)

   for e in range(len(P)):
      eta += normalized_amp[e] * np.cos(K_N[e] * (X * np.cos(theta[e]) + Y * np.sin(theta[e])) - omega[e] * delta_t + fi[e])
   eta_min = eta.min()
   eta_max = eta.max()
   eta_norm = (eta - eta_min) / (eta_max - eta_min + 1e-9)
   img_array = (eta_norm * 255).astype(np.uint8)
   img = Image.new('RGB', (Nx, Ny))
   pixels = img.load()
   for i in range(Ny):
       for j in range(Nx):
           val = img_array[i, j]
           r = int(0 + val * 0.6)
           g = int(100 + val * 0.6)
           b = int(0 + val * 0.6)
           pixels[j, i] = (r, g, b)
   filename = f'{folder}/frame_0{frame_num}.gif'
   img.save(filename)
   print(f'Створено кадр {frame_num}/60: {filename}')


print('\nВсі 60 зображень успішно створені!')
frames = []