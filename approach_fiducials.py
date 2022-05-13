# Copyright (c) 2022 Boston Dynamics, Inc.  All rights reserved.
#
# Downloading, reproducing, distributing or otherwise using the SDK Software
# is subject to the terms and conditions of the Boston Dynamics Software
# Development Kit License (20191101-BDSDK-SL).

import argparse
from vtk.util import numpy_support
import google.protobuf.timestamp_pb2
import math
import numpy as np
import numpy.linalg
import os
import sys
import time
import vtk

from bosdyn.api.graph_nav import map_pb2
from bosdyn.api import geometry_pb2
from bosdyn.client.frame_helpers import *
from bosdyn.client.math_helpers import *
import bosdyn.client.util

from utils.graph_nav_helper import GraphNavInterface

def load_map(path):
    """
    Load a map from the given file path.
    :param path: Path to the root directory of the map.
    :return: the graph, waypoints, waypoint snapshots and edge snapshots.
    """
    with open(os.path.join(path, "graph"), "rb") as graph_file:
        # Load the graph file and deserialize it. The graph file is a protobuf containing only the waypoints and the
        # edges between them.
        data = graph_file.read()
        current_graph = map_pb2.Graph()
        current_graph.ParseFromString(data)

        # Set up maps from waypoint ID to waypoints, edges, snapshots, etc.
        current_waypoints = {}
        current_waypoint_snapshots = {}
        current_edge_snapshots = {}
        current_anchors = {}
        current_anchored_world_objects = {}

        # Load the anchored world objects first so we can look in each waypoint snapshot as we load it.
        for anchored_world_object in current_graph.anchoring.objects:
            current_anchored_world_objects[anchored_world_object.id] = (anchored_world_object,)
        # For each waypoint, load any snapshot associated with it.
        for waypoint in current_graph.waypoints:
            current_waypoints[waypoint.id] = waypoint

            if len(waypoint.snapshot_id) == 0:
                continue
            # Load the snapshot. Note that snapshots contain all of the raw data in a waypoint and may be large.
            file_name = os.path.join(path, "waypoint_snapshots", waypoint.snapshot_id)
            if not os.path.exists(file_name):
                continue
            with open(file_name, "rb") as snapshot_file:
                waypoint_snapshot = map_pb2.WaypointSnapshot()
                waypoint_snapshot.ParseFromString(snapshot_file.read())
                current_waypoint_snapshots[waypoint_snapshot.id] = waypoint_snapshot

                for fiducial in waypoint_snapshot.objects:
                    if not fiducial.HasField("apriltag_properties"):
                        continue

                    str_id = str(fiducial.apriltag_properties.tag_id)
                    if (str_id in current_anchored_world_objects and
                            len(current_anchored_world_objects[str_id]) == 1):

                        # Replace the placeholder tuple with a tuple of (wo, waypoint, fiducial).
                        anchored_wo = current_anchored_world_objects[str_id][0]
                        current_anchored_world_objects[str_id] = (anchored_wo, waypoint, fiducial)

        # Similarly, edges have snapshot data.
        for edge in current_graph.edges:
            if len(edge.snapshot_id) == 0:
                continue
            file_name = os.path.join(path, "edge_snapshots", edge.snapshot_id)
            if not os.path.exists(file_name):
                continue
            with open(file_name, "rb") as snapshot_file:
                edge_snapshot = map_pb2.EdgeSnapshot()
                edge_snapshot.ParseFromString(snapshot_file.read())
                current_edge_snapshots[edge_snapshot.id] = edge_snapshot
        for anchor in current_graph.anchoring.anchors:
            current_anchors[anchor.id] = anchor
        print("Loaded graph with {} waypoints, {} edges, {} anchors, and {} anchored world objects".
              format(len(current_graph.waypoints), len(current_graph.edges),
                     len(current_graph.anchoring.anchors), len(current_graph.anchoring.objects)))
        return (current_graph, current_waypoints, current_waypoint_snapshots,
                current_edge_snapshots, current_anchors, current_anchored_world_objects)

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--path', type=str, help='Map to draw.')
    parser.add_argument('--fiducial', type=str, help='Fiducial to approach')
    parser.add_argument('-a', '--anchoring', action='store_true',
                        help='Draw the map according to the anchoring (in seed frame).')
    bosdyn.client.util.add_base_arguments(parser)
    options = parser.parse_args(argv)

    ### Get approach pose for fiducial in seed frame
    # Load the map from the given file.
    (current_graph, current_waypoints, current_waypoint_snapshots, current_edge_snapshots,
     current_anchors, current_anchored_world_objects) = load_map(options.path)

    #### seed_tform_object gives pose of fiducial in seed frame, as protobug
    seed_tform_fiducial_pb = current_anchored_world_objects[options.fiducial][0].seed_tform_object
    
    #Turn protobuf SE3Pose into math SE3Pose
    seed_tform_fiducial = SE3Pose(x=seed_tform_fiducial_pb.position.x,
                            y=seed_tform_fiducial_pb.position.y,
                            z=seed_tform_fiducial_pb.position.z,
                            rot=seed_tform_fiducial_pb.rotation)

    #Construct SE3 pose relative to fiducial we want for approach
    fiducial_tform_approach = SE3Pose(x=0,
                            y=0,
                            z=1.5,
                            rot=Quat(w=1,x=0,y=0,z=0))
    
    seed_tfrom_approach = seed_tform_fiducial.mult(fiducial_tform_approach)
    print(seed_tfrom_approach)
    print(seed_tfrom_approach.rotation.to_yaw())

    ### Load nav stack and move to 
    sdk = bosdyn.client.create_standard_sdk('GraphNavClient')
    robot = sdk.create_robot(options.hostname)
    bosdyn.client.util.authenticate(robot)

    graph_nav_interface = GraphNavInterface(robot, options.path)

    #Upload map
    graph_nav_interface._upload_graph_and_snapshots()
    #Localize robot based on nearest fiducials
    graph_nav_interface._set_initial_localization_fiducial()
    #Navigate to approach pose!
    graph_nav_interface._navigate_to_anchor([seed_tfrom_approach.position.x, seed_tfrom_approach.position.y, seed_tfrom_approach.rotation.to_yaw()])

    #Give up lease
    graph_nav_interface._on_quit()
if __name__ == '__main__':
    main(sys.argv[1:])
