import os
import sys
import pandas as pd 


if engine == "bmad":
    bmad_file = "temporary_lattice_for_twiss.bmad"
    self.to_bmad(file_path=bmad_file)

    TAO_PYTHON_DIR=os.environ['ACC_ROOT_DIR'] + '/tao/python'
    sys.path.insert(0, TAO_PYTHON_DIR)
    
    import pytao
    from io import StringIO

    tao = pytao.Tao()
    tao.init(f"-noinit -noplot -lattice_file {bmad_file}")
    bmad_twiss = tao.cmd('show lattice -python -all -custom bmad_custom.twiss')
    df = pd.read_csv(StringIO("\n".join(line for line in bmad_twiss)), sep=';')
    df.drop([0], inplace=True)
    df = df[df['NAME'] != 'BEGINNING']
    df = df[df['NAME'] != 'END']
    
    col_types = df.iloc[0]
    for col in df:
        if col_types[col] == 'INT':
            df[col] = df[col].astype(int)
        elif col_types[col] == 'REAL':
            df[col] = df[col].astype(float)

