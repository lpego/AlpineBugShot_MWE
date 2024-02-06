import pandas as pd
from pathlib import Path
import json
import re
import shutil

workdir = Path().absolute()
anns = workdir.parents[1] / "toolexplore" / "alpine-bug-shot-classifications_07Nov2023.csv"
subj = workdir.parents[1] /  "toolexplore" / "alpine-bug-shot-subjects_07Nov2023.csv"

### annotations prep
anns = pd.read_csv(anns)
anns = anns[anns['user_name'].str.contains("not-logged-in")] # filter out non-anonymous users for privacy
anns = anns[anns['workflow_version'] > 57] # filter out non-current workflow versions
anns = anns[700:800] # get a representative subset of rows (eyeballing it)

anns.to_csv(Path(workdir.parents[0] / "data" / "anns_MWE.csv"), sep=',', encoding='utf-8', index=True)

### subject set prep
subj = pd.read_csv(subj)
subj_set = set(anns['subject_ids']) # grab unique values of subject_ids from anns, make into a set
subj[subj['subject_id'].isin(subj_set)] # keep only those rows

subj.to_csv(Path(workdir.parents[0] / "data" / "subj_MWE.csv"), sep=',', encoding='utf-8', index=True)

### workflows not such a big file, copy as is. 

### grab annotations with an insect in them
anns_positives = []
for index, row in anns.iterrows():
    if json.loads(row["annotations"])[0]['value'] == "Yes": 
        # print(row)
        anns_positives.append(row)
print("There are", len(anns_positives), "frames with events. ")

### grab images containing an insect for these annotations
pics_list = []
for i in anns_positives: 
    pics = re.findall(r'PICT[a-zA-Z0-9-_\.]+', str(i.subject_data))
    pics_list.append(pics)

def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)
        
for pic1 in pics_list: 
    for pic2 in pic1: 
        print("Now finding file:", pic2)
        file = find(pic2, Path("E:\Annotations"))
        try: 
            print(Path(file))
            print("File found! Copying over now... ")
            shutil.copy2(Path(file), Path(workdir.parents[0] / "data" / "frames"))
        except: 
            print("No file found!     (ㅠ﹏ㅠ)")
