alias: spot_venv

### RECORD MAP ###
### Weblink: https://dev.bostondynamics.com/python/examples/graph_nav_command_line/readme
python3 -m recording_command_line --download-filepath /home/eric/maps/<MAP_DIR> <ROBOT_IP>
1) '1' for start recording map
2) walk robot around
(OPTIONAL):
	- '8' for edge from start to end manually (if end at start place)
	- '9' for automatic loop closure
	- 'a' for anchoring optimization
3) '2' to stop map recording
4) '5' to download map
5) 'q' to quit

### VIEW MAP ###
### Weblink: https://dev.bostondynamics.com/python/examples/graph_nav_view_map/readme
python3 -m view_map /home/eric/maps/<MAP_DIR>/downloaded_graph

### NAVIGATION MAP ###
python3 -m graph_nav_command_line --upload-filepath /home/eric/maps/new_cit121/downloaded_graph/ 138.16.161.2 --user user --password dungnydsc8su
1) '5' to upload map
2) '2' to localize w.r.t nearest fiducial
(OPTIONAL):
	- '1' to get localized state (look at seed_tform_body for pose in seed frame)
3) '8' to navigate to anchor pose in seed frame

