### This script is to parse the annotations file downloaded from Zooniverse

# %% # ----------------------------------------------------------------
### Libraries import
import pandas as pd
import json
import csv
import numpy as np
from pathlib import Path

# %% # ----------------------------------------------------------------
### SET PARAMETERS
### Set filepath and read in data
workdir = Path().absolute()
file_path = workdir.parents[0] / "data"/ "anns_MWE.csv"

### Read in full annotations file
anns = pd.read_csv(file_path)
print("# of annotations total:", len(anns))

### Shave off any annotations with older versions of the workflow
### Workflow version >= 56.55
anns = anns.loc[anns["workflow_version"] >= 56, :]
print("# of annotations on current workflow(s):", len(anns))

### Remove unnecessary columns
anns = anns[["subject_data", "annotations", "subject_ids"]]

# %% # ----------------------------------------------------------------
### Check how many annotations have insect visits recorded
empties = 0
insects = 0
for i in anns["annotations"]:
    if json.loads(i)[0]['value'] == "No": empties += 1
    else: insects += 1
print("Images without insects: ", empties)
print("Images with insect: ", insects)
# empties + insects == len(anns) # sanity check

# %% # ----------------------------------------------------------------
### Function definitions

### Function to recursively convert nested lists to tuples
def convert_nested_lists_to_tuples(obj):
    if isinstance(obj, list):
        return tuple(convert_nested_lists_to_tuples(item) for item in obj)
    return obj

### Function to recursively convert tuples back to lists
def convert_nested_tuples_to_lists(obj):
    if isinstance(obj, tuple):
        return [convert_nested_tuples_to_lists(item) for item in obj]
    return obj

### Function to evaluate if something is a list, a number or NaN
def is_nan_or_list(variable):
    if isinstance(variable, list):
        return False  # It's a list
    elif isinstance(variable, (float, int)) and np.isnan(variable):
        return True  # It's NaN
    else:
        return False  # It's neither NaN nor a list

# %% # ----------------------------------------------------------------
### ANNOTATIONS PARSING - focal_frames, subject_ids, insect taxon, number and behaviour
### Initialize dictionary with parsing values
parsing_keys = []

parsing_keys.append("subject_ids")

for i in range(-2,3): # focal_frames
    parsing_keys.append("focal_frame_" + str(i))

for i in ["taxon", "how_many", "behaviour"]: 
    parsing_keys.append(i)

parsing_keys.append("BB_value")

parsing_dict = {}
for k in parsing_keys: 
    parsing_dict[k] = []

### Iterating over rows and parsing most info in one pass (except bounding boxes)
for index, row in anns.iterrows(): 
    ### subject_ids
    # print("\n", row["subject_ids"])
    parsing_dict["subject_ids"].append(row["subject_ids"])
    ### subject_data - focal_frames
    # print(json.loads(row["subject_data"]).keys())
    iter_subject_id = list(json.loads(row["subject_data"]).keys())[0] # iteratively grab the dictionary key name
    for k in parsing_keys[1:6]: # focal_frames
        # print(k)
        try: parsing_dict[k].append(json.loads(row["subject_data"])[iter_subject_id][k])
        except: parsing_dict[k].append(np.nan)
    ### annotations - insect identity, number and behaviour
    try: 
        # print(json.loads(row["annotations"])[2]['value'][0]['choice'])
        parsing_dict["taxon"].append(json.loads(row["annotations"])[2]['value'][0]['choice'])
    except: 
        # print("NaN")
        parsing_dict["taxon"].append(np.nan)
    try: 
        # print(json.loads(row["annotations"])[2]['value'][0]['answers']['HOWMANY'])
        parsing_dict["how_many"].append(json.loads(row["annotations"])[2]['value'][0]['answers']['HOWMANY'])
    except: 
        # print("NaN")
        parsing_dict["how_many"].append(np.nan)
    try: 
        # print(json.loads(row["annotations"])[2]['value'][0]['answers']['WHATBEHAVIORSDOYOUSEE'][0])
        parsing_dict["behaviour"].append(json.loads(row["annotations"])[2]['value'][0]['answers']['WHATBEHAVIORSDOYOUSEE'][0])
    except: 
        # print("NaN")
        parsing_dict["behaviour"].append(np.nan)
    ### BB values
    try: 
        # print(json.loads(row["annotations"])[1]['value'])
        parsing_dict["BB_value"].append(json.loads(row["annotations"])[1]['value'])
    except: 
        # print("NaN")
        parsing_dict["BB_value"].append(np.nan)

### sanity check - keys should be all same length (if so, this must evaluate to True): 
if all(len(parsing_dict["subject_ids"]) == len(l) for l in parsing_dict.values()): print(True)
else: print(False)

# %% # ----------------------------------------------------------------
### Reshape parsed annotations to unpack subject_ids into its various focal_frames

### convert to dataframe
parsing_df = pd.DataFrame(parsing_dict)

### Melt dataframe and unpack focal_frames
parsing_df_melted = pd.melt(
    parsing_df,
    id_vars=['subject_ids', 'taxon', 'how_many', 'behaviour', 'BB_value'],
    value_vars=[col for col in parsing_df.columns if col.startswith('focal_frame')],
    var_name='focal_frame_id',
    value_name='focal_frame'
)

### DO NOT DROP DUPLICATES HERE - we want 1:5 correspondence between user annotations (1) and unpacked focal_frames (5)
### if you drop duplicates, you get rid of all the empties... 

### sort dataframe for better readability
focal_frames_dict = {'focal_frame_-2': 0, 'focal_frame_-1': 1, 'focal_frame_0': 2, 'focal_frame_1': 3, 'focal_frame_2': 4} # for custom sorting
parsing_df_melted['rank'] = parsing_df_melted['focal_frame_id'].map(focal_frames_dict) # apply custom sorting order in temp column
parsing_df_melted = parsing_df_melted.sort_values(['subject_ids', 'rank']) # sort by subject_ids nad temp column
parsing_df_melted = parsing_df_melted.drop('rank', axis=1) # drop temp column

# %% # ----------------------------------------------------------------
### ANNOTATIONS PARSING - Parsing Bounding Box (BB) info
### iterate over JSON elements and populate lists
BB_concat_out = []
BB_frame = []
BB_frame_list = []
BB_rowinfo = {"index": [], "subject_ids": [], "frame": []}

for index, row in parsing_df_melted.iterrows():
    # print(index)
    # print("\n", row['BB_value'])
    if is_nan_or_list(row['BB_value']): # if there is any NaN, skip
        # print("Empty row, skipping...")
        continue
    else: # otherwise, parse the contents
        # print("There's stuff here!")
        z = 0
        BB_concat_in = []
        BB_frame = []
        # print("Number of boxes is", len(row['BB_value']))
        while z < len(row['BB_value']): 
            # print(row['BB_value'][z])
            row_frame = row["focal_frame_id"]
            if row['BB_value'][z]["frame"] == (int(row_frame.replace("focal_frame_", ""))+2): # proceed only if BB corresponds to focal_frame in row
                BB_frame = (row['BB_value'][z]["frame"])
                temp_dict = {"x":[], "y":[], "width":[], "height":[]}
                temp_dict["x"] = row['BB_value'][z]["x"]
                temp_dict["y"] = row['BB_value'][z]["y"]
                try:
                    temp_dict["width"]=(temp_dict["x"] + row['BB_value'][z]["width"])
                except:
                    temp_dict["width"] = np.nan
                try:
                    temp_dict["height"]=(temp_dict["y"] + row['BB_value'][z]["height"])
                except:
                    temp_dict["height"] = np.nan
                BB_concat_in.append(list(temp_dict.values()))
            z += 1
        if len(BB_concat_in) > 0: 
            BB_concat_out.append(BB_concat_in)
            BB_rowinfo["index"].append(index)
            BB_rowinfo["subject_ids"].append(row["subject_ids"])
            BB_rowinfo["frame"].append(row["focal_frame_id"])
            ### NOTE: BB_frame_list needs to be filled only once per row;  
            ### if appended in the while cycle it could have duplicates for multiple BB in the same frame. 
            BB_frame_list.append(BB_frame) 

### convert to df, pull unique index too
BB_df = pd.DataFrame(BB_rowinfo)
BB_df["BB_list"] = BB_concat_out
BB_df["BB_frame_list"] = BB_frame_list

# %% # ----------------------------------------------------------------
### Merging insect and bounding box info, sorting, write to file
### merge back with unpacked subject_ids df, using index as unique key
anns_parsed = pd.merge(parsing_df_melted, BB_df.drop(["subject_ids", "frame", "BB_frame_list"], axis=1), left_index=True, right_on="index", how='left')
anns_parsed = anns_parsed.drop(['BB_value', 'index'], axis=1) # drop now superfluous columns

### sort by subject_ids and focal_frame_id
focal_frames_dict = {'focal_frame_-2': 0, 'focal_frame_-1': 1, 'focal_frame_0': 2, 'focal_frame_1': 3, 'focal_frame_2': 4} # for custom sorting
anns_parsed['rank'] = anns_parsed['focal_frame_id'].map(focal_frames_dict) # apply custom sorting order in temp column
anns_parsed = anns_parsed.sort_values(['subject_ids', 'rank']) # sort by subject_ids nad temp column
anns_parsed = anns_parsed.drop('rank', axis=1) # drop temp column

### write to file
anns_parsed.to_csv(Path(workdir.parents[0] / "anns_parsed.csv"), sep=',', encoding='utf-8', index=False)

# %% # ----------------------------------------------------------------
### ANNOTATIONS SUMMARIZATION - ONLY UNCOMMENT IF SUMMARIZATION BY SUBJECT_IDS & FOCAL_FRAMES REQUIRED
### Summarising insect taxon, number and behaviour as well as BB info
anns_parsed_grouped = anns_parsed.groupby(["subject_ids", "focal_frame_id"]).agg({
    "taxon": lambda x: list(x.dropna()), # this list can contain strings
    "how_many": lambda x: x.dropna().astype(int).tolist(), # this list has to contain integers
    "behaviour": lambda x: list(x.dropna()), # this list can also contain strings
    "BB_list": lambda x: list(x.dropna()), # this list has to contain lists
    })

### remove empty lists and replace with NaN
for col in ['taxon', 'how_many', 'behaviour', 'BB_list']: 
    anns_parsed_grouped[col] = anns_parsed_grouped[col].apply(lambda y: np.nan if len(y)==0 else y)

### write to file
anns_parsed_grouped.to_csv(Path(workdir.parents[0] / "anns_parsed_grouped.csv"), sep=',', encoding='utf-8', index=True)

# %% 