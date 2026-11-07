
s=part('back_cover')
t=param('display_lid_thickness',2.5)
edge_r=param('display_lid_edge_radius',0.45)
arm_w=param('display_lid_latch_arm_width',2.0)
arm_l=param('display_lid_latch_arm_length',16.0)
slit_w=param('display_lid_latch_slit_width',1.0)
hook_reach=param('display_lid_latch_hook_reach',0.75)
hook_h=param('display_lid_latch_hook_height',1.1)
hook_bottom=param('display_lid_latch_hook_bottom_z',0.4)
hook_edge_r=param('display_lid_latch_hook_edge_radius',0.15)
lid_w=s.mouth_w-2*s.lid_side_gap
lid_h=s.mouth_h-2*s.lid_side_gap
lid_r=s.mouth_r-s.lid_side_gap
left=s.window_x-lid_w/2
right=s.window_x+lid_w/2
profile=Pos(s.window_x,0)*RectangleRounded(lid_w,lid_h,lid_r)
body=Pos(0,0,s.outside_z)*extrude(profile,amount=t)
rim_edges=[e for e in body.edges() if e.bounding_box().size.Z<1e-6]
body=fillet(rim_edges,radius=edge_r)
# Two integral tongues bend in the plane of the cover, away from the fixed catch.
hooks=[]
release_pads=[]
pad_h=param('display_lid_release_pad_height',0.6)
root_inner_setback=param('display_lid_hinge_inner_setback',0.25)
root_outer_inset=param('display_lid_hinge_outer_bond_inset',0.05)
web_round=param('display_lid_hinge_web_edge_radius',0.3)
for sign in (-1,1):
 tip_y=sign*s.latch_tip_y
 root_y=sign*(s.latch_tip_y+arm_l)
 arm_cy=(tip_y+root_y)/2
 long_slot=Pos(right-arm_w-slit_w/2,arm_cy-sign*slit_w/2)*RectangleRounded(slit_w,arm_l+slit_w,slit_w*0.45)
 body-=Pos(0,0,s.outside_z-1)*extrude(long_slot,amount=t+2)
 end_slot=Pos(right-(arm_w+slit_w)/2,tip_y-sign*slit_w/2)*SlotOverall(arm_w+slit_w+0.2,slit_w)
 body-=Pos(0,0,s.outside_z-1)*extrude(end_slot,amount=t+2)
 hook=Pos(right+(hook_reach-0.05)/2,sign*(s.latch_tip_y+s.latch_hook_l/2),hook_bottom+hook_h/2)*Box(hook_reach+0.05,s.latch_hook_l,hook_h)
 hook=fillet(hook.edges().filter_by(Axis.Y),radius=hook_edge_r)
 body+=hook
 hooks.append(hook)
 pad=Pos(right-arm_w/2,sign*(s.latch_tip_y+s.latch_hook_l/2),s.outside_z-pad_h/2+0.025)*Box(arm_w-0.2,s.latch_hook_l+0.4,pad_h+0.05)
 pad=fillet(pad.edges(),radius=0.15)
 body+=pad
 release_pads.append(pad)
# The conservative released envelope fills the narrow slots, while withdrawing the two hooks.
released_envelope=Pos(0,0,s.outside_z)*extrude(profile,amount=t)
for ya,yb in s.lid_knuckle_intervals:
 yc=(ya+yb)/2
 barrel=Pos(s.lid_axis_x,yc,s.lid_axis_z)*Cylinder(s.lid_barrel_r,yb-ya,rotation=(90,0,0))
 # Solid gusset fills the space under the 45-degree face and bonds into the cover.
 root_end=left+s.lid_hinge_root_overlap
 root_top=s.outside_z+t-root_inner_setback
 root_bottom=s.outside_z+root_outer_inset
 web_start=s.lid_axis_x+0.5*s.lid_barrel_r
 run=root_end-web_start
 assert run>0 and (root_top-root_bottom)/(2**0.5)>=1.2
 web_profile=Polygon((web_start,root_bottom-run),(root_end,root_bottom),(root_end,root_top),(left+edge_r,root_top),(web_start,root_top-run),align=None)
 web=Pos(0,ya,0)*extrude(Plane.XZ*web_profile,amount=yb-ya,dir=(0,1,0))
 web=fillet(web.edges().filter_by(Axis.Y),radius=web_round)
 bore=Pos(s.lid_axis_x,yc,s.lid_axis_z)*Cylinder(s.lid_bore_r,yb-ya+2,rotation=(90,0,0))
 body+=barrel+web
 body-=bore
 released_envelope+=barrel+web
 released_envelope-=bore

assert 6<=arm_l/arm_w<=10
latch_engagement=hook_reach-s.lid_side_gap
# Clearance for the initial arc of the raised hinge.
release_margin=param('display_lid_release_margin',0.3)
required_release=latch_engagement+release_margin
for hook in hooks:
 released_envelope+=Pos(-required_release,0,0)*hook
for pad in release_pads:
 released_envelope+=Pos(-required_release,0,0)*pad
assert required_release<=arm_w/2 and required_release<slit_w
assert abs(s.seat_z-s.stop_t-(s.outside_z+t)-s.lid_top_gap)<1e-6
assert len(body.solids())==1 and body.is_valid
print('Lid W/H/thickness',lid_w,lid_h,t,'per-side gap',s.lid_side_gap)
print('Latch arm L/W',arm_l,arm_w,'engagement',latch_engagement,'required release',required_release)
print('Lid inner plane',s.outside_z+t,'phone plane clearance',s.seat_z-(s.outside_z+t))
body.color=srgb('#d5223e')
publish('display_lid',body,'180度屏幕盖板',material='petg')
