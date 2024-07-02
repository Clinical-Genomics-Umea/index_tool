# index_tool
A tool to save sequencing indices in a json-based format for illumina sequencing.

Main reasons for converting to this format are:
1. A need to include and override cycle patterns with the indexes.
2. Simplification of making Illumina samplesheet v2 files (using the tool ...) .
3. Ability to store all data as documents in a mongodb database.

Indices can be imported for conversion from illumina index kit definition files (tsv) or from custom csv files.



