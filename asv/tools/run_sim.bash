#!/usr/bin/env bash
set -eo pipefail

# The Snap build of VS Code exports GTK / GLib paths from Ubuntu core20.
# Gazebo is a host application and must not load those incompatible libraries.
unset SNAP SNAP_ARCH SNAP_COMMON SNAP_CONTEXT SNAP_COOKIE SNAP_DATA
unset SNAP_EUID SNAP_INSTANCE_NAME SNAP_LIBRARY_PATH SNAP_NAME SNAP_REAL_HOME
unset SNAP_REVISION SNAP_UID SNAP_USER_COMMON SNAP_USER_DATA SNAP_VERSION
unset GDK_PIXBUF_MODULEDIR GDK_PIXBUF_MODULE_FILE GIO_MODULE_DIR
unset GSETTINGS_SCHEMA_DIR GTK_EXE_PREFIX GTK_IM_MODULE_FILE GTK_PATH LOCPATH

if [[ -n "${XDG_DATA_DIRS_VSCODE_SNAP_ORIG:-}" ]]; then
  export XDG_DATA_DIRS="${XDG_DATA_DIRS_VSCODE_SNAP_ORIG}"
fi
if [[ -n "${XDG_CONFIG_DIRS_VSCODE_SNAP_ORIG:-}" ]]; then
  export XDG_CONFIG_DIRS="${XDG_CONFIG_DIRS_VSCODE_SNAP_ORIG}"
fi

workspace_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

source /opt/ros/lyrical/setup.bash
source "${workspace_dir}/install/setup.bash"

exec ros2 launch asv_bringup sim.launch.py use_mesh:=true "$@"
