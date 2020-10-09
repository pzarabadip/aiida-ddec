# -*- coding: utf-8 -*-
"""AiiDA DDEC plugin parser"""
from __future__ import absolute_import
import os
from aiida.parsers.parser import Parser
from aiida.common import NotExistent, OutputParsingError
from aiida.engine import ExitCode
from aiida.plugins import CalculationFactory
from aiida_ddec.utils import xyz2cif

DdecCalculation = CalculationFactory('ddec')  # pylint: disable=invalid-name


class DdecParser(Parser):
    """
    Parser class for parsing output of multiplication.
    """

    # pylint: disable=protected-access
    def parse(self, **kwargs):
        """Parse output structur, store it in database in CifData format."""

        # Check that the retrieved folder is there
        try:
            out_folder = self.retrieved
        except NotExistent:
            self.logger.error('No retrieved folder found')
            return self.exit_codes.ERROR_NO_RETRIEVED_FOLDER

        # Check what is inside the folder
        # list_of_files = out_folder._repository.list_object_names()  # pylint: disable=protected-access
        list_of_files = out_folder.list_object_names()
        
        for f in list_of_files:
            if f.endswith('.output'):
                output_file = f
                break

        # output_file = self.node.process_class._DEFAULT_OUTPUT_FILE

        # We need at least the output file name as defined in calcs.py
        if output_file not in list_of_files:
            raise self.exit_codes.ERROR_NO_OUTPUT_FILE

        finished = False
        with out_folder.open(output_file) as handle:
            for line in handle.readlines():
                if 'Finished chargemol in' in line:
                    finished = True

        if not finished:
            raise OutputParsingError('Calculation did not finish correctly')

        # Create CifData object from the following the file path returned by xyz2cif
        with out_folder.open('DDEC6_even_tempered_net_atomic_charges.xyz') as handle:
            output_cif = xyz2cif(handle.name)
        
        self.out('structure_ddec', output_cif)

        if 'DDEC6_even_tempered_atomic_spin_moments.xyz' in list_of_files:
        
            with out_folder.open('DDEC6_even_tempered_atomic_spin_moments.xyz') as handle:
                output_cif_spin = xyz2cif(handle.name)
            self.out('structure_ddec_spin', output_cif_spin)

        # output_cif = xyz2cif(
        #     os.path.join(
        #         out_folder._repository._get_base_folder().abspath, 'DDEC6_even_tempered_net_atomic_charges.xyz'
        #     )
        # )
        # output_cif_spin = xyz2cif(
        #     os.path.join(
        #         out_folder._repository._get_base_folder().abspath, 'DDEC6_even_tempered_atomic_spin_moments.xyz'
        #     )
        # )
        
        

        return ExitCode(0)
