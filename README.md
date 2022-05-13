This is a repository of utilities for Spot, mainly relying on the Spot SDK. For some of the examples in this repo, we use the python examples included in the Spot SDK, so for reference where to look for files, we will assume your path to spot-sdk is located at <SPOT_SDK_DIR>.

### RECORD MAP ###
### Weblink: https://dev.bostondynamics.com/python/examples/graph_nav_command_line/readme
- The python file is located in: <SPOT_SDK_DIR>/python/examples/graph_nav_command_line
	```
	python3 -m recording_command_line --download-filepath <MAP_DIR> <ROBOT_IP>
	```
- This will download the map to <MAP_DIR>
1) '1' for start recording map
2) walk robot around (using tabley)
(OPTIONAL):
	- '9' for automatic loop closure, '0' to automatically close all loops
	- 'a' for anchoring optimization (This constructs a metric-consistent map and defines a seed frame that acts as global map frame, needed for certain scripts below)
3) '2' to stop map recording
4) '5' to download map
5) 'q' to quit

### VIEW MAP ###
### Weblink: https://dev.bostondynamics.com/python/examples/graph_nav_view_map/readme
- The python file is located in: <SPOT_SDK_DIR>/python/examples/graph_nav_view_map
```
python3 -m view_map <MAP_DIR>/downloaded_graph
```
### NAVIGATION MAP ###
### Weblink: https://dev.bostondynamics.com/python/examples/graph_nav_command_line/readme
- The python file is located in: <SPOT_SDK_DIR>/python/examples/graph_nav_command_line
```
python3 -m graph_nav_command_line --upload-filepath <MAP_DIR>/downloaded_graph/ <ROBOT_IP> 
```
1) '5' to upload map
2) '2' to localize w.r.t nearest fiducial
(OPTIONAL):
	- '1' to get localized state (look at seed_tform_body for pose in seed frame)
3) '8' to navigate to anchor pose in seed frame

### APPROACH FIDUCIAL ###
First, build a map of the environment following the instructions before (make sure to do anchor optimization) and make sure the fiducial is within view during mapping. Then, run the following command, with --path pointing to your downloaded map, --fiducial being the number of the fiducial you want, and <ROBOT_IP> being hostname of the robot. When you run this code, the robot will automatically navigate to an approach pose facing the fiducial. Note that the fiducial does not need to be in view of the robot.
```
python approach_fiducials.py --path <MAP_DIR>/downloaded_graph/ --fiducial <FIDUCIAL_NUMBER> <ROBOT_IP>
```

### OPEN DRAWER ###
(Experimental code, will update this later)
```
python3 open_drawer.py 138.16.161.12 --force-horizontal-grasp --image-source hand_color_image --task-type drawer --task-velocity -0.5 --force-limit 40
```