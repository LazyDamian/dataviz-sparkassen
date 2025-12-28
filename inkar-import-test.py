import requests
import os
import zipfile


# Example usage
url = "https://www.bbr-server.de/imagemap/inkar/download/inkar_2025.zip"

output_folder = ""

# Step 1: Download the ZIP file
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    zip_file_path = os.path.join(output_folder, 'downloaded_file.zip')

    with open(zip_file_path, 'wb') as zip_file:
        zip_file.write(response.content)


    with zipfile.ZipFile('downloaded_file.zip', 'r') as zip_ref:
        zip_ref.extractall(zip_file_path)

    print(f"Downloaded and unzipped to {output_folder}")
else:
    print(f"Failed to download file: {response.status_code}")


