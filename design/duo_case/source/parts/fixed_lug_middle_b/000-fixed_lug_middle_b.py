s=part('back_cover')
edge_r=param('fixed_lug_middle_b_free_edge_radius',0.3)
r=s.fixed_barrel_r
width=s.fixed_ear_width
left=s.fixed_lug_bond_left-s.lid_axis_x
right=s.fixed_lug_bond_right-s.lid_axis_x
bond_top=s.fixed_lug_bond_z-s.lid_axis_z
assert right>left and bond_top>r and width>=2.0
barrel=Cylinder(r,width,rotation=(90,0,0))
base=Pos((left+right)/2,0,bond_top/2)*Box(right-left,width,bond_top)
body=barrel+base
# The entire rectangular adhesive face stays flat; blend only free corners.
free_edges=[e for e in body.edges().filter_by(Axis.Y) if e.center().Z<bond_top-1e-6]
body=fillet(free_edges,radius=edge_r)
body-=Cylinder(s.lid_bore_r,width+2,rotation=(90,0,0)).rotate(Axis.Y,45)
body=body.clean()
assert body.is_valid and len(body.solids())==1
bond_faces=[f for f in body.faces() if abs(f.bounding_box().min.Z-bond_top)<1e-6 and abs(f.bounding_box().max.Z-bond_top)<1e-6]
assert len(bond_faces)==1 and abs(bond_faces[0].area-(right-left)*width)<1e-6
body.color=srgb('#d5223e')
print('Flat adhesive foot',right-left,width,'area',bond_faces[0].area,'gap',s.fixed_lug_glue_gap)
publish('fixed_lug_middle_b',body,'独立胶粘轴耳 4',material='petg')
