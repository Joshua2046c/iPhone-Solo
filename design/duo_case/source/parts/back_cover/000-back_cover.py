# Fixed-open one-piece tray. Camera-side datum and original access geometry are retained.
phone_w=param('back_cover_open_phone_width',164.6)
phone_h=param('back_cover_open_phone_height',117.8)
phone_t=param('back_cover_open_phone_thickness',5.2)
right_x=param('back_cover_right_datum_x',43.9)
liner_t=param('back_cover_liner_thickness',0.2)
wall_h=param('back_cover_wall_height',6.28)+liner_t
clearance=param('back_cover_fit_clearance',0.25)
inner_wall_inset=param('back_cover_inner_wall_inset',0.045)
wall=param('back_cover_wall',1.6)
plate=param('back_cover_plate',3.4)
seat_z=param('back_cover_phone_seat_z',2.4)
phone_seat_z=seat_z+liner_t
radius=param('back_cover_corner_radius',12.0)
lip=param('back_cover_corner_inward',0.7)
lip_h=param('back_cover_lip_height',0.7)
outer_round=param('back_cover_outer_rim_radius',0.8)
opening_soft=param('back_cover_opening_edge_radius',0.3)
turn=param('back_cover_opening_turn_radius',1.0)
cam_w=param('back_cover_camera_width',58.3)
cam_h=param('back_cover_camera_height',22.5)
cam_x=param('back_cover_camera_x',10.0)
cam_y=param('back_cover_camera_y',43.9)
cam_inner_expand=param('back_cover_camera_inner_expansion',4.0)
cam_inner_depth=param('back_cover_camera_inner_depth',3.9)
land_h=param('back_cover_camera_vertical_land_height',0.3)
power_y=param('back_cover_power_y',16.1)
power_l=param('back_cover_power_opening',24.8)
shutter_y=param('back_cover_shutter_y',-27.0)
shutter_l=param('back_cover_shutter_opening',23.0)
corner_lip_relief=param('back_cover_corner_lip_relief',0.1)
wi,hi=phone_w+2*clearance,phone_h+2*clearance
wo,ho=wi+2*wall,hi+2*wall
shift=right_x-wo/2
edge_x=shift-wo/2
# Keep original right endpoints, mirror their left endpoints about the full-body center.
top_open_right=param('back_cover_top_opening_right_end_x',24.0)
bottom_open_right=param('back_cover_bottom_opening_right_end_x',26.9)
vol_x=shift
vol_w=2*(top_open_right-shift)-2*turn
bottom_x=shift
bottom_w=2*(bottom_open_right-shift)-2*turn
outside_z=seat_z-plate
outer=Pos(shift,0)*RectangleRounded(wo,ho,radius+wall)
inner=Pos(shift,0)*RectangleRounded(wi,hi,radius)
inner=offset(inner,amount=-inner_wall_inset)
assert clearance>inner_wall_inset and 0<lip<wall and radius>lip
corner_lip_radius=radius-lip-corner_lip_relief/(2**0.5-1)
lip_inner=Pos(shift,0)*RectangleRounded(wi-2*lip,hi-2*lip,corner_lip_radius)
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
 ('x',shift+wo/2,shift+wi/2-inner_wall_inset,power_y-power_l/2-turn,power_y+power_l/2+turn),
 ('x',shift+wo/2,shift+wi/2-inner_wall_inset,shutter_y-shutter_l/2-turn,shutter_y+shutter_l/2+turn))
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

# Preserve the independent bottom interface with its existing clipped R0.3 wall.
unrolled_access_body=body
# Roll the touch-facing outer U rim, including its new profile arcs.
opening_edges=[]
for axis,outer_side,inner_side,lo,upper in openings:
 chosen=[]
 for e in body.edges():
  bb=e.bounding_box()
  amin,amax=(bb.min.X,bb.max.X) if axis=='x' else (bb.min.Y,bb.max.Y)
  bmin,bmax=(bb.min.Y,bb.max.Y) if axis=='x' else (bb.min.X,bb.max.X)
  on_outer=abs(amin-outer_side)<eps and abs(amax-outer_side)<eps
  on_inner=abs(amin-inner_side)<eps and abs(amax-inner_side)<eps
  in_span=bmin>=lo-turn-eps and bmax<=upper+turn+eps
  rising=bb.max.Z-bb.min.Z>eps
  if bb.min.Z>=seat_z-eps and in_span and on_outer:
   chosen.append(e)
 assert len(chosen)>=5, 'Incomplete blended rim'
 opening_edges.extend(chosen)
body=fillet(opening_edges,radius=opening_soft)

original_bottom_body=floor_with_carrier+(body&Pos(shift,0,seat_z+wall_h/2)*Box(wo+2,ho+2,wall_h))
access_partition_y=shutter_y-shutter_l/2-2*turn
lower_access_mask=Pos(shift,(access_partition_y-ho/2-1)/2,(outside_z+seat_z+wall_h)/2)*Box(wo+20,access_partition_y+ho/2+1,plate+wall_h+2)
upper_access_mask=Pos(shift,(access_partition_y+ho/2+1)/2,(outside_z+seat_z+wall_h)/2)*Box(wo+20,ho/2+1-access_partition_y,plate+wall_h+2)
original_bottom_body &= lower_access_mask
body=unrolled_access_body

# Keep only the finished access wall above the plate, then merge it with the continuous rounded base.
finished_wall=body&Pos(shift,0,seat_z+wall_h/2)*Box(wo+2,ho+2,wall_h)
body=floor_with_carrier+finished_wall

# Constant-angle finger ramp and tangent lower corner are one opening profile.
ramp_angle=param('back_cover_button_ramp_angle',20.0)
from math import tan, radians
ramp_slope=tan(radians(ramp_angle))
ramp_specs=[
 ('power','x',shift+wi/2-inner_wall_inset,shift+wo/2,power_y,power_l),
 ('shutter','x',shift+wi/2-inner_wall_inset,shift+wo/2,shutter_y,shutter_l),
 ('volume','y',hi/2-inner_wall_inset,ho/2,vol_x,vol_w)]
ramp_depth=(wall+inner_wall_inset)*ramp_slope
assert 0<ramp_angle<30
ramp_cutters=[]
for axis,outer_side,inner_side,lo,upper in openings:
 a=min(inner_side,outer_side)-lip-0.5
 c=max(inner_side,outer_side)+lip+0.5
 local_slope=ramp_slope if outer_side>0 else 0
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
# Assemble the ramped button section with the unchanged bottom interface.
body=(body&upper_access_mask)+original_bottom_body
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



# Reference 3MF-inspired left outer-display opening, with an external hinged cover.
window_w=param('back_cover_display_clear_width',75.8)
window_h=param('back_cover_display_clear_height',113.6)
window_r=param('back_cover_display_corner_radius',10.5)
window_x=shift-phone_w/4
stop_land=param('back_cover_lid_stop_land',0.8)
stop_t=param('back_cover_lid_stop_thickness',0.8)
lid_top_gap=param('back_cover_lid_stop_clearance',0.1)
lid_side_gap=param('back_cover_lid_edge_clearance',0.25)
mouth_w=window_w+2*stop_land
mouth_h=window_h+2*stop_land
mouth_r=window_r+stop_land
window_left=window_x-mouth_w/2
window_right=window_x+mouth_w/2
mouth=Pos(window_x,0)*RectangleRounded(mouth_w,mouth_h,mouth_r)
clear_window=Pos(window_x,0)*RectangleRounded(window_w,window_h,window_r)
body-=Pos(0,0,outside_z-1)*extrude(mouth,amount=plate+2)
stop_ring=Pos(0,0,seat_z-stop_t)*extrude(offset(mouth,amount=0.1)-clear_window,amount=stop_t)
body+=stop_ring
# Remove only the straight inner return on the marked left short edge.
release_half_h=ho/2-(radius+wall)
lip_clear=Pos(edge_x+wall+inner_wall_inset+lip,0,seat_z+wall_h-lip_h/2)*Box(2*lip,2*release_half_h,lip_h+0.02)
body-=lip_clear

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
hinge_span=param('back_cover_lid_hinge_span',200.0/3.0)
grip_root_margin=param('back_cover_grip_hinge_margin',2.0)
# Stop the shallow texture before the hinge load path.
texture_keepout=Pos(edge_x,0,(outside_z+seat_z+wall_h)/2)*Box(2*(wall+2),hinge_span+2*grip_root_margin,plate+wall_h+4)
for i in range(int(grip_count)):
 band=Pos(0,0,grip_first_z+i*grip_pitch-grip_height/2)*groove_tool
 body-=band-texture_keepout

# Compact hinge within the case outline; fixed knuckles have full integral bases.
frame_before_hinge=body
lid_barrel_r=param('back_cover_lid_barrel_radius',2.6)
lid_socket_gap=param('back_cover_lid_socket_clearance',0.25)
hinge_edge_margin=param('back_cover_hinge_edge_margin',0.1)
fixed_barrel_r=lid_barrel_r
lid_axis_x=edge_x+fixed_barrel_r+hinge_edge_margin
lid_axis_z=outside_z-fixed_barrel_r-lid_socket_gap
support_z=lid_axis_z-lid_barrel_r
lid_bore_r=param('back_cover_lid_bore_radius',1.4)
lid_hinge_end=hinge_span/2
lid_hinge_outer_inner=hinge_span*0.34
lid_hinge_center_half=hinge_span*0.10
pin_retention_d=param('back_cover_lid_pin_retention_diameter',2.05)
pin_retention_r=pin_retention_d/2
lid_hinge_axial_gap=param('back_cover_lid_hinge_axial_gap',0.5)
lid_hinge_root_overlap=param('back_cover_lid_hinge_root_overlap',4.0)
pin_lead=param('back_cover_lid_pin_lead_length',0.5)
fixed_root_bond=param('back_cover_lid_fixed_root_bond',0.8)
fixed_web_round=param('back_cover_lid_fixed_web_edge_radius',0.3)
lid_knuckle_intervals=[(-lid_hinge_outer_inner+lid_hinge_axial_gap,-lid_hinge_center_half-lid_hinge_axial_gap),
                       (lid_hinge_center_half+lid_hinge_axial_gap,lid_hinge_outer_inner-lid_hinge_axial_gap)]
fixed_knuckle_intervals=[(-lid_hinge_end,-lid_hinge_outer_inner),(-lid_hinge_center_half,lid_hinge_center_half),(lid_hinge_outer_inner,lid_hinge_end)]
for ya,yb in fixed_knuckle_intervals:
 yc=(ya+yb)/2
 barrel=Pos(lid_axis_x,yc,lid_axis_z)*Cylinder(fixed_barrel_r,yb-ya,rotation=(90,0,0))
 base_left=lid_axis_x-fixed_barrel_r
 base_right=window_left
 base_top=outside_z+fixed_root_bond
 base_bottom=lid_axis_z
 assert base_right>base_left
 base=Pos((base_left+base_right)/2,yc,(base_bottom+base_top)/2)*Box(base_right-base_left,yb-ya,base_top-base_bottom)
 # The outside vertical wall is tangent to the upper circular crown.
 knuckle=barrel+base
 knuckle=fillet(knuckle.edges().filter_by(Axis.Y),radius=fixed_web_round)
 bore_r=pin_retention_r if ya<0<yb else lid_bore_r
 knuckle-=Pos(lid_axis_x,yc,lid_axis_z)*Cylinder(bore_r,yb-ya+2,rotation=(90,0,0)).rotate(Axis.Y,45)
 if ya<0<yb:
  for sign in (-1,1):
   lead=Cone(lid_bore_r,pin_retention_r,pin_lead).rotate(Axis.X,90 if sign>0 else -90)
   knuckle-=Pos(lid_axis_x,sign*(lid_hinge_center_half-pin_lead/2),lid_axis_z)*lead
 body+=knuckle

# Two blind-bottom catches: the lower 1.2 mm stock is the mechanical retaining shoulder.
latch_tip_y=param('back_cover_lid_latch_tip_y',24.0)
latch_hook_l=param('back_cover_lid_latch_hook_length',2.4)
latch_receiver_depth=param('back_cover_lid_latch_receiver_depth',1.2)
latch_shoulder_t=param('back_cover_lid_latch_shoulder_thickness',1.2)
latch_pocket_y_gap=param('back_cover_lid_latch_receiver_y_gap',0.3)
for sign in (-1,1):
 yc=sign*(latch_tip_y+latch_hook_l/2)
 body-=Pos(window_right+(latch_receiver_depth-0.05)/2,yc,outside_z+latch_shoulder_t+(plate-latch_shoulder_t+1)/2)*Box(latch_receiver_depth+0.05,latch_hook_l+2*latch_pocket_y_gap,plate-latch_shoulder_t+1)
# A centered finger recess on the fixed frame gives access to the lid edge.
finger_l=param('back_cover_lid_finger_slot_length',16.0)
finger_w=param('back_cover_lid_finger_slot_width',8.0)
finger_depth=param('back_cover_lid_finger_slot_depth',1.4)
finger_profile=Pos(window_right,0)*SlotOverall(finger_l,finger_w,rotation=90)
body-=Pos(0,0,outside_z-0.05)*extrude(finger_profile,amount=finger_depth+0.05)
# The main phone tray remains one fixed-open frame even when the small display lid is open.
bridge_probe=Pos(shift+4.0,0,outside_z+plate/2)*Box(2*wall,hi-2*radius,plate)
assert abs((body&bridge_probe).volume-bridge_probe.volume)<1e-5
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
print('Left straight inner lip removed Y',-release_half_h,release_half_h)
print('Display clear W/H',window_w,window_h,'center',window_x,'cover mouth W/H',mouth_w,mouth_h)
print('Hinge axis X/Z',lid_axis_x,lid_axis_z,'support plane',support_z,'body valid solids',len(body.solids()))
print('Finger slot length/width/depth',finger_l,finger_w,finger_depth)
print('Hinge bottom / camera crest',lid_axis_z-lid_barrel_r,part('camera_guard').crest_z)
assert abs(lid_axis_z-lid_barrel_r-support_z)<1e-7
body.color=srgb('#d5223e')
publish('back_cover',body,'带屏幕窗一体主壳',material='tpu')
