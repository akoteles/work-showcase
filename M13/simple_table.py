import pandas as pd

# Simple 4-column table
data = [
    [23, '27, 28', 19, '<55 ns'],
    [28, '30, 32, 33, 34, 36', 20, '<110 ns'],
    [45, '58', 44, '2.1 ms'],
    [73, '108', 83, '76 ms'],
    [60, '82, 83, 85, 86, 88, 90', 68, '55.1 s'],
    [61, 'NONE', 67, '1.48 s'],
    [66, '90, 92, 94, 95, 96, 97, 98', 72, '200 ms'],
    [67, '98', 73, '6 ms']
]

df = pd.DataFrame(data, columns=['Z', 'N (stable)', 'N (unstable)', 'Decay Time'])

print("=" * 80)
print("ISOTOPE NEUTRON COUNT REFERENCE")
print("=" * 80)
print(df.to_string(index=False))
print("=" * 80)
