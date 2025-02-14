#Par un professeur
import os
import requests
import time
from typing import Optional
from pathlib import Path

class CovidDataDownloader:
    def __init__(self, base_path: str = "data/covid"):
        """
        Initialize the downloader with a base path for saving files.
        
        Args:
            base_path (str): Directory where files will be saved
        """
        self.base_path = Path(base_path)
        self.api_url = "https://api.github.com/repos/CSSEGISandData/COVID-19/contents/csse_covid_19_data/csse_covid_19_daily_reports"
        self.session = requests.Session()
        # Set user agent to avoid potential API limitations
        self.session.headers.update({
            'User-Agent': 'Covid19DataDownloader/1.0',
        })

    def create_directory(self) -> None:
        """Create the download directory if it doesn't exist."""
        self.base_path.mkdir(parents=True, exist_ok=True)

    def get_file_list(self) -> list:
        """
        Fetch the list of files from GitHub API.
        
        Returns:
            list: List of file information dictionaries
        """
        print("Fetching repository contents...")
        response = self.session.get(self.api_url)
        response.raise_for_status()
        
        files = response.json()
        csv_files = [f for f in files if f['name'].endswith('.csv')]
        print(f"Found {len(csv_files)} CSV files in repository")
        return csv_files

    def download_file(self, file_info: dict, retry_count: int = 3) -> bool:
        """
        Download a single file with retry mechanism.
        
        Args:
            file_info (dict): File information dictionary from GitHub API
            retry_count (int): Number of retry attempts
            
        Returns:
            bool: True if download successful, False otherwise
        """
        file_path = self.base_path / file_info['name']
        
        for attempt in range(retry_count):
            try:
                response = self.session.get(file_info['download_url'])
                response.raise_for_status()
                
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                return True
                
            except Exception as e:
                if attempt == retry_count - 1:  # Last attempt
                    print(f"Failed to download {file_info['name']}: {str(e)}")
                    return False
                time.sleep(1)  # Wait before retry
                continue
        
        return False

    def download_all_files(self) -> None:
        """Download all CSV files from the repository."""
        self.create_directory()
        
        try:
            files = self.get_file_list()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch file list: {str(e)}")
            return

        successful_downloads = 0
        failed_downloads = 0
        
        for i, file_info in enumerate(files, 1):
            print(f"[{i}/{len(files)}] Downloading {file_info['name']}...")
            
            if self.download_file(file_info):
                successful_downloads += 1
            else:
                failed_downloads += 1
            
            time.sleep(0.5)  # Rate limiting
        
        # Print summary
        print("\nDownload Summary:")
        print(f"Total files found: {len(files)}")
        print(f"Successfully downloaded: {successful_downloads}")
        print(f"Failed downloads: {failed_downloads}")

def main():
    """Main function to run the downloader."""
    # Create downloader instance with custom download path
    downloader = CovidDataDownloader("covid_data")
    
    try:
        downloader.download_all_files()
    except KeyboardInterrupt:
        print("\nDownload interrupted by user")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
