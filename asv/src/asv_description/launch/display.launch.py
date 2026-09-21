"""Display the ASV model in RViz through robot_state_publisher."""

from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import xacro


def _nodes(context):
    package_share = Path(get_package_share_directory('asv_description'))
    model_file = package_share / 'urdf' / 'asv.urdf.xacro'
    description = xacro.process_file(
        str(model_file),
        mappings={
            'use_mesh': LaunchConfiguration('use_mesh').perform(context),
            'mesh_file': LaunchConfiguration('mesh_file').perform(context),
            'mesh_scale': LaunchConfiguration('mesh_scale').perform(context),
            'mesh_x': LaunchConfiguration('mesh_x').perform(context),
            'mesh_y': LaunchConfiguration('mesh_y').perform(context),
            'mesh_z': LaunchConfiguration('mesh_z').perform(context),
            'mesh_roll': LaunchConfiguration('mesh_roll').perform(context),
            'mesh_pitch': LaunchConfiguration('mesh_pitch').perform(context),
            'mesh_yaw': LaunchConfiguration('mesh_yaw').perform(context),
        },
    ).toxml()

    return [
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': description}],
        ),
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('use_mesh', default_value='false'),
        DeclareLaunchArgument('mesh_file', default_value='asv_visual.obj'),
        DeclareLaunchArgument('mesh_scale', default_value='0.001'),
        DeclareLaunchArgument('mesh_x', default_value='0.0'),
        DeclareLaunchArgument('mesh_y', default_value='0.0'),
        DeclareLaunchArgument('mesh_z', default_value='0.0'),
        DeclareLaunchArgument('mesh_roll', default_value='0.0'),
        DeclareLaunchArgument('mesh_pitch', default_value='0.0'),
        DeclareLaunchArgument('mesh_yaw', default_value='1.57079632679'),
        OpaqueFunction(function=_nodes),
    ])
