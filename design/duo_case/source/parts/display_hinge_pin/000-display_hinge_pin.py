s=part('back_cover')
r=param('display_hinge_pin_radius',1.1)
projection=param('display_hinge_pin_end_projection',0.5)
edge_r=param('display_hinge_pin_end_edge_radius',0.1)
length=s.hinge_station_width+2*projection
body=Cylinder(r,length,rotation=(90,0,0))
body=chamfer(body.edges().filter_by(GeomType.CIRCLE),length=edge_r)
assert len(body.solids())==1 and body.is_valid
assert 0<r<s.lid_bore_r
body.color=srgb('#303238')
print('Independent center pin length/diameter',length,2*r)
publish('display_hinge_pin',body,'中部无帽短销',material='petg')
