
s=part('back_cover')
r=param('display_hinge_pin_radius',1.1)
projection=param('display_hinge_pin_end_projection',0.5)
edge_r=param('display_hinge_pin_end_edge_radius',0.1)
length=s.hinge_span+2*projection
body=Cylinder(r,length,rotation=(90,0,0))
body=chamfer(body.edges().filter_by(GeomType.CIRCLE),length=edge_r)
assert len(body.solids())==1 and body.is_valid
assert s.pin_retention_r<r<s.lid_bore_r
fit('display_hinge_pin','back_cover',kind='press_fit',budget_mm=2*(r-s.pin_retention_r),reason='Headless straight pin is held by the TPU center fixed knuckle; moving lid bores remain clearance fits')
body.color=srgb('#303238')
print('Headless pin length and diameter',length,2*r,'projection each end',projection)
print('Center fixed bore / diametral interference',s.pin_retention_d,2*r-s.pin_retention_d)
publish('display_hinge_pin',body,'两端无帽直销',material='petg')
