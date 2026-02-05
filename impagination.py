import textwrap

with open("./output/trascrizione_corretta.txt", "r", encoding="utf-8") as f:
    text = f.read()

wrapped = textwrap.fill(text, width=150)
print("...In corso")

with open("./output/trascrizione_corretta.txt", "w", encoding="utf-8") as f:
    f.write(wrapped)

print(f"Impaginazione {f.name} completata!")