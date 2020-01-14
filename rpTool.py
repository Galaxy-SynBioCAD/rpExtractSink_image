import csv
import os
import pickle
import gzip
from rdkit.Chem import MolFromSmiles, MolFromInchi, MolToSmiles, MolToInchi, MolToInchiKey, AddHs
import sys
import logging
import io
import re
import libsbml

import rpSBML

## Class to read all the input files
#
# Contains all the functions that read the cache files and input files to reconstruct the heterologous pathways
class rpExtractSink:
    ## InputReader constructor
    #
    #  @param self The object pointer
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info('Starting instance of rpExtractSink')
        self.mnxm_strc = None #There are the structures from MNXM


    #######################################################################
    ############################# PRIVATE FUNCTIONS #######################
    #######################################################################


    ## Generate the sink from a given model and the
    #
    # NOTE: this only works for MNX models, since we are parsing the id
    # TODO: change this to read the annotations and extract the MNX id's
    #
    def genSink(self, input_sbml, compartment_id='MNXC3'):
        sbml_data = input_sbml.read().decode("utf-8")
        rpsbml = rpSBML.rpSBML('inputModel', libsbml.readSBMLFromString(sbml_data))
        file_out = io.StringIO()
        ### open the cache ###
        cytoplasm_species = []
        for i in rpsbml.model.getListOfSpecies():
            if i.getCompartment()==compartment_id:
                cytoplasm_species.append(i)
        count = 0
        writer = csv.writer(file_out, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(['Name','InChI'])
        for i in cytoplasm_species:
            res = rpsbml.readMIRIAMAnnotation(i.getAnnotation())
            #extract the MNX id's
            try:
                mnx = res['metanetx'][0]
            except KeyError:
                continue
            try:
                inchi = self.mnxm_strc[mnx]['inchi']
            except KeyError:
                inchi = None
            if mnx and inchi:
                writer.writerow([mnx,inchi])
                count += 1
        file_out.seek(0)
        if count==0:
            return ''
        else:
            return file_out
