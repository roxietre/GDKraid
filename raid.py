import json
import requests

url = "https://www.ghostfoundation.io/api/raid?skip=0"
response = requests.get(url)
data = response.json()

def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"


from datetime import datetime
from collections import defaultdict

def analyze_raids(raids):
    total_raids = len(raids)
    total_unique_raiders = len(set(raider['userId'] for raid in raids for raider in raid['raiders']))
    total_raiders = sum(len(raid['raiders']) for raid in raids)
    total_all_time_earnings = sum(raid['creator'].get('allTimeRaidEarnings', 0) for raid in raids)
    finished_raids = 0
    average_completion_time = None
    average_all_time_earnings = None
    
    for raid in raids:

        if len(raid['raiders']) == raid['raiderAmount']:
            finished_raids += 1
            last_raider = raid['raiders'][-1]
            finish_time = datetime.strptime(last_raider['completedAt'] , '%Y-%m-%dT%H:%M:%S.%fZ')
            completion_time = (finish_time - datetime.strptime(raid['createdAt'] , '%Y-%m-%dT%H:%M:%S.%fZ')).total_seconds()
            if average_completion_time is None:
                average_completion_time = completion_time
            else:
                average_completion_time = (average_completion_time + completion_time) / 2
    
    if total_raids > 0:
        average_all_time_earnings = total_all_time_earnings / total_raids
        average_reward = sum(raid['rewardPerRaider'] for raid in raids) / total_raids
    
    return {
        "Total Raids Ordered": total_raids,
        "Average Time Taken per Raid": format_time(average_completion_time),
        "Average Raid Reward": average_reward,
        "Total Unique Raiders": total_unique_raiders,
        "Total Raid Participants": total_raiders,
        "Average All-Time Raid Earnings": average_all_time_earnings,
        "Finished Raids": finished_raids
    }

def raids_per_day(raids):
    raid_data_per_day = defaultdict(lambda: {"raid_count": 0, "unique_raiders": set()})
    
    for raid in raids:
        raid_date = raid['createdAt'].split('T')[0]  # Extracting date from datetime string
        raid_data_per_day[raid_date]["raid_count"] += 1
        raid_data_per_day[raid_date]["unique_raiders"].update(raider['userId'] for raider in raid['raiders'])

    # Count unique raiders for each day
    for date, data in raid_data_per_day.items():
        data["unique_raiders"] = len(data["unique_raiders"])

    return dict(raid_data_per_day)


result = analyze_raids(data['raids'])
print(raids_per_day(data['raids']))

for key, value in result.items():
    print(f"{key}: {value}")