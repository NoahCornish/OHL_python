OHL Stats Scraper

Overview: This repository contains a Python-based scraper for collecting
and processing Ontario Hockey League (OHL) player statistics. The script
fetches data directly from the OHL website, processes it into a
structured format, and saves the results as a CSV file. The repository
includes GitHub Actions for automating the scraper and updating the
repository with the latest stats.

Features:

Automated data collection: The script fetches real-time OHL player stats
from the official OHL data source. Structured output: The stats are
processed and saved in a CSV file for easy analysis and visualization.
Automation: The scraper runs automatically at: 4:30 AM EST (9:30 AM UTC)
11:00 PM EST (4:00 AM UTC) Repository updates: Automatically pushes
updated CSV files to the "OHL_STATS" folder. Repository Structure: .

.github/workflows run_stats_scraper.yml (GitHub Actions workflow for
automation) script.py (Main Python script for scraping and processing
data) requirements.txt (Python dependencies) OHL_STATS/ (Folder
containing the latest stats CSV) README.txt (Repository documentation)
Installation:

Clone the repository:

Download or clone this repository to your local machine using git clone
\<repository_url\>. Install dependencies:

Install required Python libraries using the requirements.txt file.
Usage: To manually run the scraper, execute the Python script script.py.
This will generate a CSV file named LeagueStats_2024_2025.csv and save
it in the "OHL_STATS" folder.

Automation: The scraper is configured to run automatically using GitHub
Actions. The workflow performs the following tasks:

Runs twice daily at 4:30 AM EST and 11:00 PM EST. Executes the scraper
and processes the data. Saves the CSV file to the "OHL_STATS" folder.
Commits and pushes the updated stats if changes are detected. The
automation workflow file can be found in
.github/workflows/run_stats_scraper.yml.

Contributing: Contributions are welcome! You can:

Submit issues for bugs or feature requests. Fork the repository and
create a pull request for improvements. License: This project is
licensed under the MIT License. See the LICENSE file for more details.

Contact: For questions or support, please contact
\[your-email@example.com\].
