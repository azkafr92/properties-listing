from requests_html import HTMLSession
import sqlite3
import time
from numpy import arange
import traceback

session = HTMLSession()
con = sqlite3.connect('db.sqlite3')
cur = con.cursor()
'''
# rumah123.com: get listing link
for i in range(1,101):
    # page limit: 100
    print('Inserting page {}...'.format(i))
    r = session.get("""https://www.rumah123.com/jual/dki-jakarta/residensial/?page={}""".format(i))
    
    listing_url_container = r.html.find('.listing-list',first=True).absolute_links
    listing_url = [(url,time.time()) for index,url in enumerate(listing_url_container) if '/properti/' in url]
    cur.executemany('INSERT OR IGNORE INTO rumah123_links(url,date_time) VALUES (?,?)',listing_url)
    con.commit()
    print('Inserting page {}...done'.format(i))

print('Assigning url id...')
cur.execute('UPDATE rumah123_links SET `id` = _rowid_')
con.commit()
print('Assigning url id...done')
'''
# rumah123.com get listing details
number_of_links = cur.execute('''SELECT MAX(`id`) FROM rumah123_links''').fetchone()[0]
worker_id_list = [i for i in range(1,number_of_links+1,int(number_of_links/5))]
worker_id_list[-1] = number_of_links+1
# function to setup worker
def worker_setup(start,end):
    url_list = cur.execute('''SELECT url FROM rumah123_links WHERE `id`>={} AND `id`<{} '''.format(start,end)).fetchall()
    for url in url_list:
        url = url[0]
        listing_id = url.rsplit('/',maxsplit=2)[-2]
        print('Scraping {}...'.format(listing_id))
        r = session.get(url)
        with open('rumah123/{}.txt'.format(listing_id),'w') as file:
            try:
                file.write(str(r.html.find('.ListingDetailstyle__LeftContainerWrapper-gGbuvg',first=True).html))
            except:
                traceback.print_exc()
        print('Scraping {}...done'.format(listing_id))
#setup worker 1
worker_setup(worker_id_list[0],worker_id_list[1])
#setup worker 2
worker_setup(worker_id_list[1],worker_id_list[2])
#setup worker 3
worker_setup(worker_id_list[2],worker_id_list[3])
#setup worker 4
worker_setup(worker_id_list[3],worker_id_list[4])
#setup worker 5
worker_setup(worker_id_list[4],worker_id_list[5])

# hargarumah.id


# rumahdijual.com
    

# www.99.co/id/rumah-dijual-di-jakarta