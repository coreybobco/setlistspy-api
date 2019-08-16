import csv, operator, requests, time
from django.core.management.base import BaseCommand
from collections import OrderedDict
from multiprocessing import Pool

'''Because there is too much data from Mixesdb for Neo4j to reasonably handle, this command will create a whitelist
of DJ's to import based on specified whitelists (a DJ's label, the label of the artists they play, the artists they play).
Other possible future filter criteria: podcast/mix lists'''
class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        # Named (optional) arguments
        # parser.add_argument(
        #     '--all_criteria',
        #     action='store_true',
        #     dest='all_whitelists',
        #     default=False,
        #     help='Use all whitelist methods to filter for DJs',
        # )
        # parser.add_argument(
        #     '--dj_labels',
        #     action='store_true',
        #     dest='dj_labels',
        #     default=False,
        #     help='Scrape the setlist data for all DJs in the database',
        # )
        # parser.add_argument(
        #     '--track_labels',
        #     action='store_true',
        #     dest='track_labels',
        #     default=False,
        #     help='Scrape the DJs',
        # )
        parser.add_argument(
            '--refresh_label_ids',
            action='store_true',
            dest='refresh_label_ids',
            default=False,
            help='Refresh the list of discogs label ids from labels.csv',
        )

    def handle(self, *args, **options):
        # print(options)
        label_discogs_ids = dict()
        if options['refresh_label_ids']:
            print('uh')
            # dclient = discogs_client.Client('setspyfm/0.1 +http://setspy.fm', user_token='oqhqdajdVlZmgHLZiyTPupGBmKvrgHWxdYhcChvc')
            label_discogs_ids = OrderedDict()
            with open("labels.csv", "r") as labels_csv:
                csv_reader = csv.reader(labels_csv, delimiter='\t')
                for row in csv_reader:
                    if len(row) == 1:
                        try:
                            label_name = row[0]
                            label_discogs_id = dclient.search(label_name, type='label')[0].id
                            label_discogs_ids[label_name] = label_discogs_id
                        except IndexError:
                            print("Could not find Discogs ID for " + label_name)
                    else:
                        label_discogs_ids[row[0]] = row[1]
            labels_csv.close()
            with open('labels.csv', 'w') as labels_csv:
                writer = csv.writer(labels_csv, delimiter='\t')
                for label_name, discogs_id in label_discogs_ids.items():
                    writer.writerow([label_name, discogs_id])
            labels_csv.close()
        discogs_label_ids = list()
        with open('labels.csv', 'r') as label_csvfile:
            reader = csv.reader(label_csvfile, delimiter='\t')
            for row in reader:
                discogs_label_ids.append(row[1])
        # print(requests.get("https://api.discogs.com/oauth/access_token"))
        # discogs_label_ids = [discogs_label_ids[0]]
        print(discogs_label_ids)
        with Pool(2) as p:
            label_whitelists = p.map(get_label_whitelist, discogs_label_ids)
        total_whitelist = set()
        [total_whitelist.update(whitelist) for whitelist in label_whitelists]
        with open('label_artists.csv', 'w') as label_artists_csv:
            writer = csv.writer(label_artists_csv, delimiter='\t')
            for dj in total_whitelist:
                writer.writerow([dj])
        label_artists_csv.close()
        sort_csv(label_artists_csv)

def get_label_whitelist(label_id):
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
                "User-Agent": 'setspyfm/0.1 http://setlistspy.fm'}
    label_whitelist = set()
    on_last_page = False
    page = 1
    while not on_last_page:
        try:
            api_url = "https://api.discogs.com/labels/" + str(label_id) + "/releases?per_page=100&page=" + str(page) + "&key=fuelZcVMjZGjNMQikxcm&secret=UtcHrSRqnVCTJFkDjmYFxtqjmYjUQYBh"
            print(headers)
            response_json = requests.get(api_url, headers).json()
            label_releases_json = response_json['releases']
        except KeyError:
            print(api_url)
            print(response_json)
            time.sleep(63)
            response_json = requests.get(api_url, headers).json()
            label_releases_json = response_json['releases']
        for release in label_releases_json:
            label_whitelist.add(release['artist'])
        on_last_page = True if response_json['pagination']['page'] * response_json['pagination']['per_page'] >= response_json['pagination']['items'] else False
        page +=1
    print(label_id)
    print(label_whitelist)
    return label_whitelist

def sort_csv(filename):
    data = csv.reader(open(filename),delimiter='\t')
    sortedlist = sorted(data, key=operator.itemgetter(0))    # 0 specifies according to first column we want to sort
    #now write the sorte result into new CSV file
    with open(filename, "w") as f:
      fileWriter = csv.writer(f, delimiter='\t')
      for row in sortedlist:
          fileWriter.writerow(row)
