# Project - Extracting personal data from drive

### Features
Extracting 
- phone numbers, 
- url addresses, 
- e-mail addresses, 
- license plates number 

from files in connected external drive.

### Requirements
Tested on *Kali Linux 2021.3*.

Needed Python libraries listed in [requirements.txt](https://gitlab.com/pawelptak/personal-data-extractor/-/blob/master/requirements.txt) file.

The system needs following tools installed:
- [OpenALPR](https://github.com/openalpr/openalpr/wiki/Compilation-instructions-(Ubuntu-Linux)#the-easy-way) (for license plate numbers recognition)
- [Bulk-Extractor](https://www.kali.org/tools/bulk-extractor/) (for personal data extraction)
