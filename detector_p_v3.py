import cv2
import numpy as np
import statistics
import argparse
import math
def less_contours(contours):
	info=[]
	for c in range(len(contours)):
		areas=[]		
		cont_our=contours[c]
		if cv2.contourArea(cont_our)>1000:
			areas.append(c)
			areas.append(cv2.contourArea(cont_our))
			info.append(areas)
		
	
	info=sorted(info,key=lambda info:info[1])
	return(info)
		
		

def is_inside(contour1,contour2):
   prom=[]
   for c1 in contour2:
   	n=cv2.pointPolygonTest(contour1,(c1[0][0],c1[0][1]),False)
   	prom.append(n)
   return(statistics.mean(prom))
def centroid(c):
   good=False
   M_p=cv2.moments(c)
   cx=0
   cy=0
   if M_p['m00']!=0:
   	cx=int(M_p['m10']/M_p['m00'])
   	cy=int(M_p['m01']/M_p['m00'])
   	good=True
   return cx,cy,good
def check_owner(c1,v_c):
	ok=False
	for c in v_c:
		if is_inside(c1,c)==0:
			ok=True
	return ok
def get_petal_contours(img,liminf_fungi,limsup_fungi,liminf_petal,limsup_petal):
	hsv_img=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
	fungi_mask=cv2.inRange(hsv_img,liminf_fungi,limsup_fungi)
	petal_mask=cv2.inRange(hsv_img,liminf_petal,limsup_petal)
	fungi_mask=cv2.medianBlur(fungi_mask,3)
	petal_mask=cv2.medianBlur(petal_mask,3)
	petals_total=cv2.bitwise_or(fungi_mask,petal_mask)
	for k in range(0,1):
		petals_total=cv2.medianBlur(petals_total,11)
		
	
	#cv2.imshow("petalos",petals_total)
	contours_total_petal,hierarchy=cv2.findContours(petals_total,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
	npet=0
	ratio_tray=[]
	for pet in contours_total_petal:
		
		if cv2.contourArea(pet)>80:
			petal_data=[]
			npet=npet+1
			x_p,y_p,w_p,h_p=cv2.boundingRect(pet)
			c_x_p,c_y_p,flag=centroid(pet)
						
			ind_petal_petal=cv2.inRange(hsv_img[y_p:y_p+h_p,x_p:x_p+w_p],liminf_petal,limsup_petal)
			ind_petal_fungi=cv2.inRange(hsv_img[y_p:y_p+h_p,x_p:x_p+w_p],liminf_fungi,limsup_fungi)
			contours_ind_petal,hierarchy=cv2.findContours(ind_petal_petal,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
			contours_ind_fungi,hierarchy=cv2.findContours(ind_petal_fungi,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
			area_p=0
			for pp_1 in contours_ind_petal:
				cv2.drawContours(img[y_p:y_p+h_p,x_p:x_p+w_p],[pp_1],-1,(0,0,255),2)
				area_p=area_p+cv2.contourArea(pp_1)
			area_f=0							
			for ff_1 in contours_ind_fungi:
				cv2.drawContours(img[y_p:y_p+h_p,x_p:x_p+w_p],[ff_1],-1,(0,255,255),2)
				area_f=area_f+cv2.contourArea(ff_1)
			petal_data.append(npet)
			petal_data.append(round((area_f/(area_f+area_p))*100,2))
			petal_data.append(round((area_p/(area_f+area_p))*100,2))
			petal_data.append(0)
			petal_data.append(0)			
			#cv2.drawContours(img,[pet],-1,(0,255,0),3)
			cv2.putText(img, str(npet), (c_x_p,c_y_p), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
			#cv2.imshow("petalos",img[y_p:y_p+h_p,x_p:x_p+w_p])
			#cv2.waitKey(0)
			ratio_tray.append(petal_data)
	sum_h=0
	sum_p=0
	if len(ratio_tray)>0:
		for d in ratio_tray:
			sum_h=sum_h+d[1]
			sum_p=sum_p+d[2]
		sum_h=sum_h/len(ratio_tray)
		sum_p=sum_p/len(ratio_tray)
		#nums_v=[]
		num_h=round((sum_h/100)*5,2)
		num_p=round((sum_p/100)*5,2)
		for n_r in ratio_tray:
			n_r[3]=num_h
			n_r[4]=num_p
	#nums_v.append(num_h)
	#nums_v.append(num_p)
	#ratio_tray.append(nums_v)
	#cv2.waitKey(0)
	
	return ratio_tray,img
def order_by_origin(cnt,idx):
	a=[]
	for x in idx:
		b=[]
		x_cnt=cnt[x]
		cxc,cyc,g=centroid(x_cnt)
		d=math.sqrt(cxc*cxc+cyc*cyc)
		b.append(x)
		b.append(d)
		a.append(b)
	
	a=sorted(a,key=lambda a:a[1])
	#print(a)
	
      		
	return ([z[0] for z in a ])
	

	
	
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True, help = "Path to the image")
ap.add_argument("-f", "--folder", required = True, help = "Folder destination")
args = vars(ap.parse_args())
img=cv2.imread(args["image"])
print(img.shape)
#img_last_rgb=img
img_last_rgb=cv2.resize(img,(1280,960))
liminf_boxes=(0,0,0)
limsup_boxes=(124,139,118)
liminf_fungi=(0,86,6)
limsup_fungi=(64,255,255)
liminf_petal=(36,109,26)
limsup_petal=(183,255,255)

box_mask=cv2.inRange(img_last_rgb,liminf_boxes,limsup_boxes)
#cv2.imshow("mask_box",box_mask)
#cv2.imwrite("mask_box.jpg",box_mask)
#kernel=np.ones((3,3),np.uint8)
#kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(1,1))
#filtered_boxes=cv2.morphologyEx(box_mask,cv2.MORPH_OPEN,kernel)
#Con cajas negras no hay que hacer esto tantas veces
filtered_boxes=cv2.medianBlur(box_mask,3)
for i in range(0,20):
	filtered_boxes=cv2.medianBlur(filtered_boxes,3)
#_____________________________________________#
contours_boxes,hierarchy_boxes=cv2.findContours(filtered_boxes,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
#print(len(contours_boxes))
i=0
file_info=open(args["folder"]+"results_"+args["image"]+".csv","+w")
file_info.write("tratamiento,repeticion,individuo,hongo,petalo,NUM_hongo,NUM_petalo\n")
for m_c in contours_boxes:
   area_box=cv2.contourArea(m_c)
   if area_box>10000:
   	x,y,w,h=cv2.boundingRect(m_c)
   	c_x,c_y,flag=centroid(m_c)
   	dummy=filtered_boxes[y:y+h,x:x+w]
   	actual_img=img_last_rgb[y:y+h,x:x+w]
   	copy_actual_img=actual_img.copy()
   	i=i+1
   	
   	contours_inner,hierarchy_inner=cv2.findContours(dummy,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
   	#contours_inner.sort( key=lambda x:cv2.contourArea(x))
   	#contours_inner.sort(key=lambda b:b[1])
   	#cv2.imshow("dummy",dummy)
   	
   	
   	#cv2.imshow("ind",actual_img)
   	
   	#cv2.waitKey(0)
   	matrix=less_contours(contours_inner)
   	#print(matrix)
   	idx=[]
   	for y in range(0,3):
   		try:
   			idx.append(matrix[y][0])
   		except:
   			print("Error:no hubo detección de bandeja")
   			
   	#print(idx)
   	
   	idx=order_by_origin(contours_inner,idx)
   	j=0
   		
   	for i_c in idx:
   		#print(x,y,w/2,h/2)
   		cnt_i=contours_inner[i_c]
   		#print(distance_to_origin(cnt_i))
   		if cv2.contourArea(cnt_i)>100:
   			x_1,y_1,w_1,h_1=cv2.boundingRect(cnt_i)
   			j=j+1
   			c_x_1,c_y_1,flag=centroid(cnt_i)
   			#cv2.drawContours(actual_img,[cnt_i],-1,(0,255,0),1)
   			ratio_matrix,cropped=get_petal_contours(copy_actual_img[y_1:y_1+h_1,x_1:x_1+w_1],liminf_fungi,limsup_fungi,liminf_petal,limsup_petal)
   			actual_img[y_1:y_1+h_1,x_1:x_1+w_1]=cropped
   			#print(ratio_matrix)
   			for data in ratio_matrix:
   				file_info.write(str(i)+","+str(j)+","+str(data[0])+","+str(data[1])+","+str(data[2])+","+str(data[3])+","+str(data[4])+"\n")
   				
   				
   				
   			
   			cv2.putText(actual_img, str(j), (c_x_1,c_y_1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)
   			#print(c_x-w/2,c_y-h/2)
   			
   			cv2.putText(img_last_rgb, str(i), (int(c_x-w/2),int(c_y-h/2+20)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
   			#cv2.imshow("ind",cropped)
   			
   			#cv2.waitKey(0)
   			#print(cv2.contourArea(cnt_i))
   			
   
   
print(i)
#cv2.drawContours(img_last_rgb,contours_boxes,-1,(0,255,0),1)
#cv2.imshow("cajas",filtered_boxes)
#cv2.imshow("cajas_2",img_last_rgb)
cv2.imwrite(args["folder"]+"resultado"+args["image"],img_last_rgb)
file_info.close()
print("Done..")
#cv2.waitKey(0)

	