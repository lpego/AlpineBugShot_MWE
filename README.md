# AlpineBugShot_MWE
This is a Minimum Working Example for the Zooniverse project [Alpine Bug Shot](https://www.zooniverse.org/projects/lucapego/alpine-bug-shot) annotations parsing, trying to figure out problems with Bounding Boxes (BBs) localization on the original images. 

For full project description, please see the private repo on Renku's instance of GitLab. 

Repo infos
==========
Data
----
 - `/anns_parsed.csv` contains the annotations, parsed according to `scripts/zooniverse_annotations_parsing.py`, grouped by annotator (i.e. one user's BBs per row); 
 - `anns_parsed_onlypos.csv` is the same as `/anns_parsed.csv` but only contains rows with BBs; 
 - `/anns_parsed_grouped.csv` contains the annotations grouped by subject and focal_frame (i.e. multiple users' BBs per row). 

 - `data/anns_MWE.csv` is a small subset of the original annotation file, as downloaded from Zooniverse; 
  - `data/subj_MWE.csv` is the subject data from Zooniverse
  - `data/wrkfl_MWE.csv` is the full workflow files from Zooniverse

  - The folder `data/frames` contains only the frames pertaining to the subjects; contained in `data/anns_MWE.csv`, as pulled from all the frames for all the subjects.
  - The folder `data/frames/examples`  contains examples of visualization from a previous version of the visualization script. 

Scripts
-------
 - `scripts/MWE_prepare.py` is used to pull a representative subset of annotations and subjects from the respective full files, and to find and copy (only) the corresponding frames (_note:_ must have already frames extracted as images)
 - `scripts/zooniverse_annotations_parsing.py` is the original script that processes annotations into a usable format; it takes `data/anns_MWE.csv` as input and returns `/anns_parsed.csv` as output. 
 - `scripts/visualize_bb.py` is a re-implementation of the original script to visualize BBs on images, using matplotlib and not opencv. 

A `conda` environment file is provided in `/environment.yml`

Processing BBs data
===================
panoptes_aggregation
--------------------
When trying to use built-in functions in [panotpes_aggregation](https://aggregation-caesar.zooniverse.org/index.html) to extract BBs, I encountered several problems: 

 - there seems to be whitespace in the column names of the example data that doesn't get stripped.
    - _fix:_ TBC...
 - further errors up the function chain get harder to decipher...
_Bug report TBC..._

I can replicate this bug using a local installation of panoptes (via `conda`, see included `environment.yml` file), but also with Docker (Docker compose method), as specified in [panoptes's docs](https://aggregation-caesar.zooniverse.org/README.html#installing-for-offline-use). 

Custom parsing / visualization scripts
--------------------------------------
_Details TBC..._ 

The main issue seemed to be that `scripts/zooniverse_annotations_parsing.py` parses BB info into `[x1, y1, x2, y2]` format, but the original visualization script expects `[x1, y1, width, height]`... 

Furthermore, `/anns_parsed_grouped.csv` has BB info encoded as a nested list with three levels: 
```
[all user's annotations
    [single user's annotations
        [single BB coordinates]
    ]
]
```
This is because each user could have drawn multiple BBs per frame, and we aggregate multiple users' annotations for each frame. 
Re-implementation of visualization takes account of that, and parses separately (with different colours) the BBs of each user. 
This also makes it easier to clean / evaluate annotations down the line. 