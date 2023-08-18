import csv
import matplotlib.pyplot as plt

# Ler os dados do arquivo CSV
times = []
scales = []

with open('scale_data.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Pular o cabeçalho
    for index, row in enumerate(reader):
        times.append(index)  # Adiciona um valor de tempo baseado no índice da linha (0, 1, 2, ...)
        scales.append(float(row[1]))  # Supondo que a escala é o segundo campo em cada linha

# Plotar os dados
plt.figure(figsize=(10, 6))
plt.plot(times, scales, marker='o', linestyle='-')
plt.title("Variação de escala vs. tempo")
plt.xlabel("Tempo")
plt.ylabel("Escala")
plt.grid(True)
plt.tight_layout()
plt.show()
