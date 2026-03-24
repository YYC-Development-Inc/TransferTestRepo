
1. Browse site and capture HAR file
2. Parse HAR files using 'parsehar.py'
  a. Before parsing, alter the 'endpoint' setting in the config.json file to match the ventrek endpoint in the HAR file being processed
  b. Command Line:
    python3 parsehar.py 003app.ventrek.com.har app-003.json
    python3 parsehar.py 003app2.ventrek.com.har app2-003.json

3. Compare the request and responses using 'comparerequests.py'
  a. Command Line:
  	python3 comparerequests.py app-003.json app2-003.json


Notes:
From within windows wsl, you can get your downloads folder as follows:

  /mnt/c/Users/<your_username>/Downloads

So for example:
python3 parsehar.py /mnt/c/Users/mhept/Downloads/003app.ventrek.com.har app-003.json
