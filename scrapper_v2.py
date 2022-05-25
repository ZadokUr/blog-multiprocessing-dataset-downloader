from multiprocessing import Process, Queue
from os import cpu_count
import requests
from bs4 import BeautifulSoup
import re
from termcolor import colored

source = 'https://vincentarelbundock.github.io/Rdatasets/datasets.html'
titles = []
filenames = []

def master():

    response = requests.get(source).content

    soup = BeautifulSoup(response, 'html.parser')

    urls = []
    trs = soup.select("tr > td:nth-of-type(3)")

    
    for tr in trs:
        string = tr.string
        titles.append(string[:len(string) - 1])

    # get all the urls that contain .csv in them
    for url in soup.find_all('a', href=re.compile('csv')):
        urls.append(url.get('href'))

    for i, link in enumerate(urls):
        url = str(url)
        try:
            name = re.search(r"AER\/(.*?)\.csv", link).group(1)
        except AttributeError:
            name = titles[i]
        filenames.append(name)

    work_queue = Queue()
    workers = []
    
    for i, url in enumerate(urls):
        work_queue.put((filenames[i],url))

    for i in range(cpu_count()):
        process = Process(target=download_csv, args=(work_queue,))
        workers.append(process)
        process.start()

    for worker in workers:
        work_queue.put(None)

    for worker in workers:
        worker.join()

    print(colored('DONE', 'green'))

# download csv from url, change name to specified fname

def download_csv(work_queue_items):
    while True:
        work_item = work_queue_items.get()
        
        if work_item is None:
            break

        fname = work_item[0]
        url = work_item[1]
        fname = re.sub('(\W+)','-', fname)
        dest_dir = r'csvs/' + str(fname) + '.csv'
        fx = open(dest_dir, 'wb')
        try:

            response = requests.get(url)
            
            fx.write(response.content) 
            fx.close()

            print(fname, 'succesfully downloaded and written')
        except:
            print(colored(f'An exception occurred file {fname} @ {url}', 'red'))

if __name__ == '__main__':
    master()
