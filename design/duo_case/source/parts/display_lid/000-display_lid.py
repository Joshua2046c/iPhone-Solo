
s=part('back_cover')
t=param('display_lid_thickness',1.6)
# Keep the phone-facing surface and stop gap fixed as the outer face is thinned.
lid_outer_z=s.seat_z-s.stop_t-s.lid_top_gap-t
edge_r=param('display_lid_edge_radius',0.45)
arm_w=param('display_lid_latch_arm_width',2.0)
arm_l=param('display_lid_latch_arm_length',16.0)
slit_w=param('display_lid_latch_slit_width',1.0)
hook_reach=param('display_lid_latch_hook_reach',0.75)
hook_h=param('display_lid_latch_hook_height',0.8)
hook_bottom=param('display_lid_latch_hook_bottom_z',0.7)
hook_edge_r=param('display_lid_latch_hook_edge_radius',0.15)
lid_w=s.mouth_w-2*s.lid_side_gap
lid_h=s.mouth_h-2*s.lid_side_gap
lid_r=s.mouth_r-s.lid_side_gap
left=s.window_x-lid_w/2
right=s.window_x+lid_w/2
hinge_sign=1 if s.lid_axis_x>s.window_x else -1
hinge_edge=right if hinge_sign>0 else left
latch_edge=left if hinge_sign>0 else right
profile=offset(s.mouth,amount=-s.lid_side_gap,kind=Kind.INTERSECTION)
body=Pos(0,0,lid_outer_z)*extrude(profile,amount=t)
rim_edges=[e for e in body.edges() if e.bounding_box().size.Z<1e-6]
body=fillet(rim_edges,radius=edge_r)
# One centered integral tongue bends inward, away from the fixed catch.
hooks=[]
release_pads=[]
pad_h=param('display_lid_release_pad_height',0.6)
root_inner_setback=param('display_lid_hinge_inner_setback',0.25)
root_outer_inset=param('display_lid_hinge_outer_bond_inset',0.05)
web_round=param('display_lid_hinge_web_edge_radius',0.3)
neck_h=param('display_lid_hinge_neck_height',2.2)
latch_center_y=s.finger_profile.center().Y
tip_y=latch_center_y-s.latch_hook_l/2
root_y=tip_y+arm_l
arm_cy=(tip_y+root_y)/2
long_slot=Pos(latch_edge+hinge_sign*(arm_w+slit_w/2),arm_cy-slit_w/2)*RectangleRounded(slit_w,arm_l+slit_w,slit_w*0.45)
body-=Pos(0,0,lid_outer_z-1)*extrude(long_slot,amount=t+2)
end_slot=Pos(latch_edge+hinge_sign*(arm_w+slit_w)/2,tip_y-slit_w/2)*SlotOverall(arm_w+slit_w+0.2,slit_w)
body-=Pos(0,0,lid_outer_z-1)*extrude(end_slot,amount=t+2)
hook=Pos(latch_edge-hinge_sign*(hook_reach-0.05)/2,latch_center_y,hook_bottom+hook_h/2)*Box(hook_reach+0.05,s.latch_hook_l,hook_h)
hook=fillet(hook.edges().filter_by(Axis.Y),radius=hook_edge_r)
body+=hook
hooks.append(hook)
pad=Pos(latch_edge+hinge_sign*arm_w/2,latch_center_y,lid_outer_z-pad_h/2+0.025)*Box(arm_w-0.2,s.latch_hook_l+0.4,pad_h+0.05)
pad=fillet(pad.edges(),radius=0.15)
body+=pad
release_pads.append(pad)
# The conservative released envelope fills the narrow slots, while withdrawing the two hooks.
released_envelope=Pos(0,0,lid_outer_z)*extrude(profile,amount=t)
for ya,yb in s.lid_knuckle_intervals:
 yc=(ya+yb)/2
 barrel=Pos(s.lid_axis_x,yc,s.lid_axis_z)*Cylinder(s.lid_barrel_r,yb-ya,rotation=(90,0,0))
 # Solid gusset fills the space under the 45-degree face and bonds into the cover.
 root_end=hinge_edge-hinge_sign*s.lid_hinge_root_overlap
 root_top=lid_outer_z+t-root_inner_setback
 root_bottom=lid_outer_z+root_outer_inset
 web_start=s.lid_axis_x-hinge_sign*0.5*s.lid_barrel_r
 run=hinge_sign*(web_start-root_end)
 assert run>0 and neck_h/(2**0.5)>=1.2 and root_top-root_bottom>=1.2
 web_profile=Polygon((web_start,root_bottom-run),(root_end,root_bottom),(root_end,root_top),(hinge_edge-hinge_sign*edge_r,root_top),(web_start,root_bottom-run+neck_h),align=None)
 web=Pos(0,ya,0)*extrude(Plane.XZ*web_profile,amount=yb-ya,dir=(0,1,0))
 web=fillet(web.edges().filter_by(Axis.Y),radius=web_round)
 bore=Pos(s.lid_axis_x,yc,s.lid_axis_z)*Cylinder(s.lid_bore_r,yb-ya+2,rotation=(90,0,0))
 body+=barrel+web
 body-=bore
 released_envelope+=barrel+web
 released_envelope-=bore

assert len(hooks)==len(release_pads)==1
assert 6<=arm_l/arm_w<=10
latch_engagement=hook_reach-s.lid_side_gap
# Clearance for the initial arc of the raised hinge.
release_margin=param('display_lid_release_margin',0.3)
required_release=latch_engagement+release_margin
for hook in hooks:
 released_envelope+=Pos(hinge_sign*required_release,0,0)*hook
for pad in release_pads:
 released_envelope+=Pos(hinge_sign*required_release,0,0)*pad
assert required_release<=arm_w/2 and required_release<slit_w
assert abs(s.seat_z-s.stop_t-(lid_outer_z+t)-s.lid_top_gap)<1e-6
assert len(body.solids())==1 and body.is_valid
print('Lid W/H/thickness',lid_w,lid_h,t,'per-side gap',s.lid_side_gap)
print('Latch arm L/W',arm_l,arm_w,'engagement',latch_engagement,'required release',required_release)
print('Lid inner plane',lid_outer_z+t,'phone plane clearance',s.seat_z-(lid_outer_z+t))
body.color=srgb('#d5223e')
publish('display_lid',body,'180度屏幕盖板',material='petg')
