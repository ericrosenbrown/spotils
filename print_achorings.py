import argparse
import grpc
import logging
import math
import os
import sys
import time

from bosdyn.api import geometry_pb2
from bosdyn.api import power_pb2
from bosdyn.api import robot_state_pb2
from bosdyn.api.graph_nav import graph_nav_pb2
from bosdyn.api.graph_nav import map_pb2
from bosdyn.api.graph_nav import nav_pb2
import bosdyn.client.channel
from bosdyn.client.power import safe_power_off, PowerClient, power_on
from bosdyn.client.exceptions import ResponseError
from bosdyn.client.graph_nav import GraphNavClient
from bosdyn.client.frame_helpers import get_odom_tform_body
from bosdyn.client.lease import LeaseClient, LeaseKeepAlive, LeaseWallet, ResourceAlreadyClaimedError
from bosdyn.client.math_helpers import Quat, SE3Pose
from bosdyn.client.robot_command import RobotCommandClient, RobotCommandBuilder
from bosdyn.client.robot_state import RobotStateClient
import bosdyn.client.util
import google.protobuf.timestamp_pb2


# For each waypoint in the graph's anchoring, prints the (x, y, z) position of that waypoint.
def print_anchorings(graph):
    for anchor in graph.anchoring.anchors:
        pos = anchor.seed_tform_waypoint.position
        print("id: {} x: {} y: {} z: {}".format(anchor.id, pos.x, pos.y, pos.z))

if __name__ == "__main__":
    argv = sys.argv[1:]

    parser = argparse.ArgumentParser(description=__doc__)
    bosdyn.client.util.add_base_arguments(parser)
    options = parser.parse_args(argv)

    # Setup and authenticate the robot.
    sdk = bosdyn.client.create_standard_sdk('GraphNavClient')
    robot = sdk.create_robot(options.hostname)
    bosdyn.client.util.authenticate(robot)

    graph_nav_client = robot.ensure_client(GraphNavClient.default_service_name)

     # Download current graph
    graph = graph_nav_client.download_graph()
    print_anchorings(graph)

