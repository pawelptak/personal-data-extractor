# Extracting personal data from drive

### Features
Extracting 
- phone numbers, 
- url addresses, 
- e-mail addresses, 
- credit card numbers,
- license plates numbers,
- exif data

from files in connected external drive.

### Requirements
Tested on *Kali Linux 2021.3*.

- Needed Python libraries listed in [requirements.txt](https://gitlab.com/pawelptak/personal-data-extractor/-/blob/master/requirements.txt) file.

- The system needs following tools installed:
    - [OpenALPR](https://github.com/openalpr/openalpr/wiki/Compilation-instructions-(Ubuntu-Linux)#the-easy-way) (for license plate numbers recognition)
    - [Bulk-Extractor](https://www.kali.org/tools/bulk-extractor/) (for personal data extraction)

### Launching application
1. Install libraries listed in the [Requirements section](#requirements)
2. Create *settings_development.py* file in the same directory as the *settings.py* file
3. Put your sudo password inside *settings_development.py* in the following form 
```
sudoPassword = 'your_password'
```
 
4. Launch the application from *app.py* file. Application is running on http://127.0.0.1:5000

## To do
- Extract names and surnames.
- Extract home addresses.
- Extract social media profiles.
- Generate reports.
