# CaisisTools
Tools to transform Caisis data into cBioPortal format, including extensions specific to Oncoscape V3.

Caisis is a clinical database system. Oncoscape is a visualization and hypothesis generation tool developed at Fred Hutchinson Cancer Research Center. The cBioPortal project has produced a set of file formats for trnasporting molecular data (principly) and clinical data (secondarily), and Oncoscape uses that format for importing data. This project takes an export from Caisis, in the form of an Excel workbook, and transform it into cBioPortal-compatible tab-separated (TSV) files that Oncoscape can import. In addition, it adds some decoration with Oncoscape extensions to the cBioPortal format.


