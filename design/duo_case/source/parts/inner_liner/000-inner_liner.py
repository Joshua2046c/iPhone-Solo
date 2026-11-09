s=part('back_cover')
edge_gap=param('inner_liner_wall_clearance',0.2)
screen_gap=param('inner_liner_screen_clearance',0.4)
camera_gap=param('inner_liner_camera_clearance',0.5)
outside=offset(s.inner,amount=-edge_gap)
screen_keepout=offset(s.mouth,amount=screen_gap)
camera_keepout=Pos(s.cam_x,s.cam_y)*offset(s.glass,amount=s.cam_inner_expand+camera_gap)
# Keep only the camera-side sheet, with a straight edge beyond the screen opening.
liner_left=s.window_right+screen_gap
camera_side=Pos(liner_left+s.wo/2,0)*Rectangle(s.wo,s.ho)
cut_profile=(outside-screen_keepout-camera_keepout)&camera_side
# Remove the sub-millimetre corner offcut detached by the camera relief.
faces=sorted(cut_profile.faces(),key=lambda f:f.area)
assert sum(f.area for f in faces[:-1])<1.0
profile=faces[-1]
body=Pos(0,0,s.seat_z)*extrude(profile,amount=s.liner_t)
assert body.is_valid and len(body.solids())==1
assert abs(body.bounding_box().size.Z-s.liner_t)<1e-6
assert abs(body.bounding_box().min.X-liner_left)<1e-6
body.color=srgb('#3e4044')
print('Liner straight left cut X',liner_left,'camera-side coverage only')
print('Liner total thickness',s.liner_t,'floor and phone plane',s.seat_z,s.phone_seat_z)
publish('inner_liner',body,'0.2毫米内保护贴片',material='tpu')
