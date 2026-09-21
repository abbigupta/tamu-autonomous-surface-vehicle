# fusion2URDF export staging area

Use this directory as a temporary landing area for exports made from Fusion
360. A current fusion2URDF exporter creates a complete ROS 2 description
package containing its own `package.xml`, `CMakeLists.txt`, URDF/Xacro files,
meshes, and launch files.

After checking the export, move the complete generated package directory into:

`/home/abbi/ros_projects/asv/src/`

Do not copy a generated package into `src/asv_description`; nested ROS packages
are not supported.

For the simpler rigid-model workflow, export one combined assembly STL and put
it at:

`src/asv_description/meshes/visual/asv_visual.stl`
