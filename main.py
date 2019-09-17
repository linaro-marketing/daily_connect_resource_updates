import boto3
import sys
import datetime
import requests
from secrets import SCHED_API_KEY

class GetDailyResourcesUpdates:
    def __init__(self, connect_code):
        self.connect_code = connect_code.lower()
        self.API_KEY = SCHED_API_KEY
        # Get a list of presentations uploaded to a given bucket/path
        presentations_uploaded = self.fetch_files_from_s3_path("static-linaro-org","connect/san19/presentations/")
        # Get a list of videos uploaded to a given bucket/path
        videos_uploaded = self.fetch_files_from_s3_path("static-linaro-org", "connect/san19/videos/")
        # Get the resources uploaded today (parsed in arg)
        todays_presentations = self.get_files_modified_today(presentations_uploaded)
        todays_videos = self.get_files_modified_today(videos_uploaded)
        print("Daily Presentation Updates")
        print("--------------------------")
        self.get_human_readable_list(todays_presentations)
        print("--------------------------")
        print("Daily Video Updates")
        print("--------------------------")
        self.get_human_readable_list(todays_videos)
        print("--------------------------")

    def get_human_readable_list(self, obj_list):
        """Prints a human readable list of resources that have been made available on a given date"""
        if len(obj_list) > 0:
            for entry in obj_list:
                # print(entry[0])
                self.fetch_session_details_from_sched(entry[0])
        else:
            print("Sorry but there have not been any updates...")

    def fetch_session_details_from_sched(self, session_id):
        """ Returns an array of session details based on a session id"""
        data = requests.get(
            url="https://linaroconnectsandiego.sched.com/api/session/list?api_key={0}&since=1282755813&format=json".format(self.API_KEY)).json()
        for sched_entry in data:
            if session_id.upper() in sched_entry["name"]:
                # print(sched_entry)
                print("{0} - https://connect.linaro.org/resources/san19/{1}/".format(sched_entry["name"], session_id))
                return True
        return False

    def get_files_modified_today(self, obj_list):
        """Gets a list of entries that were modified today from a list returned by fetch_files_from_s3_path"""
        todays_date = datetime.datetime.strptime(sys.argv[1], "%d/%m/%Y")
        matched_resources = []
        for entry in obj_list:
            if entry[1].month == todays_date.month and entry[1].day == todays_date.day:
                matched_resources.append(entry)
        return matched_resources

    def fetch_files_from_s3_path(self, s3_bucket, s3_path):
        """ Fetches a list of files from an s3 path/bucket """
        s3 = boto3.resource('s3')
        bucket = s3.Bucket('static-linaro-org')
        uploaded_files = []
        for obj in bucket.objects.filter(Prefix=s3_path):
            file_name = obj.key
            session_id = file_name.split(".")[0].split("/")[-1]
            dateModified = obj.last_modified
            uploaded_files.append([session_id, dateModified])
        if len(uploaded_files) > 0:
            return uploaded_files
        else:
            return False
if __name__ == "__main__":
    daily_updates = GetDailyResourcesUpdates("SAN19")
