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
Recommended system: *Kali Linux 2021.3*.

- Needed Python libraries listed in *requirements.txt* file.

- The system needs following tools installed:
    - [OpenALPR](https://github.com/openalpr/openalpr/wiki/Compilation-instructions-(Ubuntu-Linux)#the-easy-way) (for license plate numbers recognition)
    - [Bulk-Extractor](https://www.kali.org/tools/bulk-extractor/) (for personal data extraction)

### Launching application
1. Install libraries listed in the [Requirements section](#requirements)
2. Put your sudo password inside *settings.py* file.
3. Launch the application from *app.py* file. Application is running on http://127.0.0.1:5000

## Screenshots
<img src="https://user-images.githubusercontent.com/52631916/183150249-d01ecbd2-e97e-41cb-bd11-cc01af2cdaae.png" alt="Detected devices screen" width="700"/>
<img src="https://user-images.githubusercontent.com/52631916/183150256-eee8462b-2c97-4b97-a8df-9115456157a9.png" alt="Extracted data screen" width="700"/>




## To do
- Extract names and surnames.
- Extract home addresses.
- Extract social media profiles.
