import pygtfs
from pygtfs import Schedule

import gtfs

if __name__ == "__main__":
    schedule: Schedule = pygtfs.Schedule("gtfs.sqlite")
    gtfs.update_gtfs_db(schedule)
