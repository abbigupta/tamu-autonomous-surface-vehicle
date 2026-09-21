# Visual mesh drop directory

For a colored model, place the combined Fusion 360 assembly files here with
the exact filenames:

- `asv_visual.obj`
- `asv_visual.mtl`

The OBJ must contain `mtllib asv_visual.mtl`.

The starter launch command is:

```bash
ros2 launch asv_bringup sim.launch.py use_mesh:=true
```

The default assumes the mesh coordinates are millimetres. Use
`mesh_scale:=1.0` if the mesh is already in metres.

Do not use the detailed assembly mesh as collision geometry. Collision and
buoyancy use the simplified pontoon shapes in `urdf/asv.urdf.xacro`.
