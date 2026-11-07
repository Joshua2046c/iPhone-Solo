# cell: camera_guard
# Custom ring. The camera protrusion is an explicit prototype assumption, not a vendor dimension.
w=param('camera_guard_inner_width',55.0)
h=param('camera_guard_inner_height',23.0)
wall=param('camera_guard_radial_width',2.0)
phone_z=param('camera_guard_phone_back_z',2.4)
back_plate=param('camera_guard_back_plate',3.4)
glue=param('camera_guard_glue_thickness',0.15)
cam_height=param('camera_guard_assumed_camera_protrusion',4.0)
margin=param('camera_guard_protection_margin',0.5)
inner_depth=param('camera_guard_inner_cavity_depth',3.9)
extension=max(0.0,inner_depth-back_plate)
# Model local bond face at Z0, with outward crest in -Z. Placement binds to the flush exterior back plane.
base_z=phone_z-back_plate-glue
crest_z=phone_z-cam_height-margin-extension
outer_raise=param('camera_guard_extra_outer_height',0.8)
crest_z-=outer_raise
thickness=base_z-crest_z
assert wall>0 and thickness>0 and margin>0
# Equal-radius symmetric ends, joined by parallel straight tangent segments.
# Match the symmetric shell aperture; end radii follow short-axis height.
assert w>h>0
rr=h/2
rl=rr
xr=w/2-rr
xl=-w/2+rl
nx=(rl-rr)/(xr-xl)
ny=(1-nx*nx)**0.5
tl=(xl+rl*nx,rl*ny)
tr=(xr+rr*nx,rr*ny)
glass=(Pos(xl,0)*Circle(rl)+Pos(xr,0)*Circle(rr)+
       Polygon(tl,(tl[0],-tl[1]),(tr[0],-tr[1]),tr,align=None))
# Glue-only stepped ring: half-width flange and raised locating sleeve, no retaining bead.
inward=param('camera_guard_collar_inward',1.0)
collar_h=param('camera_guard_collar_height',1.6)
assert 0<inward<h/2 and collar_h>0
inner=offset(glass,amount=-inward)
profile=offset(glass,amount=wall)-inner
body=extrude(profile,amount=-thickness)
collar=extrude(glass-inner,amount=collar_h)
body+=collar
ib=inner.bounding_box().size
assert abs(ib.X-(w-2*inward))<1e-6 and abs(ib.Y-(h-2*inward))<1e-6
assert abs(body.bounding_box().max.Z-collar_h)<1e-6
assert abs(body.bounding_box().min.Z+thickness)<1e-6
assert base_z+collar_h<phone_z
print('Collar inward extension',inward,'raised height',collar_h,'net opening',w-2*inward,h-2*inward)
print('Glue-only base band width',wall+inward,'outer flange',wall,'raised locator wall',inward,'locator top world Z',base_z+collar_h)

assert len(body.solids())==1
print('Ring axial thickness',thickness,'crest world Z',crest_z,'assumed lens Z',phone_z-cam_height)
publish('camera_guard',body,'05 镜头保护圈')