from dataclasses import dataclass
from typing import Optional
from pathlib import Path
import os


TEST_SEQ_DIR = Path(__file__).parent 

class SadToMadx:
    """ Class that contains basic building blocks to convert lattices from sad to madx""" 
    def __init__(self, momentum, path_to_sad_sequence, madx_output_file, **kwargs) -> None:
        self.momentum = momentum 
        self.path_to_sad_sequence = path_to_sad_sequence
        self.madx_output_file = madx_output_file
        self.n_cores = kwargs.pop('n_cores', 1)
        self.sad_twiss_output = kwargs.pop('sad_twiss_output', '')     

        self.TWISS_FUNCTION = str(TEST_SEQ_DIR / "twiss.n")
        self.TUNE_MATCHING = str(TEST_SEQ_DIR / "tunematching.n")
        self.SAD_TO_MADX_FUNCTION = str(TEST_SEQ_DIR / "SAD2MADX.n")

        self.READ_SAD = f"""
                ON ECHO;

                READ "{self.path_to_sad_sequence}";

                FFS USE RING;
                NPARA={self.n_cores};
                MOMENTUM = {self.momentum}; ! GEV;
                CONVERGENCE=10^-32;
                RAD; ! Turn on radiation in all elements.
                NOFLUC; ! Turn off quantum effects.
                RADCOD; ! calculate orbit considering radiation loss
                RADTAPER; ! automatic tapering of all magnets according to local energy of the closed orbit.

                MINCOUP=2e-3;

                INS;
                CALCULATE;
                """


        self.MATCH_TUNES = f"""
                (* ----------------------ADJUST TUNE----------------------------------------- *)

                USE RING;
                INS;
                CALCULATE;

                Get["{self.TUNE_MATCHING}"]; 
                ax0=0;
                bx0=0.3;
                ay0=0;
                by0=.001; ! the values at IP
                bxmrf=200;
                bymrf=200; ! the maximum betas at rf cavities
                bxmds=2000;
                bymds=2000; ! maximum at QI* and QU*

                (* Working point for ZH lattice *)
                AdjustTune[389.13000, 389.20000]; 

                SAVE;
                VARIABLES;
                CALCULATE;
                """

        self.PRINT_TWISS = f"""
                (* ----------------------PRINT TWISS----------------------------------------- *)
                USE RING;
                CELL;
                CALCULATE;

                Get["{self.TWISS_FUNCTION}"];
                SaveTwissFile["{self.sad_twiss_output}"];
                """


        self.CONVERT_SAD_TO_MAD = f"""
                (* ----------------------CONVERT SAD SEQUENCES TO MAD SEQUENCE--------------- *)
                Get["{self.SAD_TO_MADX_FUNCTION}"];

                mx=SAD2MADX[fname->"{self.madx_output_file}"];
                mx@CreateMADX[];
                """
        
        self.EXIT = "Exit[];"


    def convert_to_madx(self, tune_matching = False):
        if tune_matching:
            command = self.READ_SAD + self.MATCH_TUNES + self.CONVERT_SAD_TO_MAD + self.EXIT
        else:
            command = self.READ_SAD + self.CONVERT_SAD_TO_MAD + self.EXIT
        self.run_sad_command(command)


    def run_sad_command(self, command):
        
        f = open("temp.job", "w")
        f.write(command)
        f.close()
        os.system(f"/home/fcarlier/git-projects/SAD/bin/gs temp.job")
        os.remove("temp.job")

