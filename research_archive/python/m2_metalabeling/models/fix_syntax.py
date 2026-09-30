import os

base_dir = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Experts\HMA_SQX_Discovery'
files = ['Pipeline_Extractor_M1.mq5', 'Strategy 2.91.69.mq5']

broken_block = """string correctSymbol(string symbol){
    return _Symbol; // BLOQUEO HARDWARE CONTRA CACHE DE TESTER
}
        else if (symbol == "Subchart1Symbol") return correctSymbol(Subchart1Symbol);
    else if (symbol == "Subchart2Symbol") return correctSymbol(Subchart2Symbol);
    else return symbol;
}"""

fixed_block = """string correctSymbol(string symbol){
    return _Symbol; // BLOQUEO HARDWARE CONTRA CACHE DE TESTER
}"""

for file_name in files:
    file_path = os.path.join(base_dir, file_name)
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    if broken_block in code:
        code = code.replace(broken_block, fixed_block)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        print(f"Corregido error de sintaxis en {file_name}")
    else:
        print(f"No se encontro el bloque roto en {file_name}")

