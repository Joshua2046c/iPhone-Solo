# Fixed-open one-piece tray. Camera-side datum and original access geometry are retained.
phone_w=param('back_cover_open_phone_width',164.6)
phone_h=param('back_cover_open_phone_height',117.8)
phone_t=param('back_cover_open_phone_thickness',5.2)
right_x=param('back_cover_right_datum_x',43.9)
liner_t=param('back_cover_liner_thickness',0.2)
wall_h=param('back_cover_wall_height',6.28)+liner_t
clearance=param('back_cover_fit_clearance',0.25)
inner_wall_inset=param('back_cover_inner_wall_inset',0.045)
short_edge_inset=param('back_cover_short_edge_inner_thickening',0.055)
wall=param('back_cover_wall',1.6)
plate=param('back_cover_plate',2.5)
seat_z=param('back_cover_phone_seat_z',2.4)
phone_seat_z=seat_z+liner_t
radius=param('back_cover_corner_radius',12)
lip=param('back_cover_corner_inward',0.7)
lip_h=param('back_cover_lip_height',0.7)
outer_round=param('back_cover_outer_rim_radius',0.8)
opening_soft=param('back_cover_opening_edge_radius',0.3)
turn=param('back_cover_opening_turn_radius',1)
cam_w=param('back_cover_camera_width',58.3)
cam_h=param('back_cover_camera_height',22.5)
cam_x=param('back_cover_camera_x',10)
cam_y=param('back_cover_camera_y',43.9)
cam_inner_expand=param('back_cover_camera_inner_expansion',4)
cam_inner_depth=param('back_cover_camera_inner_depth',3.9)
land_h=param('back_cover_camera_vertical_land_height',0.3)
power_y=param('back_cover_power_y',16.1)
power_l=param('back_cover_power_opening',24.8)
shutter_y=param('back_cover_shutter_y',-27)
shutter_l=param('back_cover_shutter_opening',23)
corner_lip_relief=param('back_cover_corner_lip_relief',0.1)
wi,hi=phone_w+2*clearance,phone_h+2*clearance
wo,ho=wi+2*wall,hi+2*wall
shift=right_x-wo/2
edge_x=shift-wo/2
# Keep original right endpoints, mirror their left endpoints about the full-body center.
top_open_right=param('back_cover_top_opening_right_end_x',24)
bottom_open_right=param('back_cover_bottom_opening_right_end_x',26.9)
vol_x=shift
vol_w=2*(top_open_right-shift)-2*turn
bottom_x=shift
bottom_w=2*(bottom_open_right-shift)-2*turn
outside_z=seat_z-plate
outer=Pos(shift,0)*RectangleRounded(wo,ho,radius+wall)
inner=Pos(shift,0)*RectangleRounded(wi-2*short_edge_inset,hi,radius)
inner=offset(inner,amount=-inner_wall_inset)
assert clearance>inner_wall_inset+short_edge_inset and 0<lip<wall and radius>lip
corner_lip_radius=radius-lip-corner_lip_relief/(2**0.5-1)
lip_inner=Pos(shift,0)*RectangleRounded(wi-2*lip-2*short_edge_inset,hi-2*lip,corner_lip_radius)
lip_inner=offset(lip_inner,amount=-inner_wall_inset)
# One uninterrupted back plate spans both phone halves: no joint, pivot, groove or magnet seat.
floor_with_carrier=Pos(0,0,outside_z)*extrude(outer,amount=plate)
bottom_edges=[e for e in floor_with_carrier.edges() if abs(e.bounding_box().min.Z-outside_z)<1e-6 and abs(e.bounding_box().max.Z-outside_z)<1e-6]
assert len(bottom_edges)==8
floor_with_carrier=fillet(bottom_edges,radius=outer_round)
ring=extrude(outer,amount=wall_h)-extrude(inner,amount=wall_h)
ledge=extrude(outer,amount=lip_h)-extrude(lip_inner,amount=lip_h)
ring+=Pos(0,0,wall_h-lip_h)*ledge
# Four existing camera-half openings; new left perimeter is continuous.
ring-=Pos(vol_x,ho/2,wall_h/2)*Box(vol_w+2*turn,2*wall+2,wall_h+2)
ring=Compound(children=ring.solids())
ring-=Pos(right_x,power_y,wall_h/2)*Box(2*wall+2,power_l+2*turn,wall_h+2)
ring=Compound(children=ring.solids())
ring-=Pos(right_x,shutter_y,wall_h/2)*Box(2*wall+2,shutter_l+2*turn,wall_h+2)
ring=Compound(children=ring.solids())
ring-=Pos(bottom_x,-ho/2,wall_h/2)*Box(bottom_w+2*turn,2*wall+2,wall_h+2)
ring=Compound(children=ring.solids())
body=Pos(0,0,outside_z)*extrude(outer,amount=plate)
body+=Pos(0,0,seat_z)*ring
# Equal-radius ends and parallel common tangents give the requested symmetric capsule.
# Symmetric end radii are derived from short-axis height, not independent dimensions.
assert cam_w>cam_h>0
rr=cam_h/2
rl=rr
xr=cam_w/2-rr
xl=-cam_w/2+rl
nx=(rl-rr)/(xr-xl)
ny=(1-nx*nx)**0.5
tl=(xl+rl*nx,rl*ny)
tr=(xr+rr*nx,rr*ny)
glass=(Pos(xl,0)*Circle(rl)+Pos(xr,0)*Circle(rr)+
       Polygon(tl,(tl[0],-tl[1]),(tr[0],-tr[1]),tr,align=None))

# Flat exterior mouth; +4 mm inner relief. The clearance cutter reaches 3.9 mm from the phone seat.
camera_mouth_z=seat_z-cam_inner_depth
# No external raised pad or recessed ring seat: the camera surround stays on outside_z.
assert 0<land_h<plate
u0=land_h/plate
def flare_amount(u):
 return cam_inner_expand*(6*u**5-15*u**4+10*u**3)
def camera_profile(amount):
 lt=(xl+(rl+amount)*nx,(rl+amount)*ny)
 rt=(xr+(rr+amount)*nx,(rr+amount)*ny)
 return (Pos(xl,0)*Circle(rl+amount)+Pos(xr,0)*Circle(rr+amount)+
         Polygon(lt,(lt[0],-lt[1]),(rt[0],-rt[1]),rt,align=None))
land_expand=flare_amount(u0)
land_profile=camera_profile(land_expand)
sections=[]
for v in (0.0,0.1,0.25,0.5,0.75,0.9,1.0):
 u=u0+(1-u0)*v
 sk=camera_profile(flare_amount(u))
 assert len(sk.faces())==1 and len(sk.wires())==1, 'Camera station must be one closed profile'
 sections.append((Pos(cam_x,cam_y,outside_z+u*plate)*sk).faces()[0])
funnel=loft(sections,ruled=False)
# The outward offset matches the old flare at the top of the specified vertical land.
# Extend its straight cutter through free air, overlapping only inside the upper cutter.
funnel+=Pos(cam_x,cam_y,camera_mouth_z)*extrude(land_profile,amount=outside_z+land_h-camera_mouth_z+0.01)
fb=funnel.bounding_box()
assert abs(fb.min.Z-camera_mouth_z)<1e-5 and abs(fb.max.Z-seat_z)<1e-5, 'Camera funnel depth differs from 3.9 mm'
ib=offset(glass,amount=cam_inner_expand).bounding_box().size
gb=glass.bounding_box().size
assert abs(ib.X-gb.X-2*cam_inner_expand)<1e-5 and abs(ib.Y-gb.Y-2*cam_inner_expand)<1e-5, 'Inside opening offset differs from 4 mm'
# Apply this cutter after the adjacent button rim has been blended.
# The enlarged relief stops at the phone seat: extending it upward cut a notch in the perimeter rim.
# The existing 3.9 mm clearance-cut envelope extends outside the 3.4 mm back plate.
assert abs((seat_z-camera_mouth_z)-cam_inner_depth)<1e-7

# Profile blends are independent of the small through-thickness edge roll.
# Widen by one turn radius at each end so the original rectangular access remains clear.
eps=1e-5
openings=(
 ('y',ho/2,hi/2-inner_wall_inset,vol_x-vol_w/2-turn,vol_x+vol_w/2+turn),
 ('y',-ho/2,-hi/2+inner_wall_inset,bottom_x-bottom_w/2-turn,bottom_x+bottom_w/2+turn),
 ('x',shift+wo/2,shift+wi/2-inner_wall_inset-short_edge_inset,power_y-power_l/2-turn,power_y+power_l/2+turn),
 ('x',shift+wo/2,shift+wi/2-inner_wall_inset-short_edge_inset,shutter_y-shutter_l/2-turn,shutter_y+shutter_l/2+turn))
turn_edges=[]
for axis,outer_side,inner_side,lo,upper in openings:
 chosen=[]
 for e in body.edges():
  if e.geom_type!=GeomType.LINE:
   continue
  bb=e.bounding_box()
  amin,amax=(bb.min.X,bb.max.X) if axis=='x' else (bb.min.Y,bb.max.Y)
  bmin,bmax=(bb.min.Y,bb.max.Y) if axis=='x' else (bb.min.X,bb.max.X)
  at_end=(abs(bmin-lo)<eps and abs(bmax-lo)<eps) or (abs(bmin-upper)<eps and abs(bmax-upper)<eps)
  level=abs(bb.max.Z-bb.min.Z)<eps and (abs(bb.min.Z-seat_z)<eps or abs(bb.min.Z-seat_z-wall_h)<eps)
  through_wall=amin>=min(outer_side,inner_side)-lip-eps and amax<=max(outer_side,inner_side)+lip+eps and amax-amin>eps
  if at_end and level and through_wall:
   chosen.append(e)
 assert len(chosen)==4, 'Expected two lower and two upper profile corners'
 turn_edges.extend(chosen)
body=fillet(turn_edges,radius=turn)

# Keep only the finished access wall above the plate, then merge it with the continuous rounded base.
finished_wall=body&Pos(shift,0,seat_z+wall_h/2)*Box(wo+2,ho+2,wall_h)
body=floor_with_carrier+finished_wall

# Constant-angle finger ramp and tangent lower corner are one opening profile.
ramp_angle=param('back_cover_button_ramp_angle',20)
from math import tan, radians
ramp_slope=tan(radians(ramp_angle))
ramp_specs=[
 ('power','x',shift+wi/2-inner_wall_inset-short_edge_inset,shift+wo/2,power_y,power_l),
 ('shutter','x',shift+wi/2-inner_wall_inset-short_edge_inset,shift+wo/2,shutter_y,shutter_l),
 ('volume','y',hi/2-inner_wall_inset,ho/2,vol_x,vol_w)]
ramp_depth=(wall+inner_wall_inset+short_edge_inset)*ramp_slope
assert 0<ramp_angle<30
ramp_cutters=[]
for axis,outer_side,inner_side,lo,upper in openings:
 a=min(inner_side,outer_side)-lip-0.5
 c=max(inner_side,outer_side)+lip+0.5
 local_slope=ramp_slope if outer_side>0 else -ramp_slope
 def tangent_opening_station(at):
  floor_z=seat_z-(at-inner_side)*local_slope
  # The top remains above the perimeter even after oblique extrusion.
  top_z=seat_z+wall_h+2+(c-a)*abs(local_slope)
  cross=Pos((lo+upper)/2,(floor_z+top_z)/2)*Rectangle(upper-lo,top_z-floor_z)
  lower_vertices=[v for v in cross.vertices() if abs(v.Y-floor_z)<eps]
  assert len(lower_vertices)==2
  cross=fillet(lower_vertices,radius=turn)
  if axis=='x':
   return (Pos(at,0,0)*(Plane.YZ*cross)).faces()[0]
  return (Pos(0,at,0)*(Plane.XZ*cross)).faces()[0]
 direction=(1,0,-local_slope) if axis=='x' else (0,1,-local_slope)
 distance=(c-a)*(1+local_slope**2)**0.5
 ramp_cutters.append(extrude(tangent_opening_station(a),amount=distance,dir=direction))
body-=ramp_cutters
assert len(body.solids())==1
print('Tangent lower corners',turn,'constant ramp angle',ramp_angle,'virtual outer drop',ramp_depth)

# Round the complete access rim after cutting the ramps, before camera relief trims it.
# This shares the existing R0.3 parameter with the original opening edges.
opening_edges=[]
ramp_opening_edge_counts=[]
for axis,outer_side,inner_side,lo,upper in openings:
 chosen=[]
 for e in body.edges():
  bb=e.bounding_box()
  amin,amax=(bb.min.X,bb.max.X) if axis=='x' else (bb.min.Y,bb.max.Y)
  bmin,bmax=(bb.min.Y,bb.max.Y) if axis=='x' else (bb.min.X,bb.max.X)
  on_outer=abs(amin-outer_side)<eps and abs(amax-outer_side)<eps
  in_span=bmin>=lo-turn-eps and bmax<=upper+turn+eps
  above_floor=bb.min.Z>=seat_z-ramp_depth-eps
  if on_outer and in_span and above_floor:
   chosen.append(e)
 assert len(chosen)>=6, 'Incomplete access rim including its tangent lower corners'
 ramp_opening_edge_counts.append(len(chosen))
 opening_edges.extend(chosen)
body=fillet(opening_edges,radius=opening_soft)
assert body.is_valid and len(body.solids())==1
print('Shared access edge radius',opening_soft,'rim segment counts',ramp_opening_edge_counts)
for axis,outer_side,inner_side,lo,upper in openings:
 center=(lo+upper)/2
 span=upper-lo-2*turn
 if axis=='x':
  access=Pos(outer_side,center,seat_z+wall_h/2)*Box(2*wall+2,span,wall_h)
 else:
  access=Pos(center,outer_side,seat_z+wall_h/2)*Box(span,2*wall+2,wall_h)
 assert (body&access).volume<1e-6, 'Original rectangular button passage obstructed'

# Cut the camera relief after blending the button rim: the expanded relief trims the blend locally.
body-=funnel
body-=Pos(cam_x,cam_y,camera_mouth_z-0.1)*extrude(land_profile,amount=0.15)

# Internal MagSafe seats measured from the user-supplied back-cover STEP.
# The specified 1.15 mm is the backing between pocket floors and exterior back.
mag_id=param('back_cover_magsafe_inner_diameter',45)
mag_od=param('back_cover_magsafe_outer_diameter',54.72)
mag_x=param('back_cover_magsafe_x',2.05)
mag_y=param('back_cover_magsafe_y',-2.41)
mag_back_skin=param('back_cover_magsafe_back_skin',1.15)
mag_tail_l=param('back_cover_magsafe_tail_length',16.98)
mag_tail_w=param('back_cover_magsafe_tail_width',6.99)
mag_tail_gap=param('back_cover_magsafe_tail_gap',1.9)
assert 0<mag_id<mag_od and 0<mag_back_skin<plate
mag_depth=plate-mag_back_skin
mag_floor=outside_z+mag_back_skin
mag_profile=Pos(mag_x,mag_y)*(Circle(mag_od/2)-Circle(mag_id/2))
mag_tail_y=mag_y-mag_od/2-mag_tail_gap-mag_tail_l/2
mag_tail_profile=Pos(mag_x,mag_tail_y)*SlotOverall(mag_tail_l,mag_tail_w,rotation=90)
mag_disk=Pos(mag_x,mag_y)*Circle(mag_od/2)
mag_camera_gap=mag_disk.distance_to(Pos(cam_x,cam_y)*offset(glass,amount=cam_inner_expand))
assert mag_camera_gap>0
for profile in (mag_profile,mag_tail_profile):
 cutter=Pos(0,0,mag_floor)*extrude(profile,amount=mag_depth+0.05)
 assert abs((body&cutter).volume-profile.area*mag_depth)<1e-5, 'MagSafe seat intersects an existing opening'
 body-=cutter
# Both seats leave continuous exterior backing.
for profile in (mag_profile,mag_tail_profile):
 skin=Pos(0,0,outside_z)*extrude(profile,amount=mag_back_skin)
 assert abs((body&skin).volume-skin.volume)<1e-5, 'MagSafe exterior skin is not continuous'
print('MagSafe ID/OD, center, pocket depth, exterior skin',mag_id,mag_od,(mag_x,mag_y),mag_depth,mag_back_skin)
print('Tail length/width/center, ring-tail gap, camera gap',mag_tail_l,mag_tail_w,(mag_x,mag_tail_y),mag_tail_gap,mag_camera_gap)




# Keep the former display's inner recess while sealing its outer back face.
window_w=param('back_cover_display_clear_width',75.8)
window_h=param('back_cover_display_clear_height',113.6)
window_r=param('back_cover_display_corner_radius',10.5)
window_x=shift-phone_w/4
stop_land=param('back_cover_lid_stop_land',0.8)
mouth_w=window_w+2*stop_land
mouth_h=window_h+2*stop_land
mouth_r=window_r+stop_land
window_left=window_x-mouth_w/2
window_right=window_x+mouth_w/2
mouth=Pos(window_x,0)*(RectangleRounded(mouth_w,mouth_h,mouth_r)+Pos(mouth_w/4,0)*Rectangle(mouth_w/2,mouth_h))
# Keep the three 1.2 mm margins and the existing right screen-recess datum.
recess_side_land=param('back_cover_display_recess_side_land',1.2)
recess_right=window_x+window_w/2
recess_inside=offset(inner,amount=-recess_side_land)
recess_right_mask=Pos(recess_right-(wo+20)/2,0)*Rectangle(wo+20,ho+20)
clear_window=recess_inside&recess_right_mask
assert len(clear_window.faces())==1

recess_depth=param('back_cover_display_recess_depth',0.9)
recess_floor=seat_z-recess_depth
assert 0<recess_depth<plate and plate-recess_depth>=1.2
body-=Pos(0,0,recess_floor)*extrude(clear_window,amount=recess_depth+0.05)
# This is a blind pocket: the single exterior face stays continuous.
sealed_floor=Pos(0,0,outside_z)*extrude(clear_window,amount=plate-recess_depth)
assert abs((body&sealed_floor).volume-sealed_floor.volume)<1e-5
# The former liner thickness is now integral shell material on every planar seat.
# Selecting the complete existing Z=seat_z support faces also fills the left-side bands,
# while omitting the screen recess, camera aperture and open magnetic pockets.
compensation_faces=[f for f in body.faces()
 if f.geom_type==GeomType.PLANE
 and abs(f.bounding_box().min.Z-seat_z)<1e-6
 and abs(f.bounding_box().max.Z-seat_z)<1e-6
 and f.normal_at().Z>0.99]
assert len(compensation_faces)>0
integral_compensation=extrude(compensation_faces,amount=liner_t)
body+=integral_compensation
compensated_seat_z=seat_z+liner_t
compensated_recess_depth=compensated_seat_z-recess_floor
compensated_mag_depth=compensated_seat_z-mag_floor
print('Integral compensation thickness, final seat, recess and MagSafe depths',liner_t,compensated_seat_z,compensated_recess_depth,compensated_mag_depth)

# Remove only the straight inner return on the marked left short edge.
release_half_h=ho/2-(radius+wall)
lip_clear=Pos(edge_x+wall+inner_wall_inset+short_edge_inset+lip,0,seat_z+wall_h-lip_h/2)*Box(2*lip,2*release_half_h,lip_h+0.02)
body-=lip_clear
# Match the left retaining lip exactly to the existing right central lip.
center_lip_root_bond=param('back_cover_center_retention_root_bond',0.4)
right_lip_lo=shutter_y+shutter_l/2+turn
right_lip_hi=power_y-power_l/2-turn
center_lip_length=right_lip_hi-right_lip_lo
center_lip_y=(right_lip_hi+right_lip_lo)/2
right_inner=shift+wi/2-inner_wall_inset-short_edge_inset
right_lip_roi=Pos(right_inner+(center_lip_root_bond-lip)/2,center_lip_y,seat_z+wall_h-lip_h/2)*Box(lip+center_lip_root_bond,center_lip_length,lip_h)
right_lip_reference=body&right_lip_roi
assert right_lip_reference.is_valid and len(right_lip_reference.solids())==1
center_lip=mirror(right_lip_reference,about=Plane.YZ.offset(shift))
assert abs(center_lip.volume-right_lip_reference.volume)<1e-6
body+=center_lip

# Four rounded grip grooves are centered over the complete case-side thickness.
grip_depth=param('back_cover_grip_groove_depth',0.15)
grip_height=param('back_cover_grip_groove_height',0.6)
grip_pitch=param('back_cover_grip_groove_pitch',1.2)
grip_count=param('back_cover_grip_groove_count',4)
grip_center_z=(outside_z+seat_z+wall_h)/2
grip_first_z=grip_center_z-(grip_count-1)*grip_pitch/2
assert int(grip_count)==grip_count and grip_depth<wall-1.2
groove_ring=offset(outer,amount=grip_height)-offset(outer,amount=-grip_depth)
groove_tool=extrude(groove_ring,amount=grip_height)
groove_edges=[e for e in groove_tool.edges() if e.bounding_box().size.Z<1e-6]
groove_round=min(grip_height/4,grip_depth/2)
groove_tool=fillet(groove_edges,radius=groove_round)
# Four shallow grooves continue around the perimeter.
for i in range(int(grip_count)):
 band=Pos(0,0,grip_first_z+i*grip_pitch-grip_height/2)*groove_tool
 body-=band

# The sealed version is a continuous fixed-open phone tray.
bridge_probe=Pos(shift+4.0,0,outside_z+plate/2)*Box(2*wall,hi-2*radius,plate)
assert abs((body&bridge_probe).volume-bridge_probe.volume)<1e-5
# Open-top access notch on the lower edge, centered on the left phone half.
bottom_port_width=param('back_cover_bottom_left_notch_width',12.7)
bottom_port_inward=param('back_cover_bottom_left_notch_inward',3.4)
bottom_port_backing=param('back_cover_bottom_left_notch_backing',1.5)
bottom_port_corner=param('back_cover_bottom_left_notch_corner',0.3)
bottom_port_x=shift-phone_w/4
bottom_port_y=-ho/2
bottom_port_floor=outside_z+bottom_port_backing
bottom_port_inner_y=bottom_port_y+bottom_port_inward
port_entry_overrun=1.0
port_outline=Pos(bottom_port_x,bottom_port_y+(bottom_port_inward-port_entry_overrun)/2)*Rectangle(bottom_port_width,bottom_port_inward+port_entry_overrun)
port_inner_corners=[v for v in port_outline.vertices() if abs(v.Y-bottom_port_inner_y)<1e-6]
assert len(port_inner_corners)==2
port_outline=fillet(port_inner_corners,radius=bottom_port_corner)
bottom_port_cutter=Pos(0,0,bottom_port_floor)*extrude(port_outline,amount=seat_z+wall_h+2-bottom_port_floor)
body-=bottom_port_cutter
print('Bottom left notch width/inward/backing',bottom_port_width,bottom_port_inward,bottom_port_backing,'center X',bottom_port_x,'inner Y',bottom_port_inner_y,'floor Z',bottom_port_floor)
# Access recesses with large tangent reverse-arc transitions at all six ends.
edge_recess_inset=param('back_cover_edge_recess_inset',1.0)
edge_recess_blend_r=param('back_cover_edge_recess_blend_radius',2.0)
top_edge_recess_length=param('back_cover_top_edge_recess_length',29.0)
power_edge_recess_length=param('back_cover_power_edge_recess_length',22.0)
shutter_edge_recess_length=param('back_cover_shutter_edge_recess_length',22.0)
edge_recess_overrun=1.0
from math import acos, sin, cos, sqrt
def smooth_recess_profile(length,depth,blend_r,axis,start,outer_side):
 assert blend_r>depth/2
 theta=acos(1-depth/(2*blend_r))
 half_span=blend_r*sin(theta)
 blend_span=2*half_span
 assert 2*blend_span<length
 # Each end consists of two equal-radius, opposite-curvature arcs.
 # Tangents at the outer edge and inset straight both run along the edge.
 u1=blend_r*sin(theta/2)
 v1=blend_r*(1-cos(theta/2))
 left_points=[(0,0),(u1,v1),(half_span,depth/2),
              (blend_span-u1,depth-v1),(blend_span,depth)]
 def point(uv):
  u,v=uv
  return (start+u,outer_side-v,0) if axis=='y' else (outer_side-v,start+u,0)
 p=[point(uv) for uv in left_points]
 q=[point((length-u,v)) for u,v in left_points]
 edges=[Edge.make_three_point_arc(p[0],p[1],p[2]),
        Edge.make_three_point_arc(p[2],p[3],p[4]),
        Edge.make_line(p[4],q[4]),
        Edge.make_three_point_arc(q[4],q[3],q[2]),
        Edge.make_three_point_arc(q[2],q[1],q[0]),
        Edge.make_line(q[0],point((length,-edge_recess_overrun))),
        Edge.make_line(point((length,-edge_recess_overrun)),point((0,-edge_recess_overrun))),
        Edge.make_line(point((0,-edge_recess_overrun)),p[0])]
 profile=Face(Wire(edges))
 assert profile.is_valid and len(profile.wires())==1
 return profile,blend_span
top_edge_recess_left=top_open_right-top_edge_recess_length
top_edge_recess_inner_y=ho/2-edge_recess_inset
top_edge_recess_profile,top_transition_span=smooth_recess_profile(
 top_edge_recess_length,edge_recess_inset,edge_recess_blend_r,'y',
 top_edge_recess_left,ho/2)
edge_recess_profiles=[top_edge_recess_profile]
side_edge_recess_inner_x=right_inner
side_edge_recess_inset=right_x-side_edge_recess_inner_x
side_transition_spans=[]
for side_center,side_length in [(power_y,power_edge_recess_length),(shutter_y,shutter_edge_recess_length)]:
 side_profile,side_span=smooth_recess_profile(side_length,side_edge_recess_inset,
  edge_recess_blend_r,'x',side_center-side_length/2,right_x)
 edge_recess_profiles.append(side_profile)
 side_transition_spans.append(side_span)
edge_recess_cutters=[]
for recess_profile in edge_recess_profiles:
 recess_cutter=Pos(0,0,outside_z-1)*extrude(recess_profile,
  amount=plate+wall_h+2,dir=(0,0,1))
 edge_recess_cutters.append(recess_cutter)
 body-=recess_cutter
print('Inner cavity / outer overall',inner.bounding_box().size.X,inner.bounding_box().size.Y,wo,ho)
print('Recess overall entrance lengths',top_edge_recess_length,power_edge_recess_length,shutter_edge_recess_length)
print('Top inset / side step inset',edge_recess_inset,side_edge_recess_inset,'step X',side_edge_recess_inner_x)
print('All six end transitions radius',edge_recess_blend_r,'transition spans',top_transition_span,side_transition_spans)
body=body.clean()

assert body.is_valid and len(body.solids())==1
# Retained right-side and corner segments, outside the extended long openings.
probe_size=0.05
for px,py in ((-108,hi/2-lip+0.05),(30,hi/2-lip+0.05),
              (-109,-hi/2+lip-0.05),(30,-hi/2+lip-0.05),
              (right_x-wall-lip+0.05,40),(right_x-wall-lip+0.05,0),
              (right_x-wall-lip+0.05,-44)):
 probe=Pos(px,py,seat_z+wall_h-lip_h/2)*Box(probe_size,probe_size,probe_size)
 assert abs((body&probe).volume-probe.volume)<1e-7
print('Top opening endpoint X',2*shift-top_open_right,top_open_right,'equal end land',right_x-top_open_right)
print('Bottom opening endpoint X',2*shift-bottom_open_right,bottom_open_right,'equal end land',right_x-bottom_open_right)
print('Left straight inner lip released Y',-release_half_h,release_half_h,'except centered tab length',center_lip_length)
print('Display clear W/H',window_w,window_h,'center',window_x,'cover mouth W/H',mouth_w,mouth_h)
body.color=srgb('#d5223e')
publish('back_cover',body,'封闭背板一体主壳',material='tpu')

print('Sealed display inner recess depth/floor/base thickness',recess_depth,recess_floor,plate-recess_depth)
