import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from termcolor import colored


# download csv from link, change name to specified fname

def download_csv(fname, url):
    error_file = open("error-log", "w")

    try:
        fname = re.sub('(\W+)','-', fname)
        dest_dir = r'csvs/' + str(fname) + '.csv'
        fx = open(dest_dir, "wb")

        response = requests.get(url)
        
        fx.write(response.content)

        print(fname, "succesfully downloaded and written")
        fx.close()
    except:
        print(colored(f"An exception occurred file {fname} @ {url}", "red"))
        error_file.write(f"An exception occurred file {fname} @ {url} \n")

    error_file.close()


url = "https://vincentarelbundock.github.io/Rdatasets/datasets.html"
url = requests.get(url).content

soup = BeautifulSoup(url, 'html.parser')

trs = soup.select("tr > td:nth-of-type(3)")
titles = []
links = []
filenames = []

# get title names from title column in table
for tr in trs:
    string = tr.string
    titles.append(string[:len(string) - 1])

# get all the links that contain .csv in them
for link in soup.find_all("a", href=re.compile("csv")):
    links.append(link.get('href'))

# get all the names of the files as were named
for i, link in enumerate(links):
    link = str(link)
    try:
        name = re.search(r"AER\/(.*?)\.csv", link).group(1)
    except AttributeError:
        name = titles[i]
    filenames.append(name)

# write a csv file that indexes file names with the names of the datasets
data_tuples = list(zip(titles, filenames))
df = pd.DataFrame(data_tuples, columns=["Dataset Name", "File name"])
df.to_csv("Dataset Phonebook.csv")

for i, url in enumerate(links):
    download_csv(filenames[i], url)

print(colored("DONE", "green"))
