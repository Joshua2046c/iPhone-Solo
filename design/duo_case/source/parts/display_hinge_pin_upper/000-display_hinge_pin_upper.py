s=part('back_cover')
p=part('display_hinge_pin')
r=param('display_hinge_pin_upper_radius',1.1)
length=s.hinge_station_width+2*p.projection
body=Cylinder(r,length,rotation=(90,0,0))
body=chamfer(body.edges().filter_by(GeomType.CIRCLE),length=p.edge_r)
assert body.is_valid and len(body.solids())==1 and 0<r<s.lid_bore_r
body.color=srgb('#303238')
publish('display_hinge_pin_upper',body,'上部无帽短销',material='petg')
