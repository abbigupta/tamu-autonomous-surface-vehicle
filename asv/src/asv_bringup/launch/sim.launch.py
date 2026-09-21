"""Launch the ASV in a calm-water Gazebo Sim world."""

from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.actions import OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import xacro


def _simulation_nodes(context):
    description_share = Path(get_package_share_directory('asv_description'))
    model_file = description_share / 'urdf' / 'asv.urdf.xacro'
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
            parameters=[
                {'robot_description': description},
                {'use_sim_time': True},
            ],
        ),
        Node(
            package='ros_gz_sim',
            executable='create',
            name='spawn_asv',
            output='screen',
            parameters=[{
                'world': 'calm_water',
                'string': description,
                'name': 'asv',
                'allow_renaming': False,
                'x': 0.0,
                'y': 0.0,
                'z': 0.10,
                'R': 0.0,
                'P': 0.0,
                'Y': 0.0,
            }],
        ),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='simulation_bridge',
            output='screen',
            arguments=[
                '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
                '/model/asv/joint/port_thruster_joint/cmd_thrust'
                '@std_msgs/msg/Float64]gz.msgs.Double',
                '/model/asv/joint/starboard_thruster_joint/cmd_thrust'
                '@std_msgs/msg/Float64]gz.msgs.Double',
            ],
        ),
        Node(
            package='asv_control',
            executable='twin_thruster_controller',
            output='screen',
            parameters=[
                {'use_sim_time': True},
                {'max_forward_thrust_n': 25.0},
                {'max_reverse_thrust_n': 15.0},
                {'command_timeout_s': 0.75},
            ],
        ),
    ]


def generate_launch_description():
    description_share = Path(get_package_share_directory('asv_description'))
    ros_gz_share = Path(get_package_share_directory('ros_gz_sim'))
    world_file = description_share / 'worlds' / 'calm_water.sdf'

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            str(ros_gz_share / 'launch' / 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': [
                LaunchConfiguration('gz_args_extra'),
                f' -r -v 3 {world_file}',
            ],
            'on_exit_shutdown': 'true',
        }.items(),
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_mesh',
            default_value='false',
            description='Use a detailed visual mesh instead of preview shapes.',
        ),
        DeclareLaunchArgument(
            'mesh_file',
            default_value='asv_visual.obj',
            description='Filename under asv_description/meshes/visual.',
        ),
        DeclareLaunchArgument(
            'mesh_scale',
            default_value='0.001',
            description='Uniform STL scale; 0.001 converts millimetres to metres.',
        ),
        DeclareLaunchArgument('mesh_x', default_value='0.0'),
        DeclareLaunchArgument('mesh_y', default_value='0.0'),
        DeclareLaunchArgument('mesh_z', default_value='0.0'),
        DeclareLaunchArgument('mesh_roll', default_value='0.0'),
        DeclareLaunchArgument('mesh_pitch', default_value='0.0'),
        DeclareLaunchArgument('mesh_yaw', default_value='1.57079632679'),
        DeclareLaunchArgument(
            'gz_args_extra',
            default_value='',
            description='Additional Gazebo arguments, for example -s for server only.',
        ),
        gazebo,
        OpaqueFunction(function=_simulation_nodes),
    ])
