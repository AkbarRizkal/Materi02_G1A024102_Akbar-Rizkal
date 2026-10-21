from concurrent.futures import ProcessPoolExecutor
from time import perf_counter
import math
import os

def flood_risk(cell):
    # Data sintetis: elevasi, curah hujan, jarak ke sungai
    elevation, rainfall, river_distance = cell
    elevation_score = max(0, 1 - elevation / 20)
    rain_score = min(rainfall / 200, 1)
    river_score = max(0, 1 - river_distance / 5)
    risk = 0.45 * elevation_score + 0.35 * rain_score + 0.20 * river_score
    return round(risk, 4)

def main():
    # Data sintetis berukuran besar untuk mendemonstrasikan workload HPC
    n = 100_000
    cells = [
        ((i * 7 % 25) + 1, (i * 13 % 250) + 10, (i * 3 % 10) / 2)
        for i in range(n)
    ]

    start = perf_counter()
    serial = [flood_risk(c) for c in cells]
    serial_time = perf_counter() - start

    # Pecah data menjadi bagian agar worker mengerjakan batch
    chunks = [cells[i:i + 5000] for i in range(0, len(cells), 5000)]
    start = perf_counter()
    with ProcessPoolExecutor(max_workers=os.cpu_count() or 2) as pool:
        parallel_chunks = list(pool.map(process_chunk, chunks))
    parallel = [value for chunk in parallel_chunks for value in chunk]
    parallel_time = perf_counter() - start

    print(f"Jumlah titik simulasi: {n:,}")
    print(f"Risiko rata-rata: {sum(serial) / len(serial):.4f}")
    print(f"Waktu serial: {serial_time:.3f} detik")
    print(f"Waktu paralel: {parallel_time:.3f} detik")
    if parallel_time > 0:
        print(f"Speedup: {serial_time / parallel_time:.2f}x")
    print("Catatan: paralel belum tentu lebih cepat untuk tugas kecil karena overhead proses.")

def process_chunk(chunk):
    return [flood_risk(cell) for cell in chunk]

if __name__ == "__main__":
    main()
