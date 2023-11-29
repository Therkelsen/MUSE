'''
Copyright (C) 2019 Xiaofeng Xiong and Poramate Manoonpong

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

The code has been used to produce the results of the paper: X. Xiong and P. Manoonpong, "Adaptive Motor Control for Human-like Spatial-temporal Adaptation," 2018 IEEE International Conference on Robotics and Biomimetics (ROBIO), Kuala Lumpur, Malaysia, 2018, pp. 2107-2112.
doi: 10.1109/ROBIO.2018.8665222

'''

'''
Tasks:

T1: see pla_postu_con()

T2: see pla_tra()

T3: see get_pos_diff()

T4: see get_vel_diff()

T5: see get_tra_diff()

T6: see get_coe()

T7 and T8: see const_impe()

T9 and T10: see ada_impe()

'''

import copy
import Dyna_moto as Dm
import itertools
import math
import numpy as np
import numpy.random as npr
import time

from datetime import datetime
from os.path import *
from scipy import *

DXL_MOVING_STATUS_THRESHOLD = 20 
import os
if os.name == 'nt':
	import msvcrt
	def getch():
		return msvcrt.getch().decode()
else:
	import sys, tty, termios
	fd = sys.stdin.fileno()
	old_settings = termios.tcgetattr(fd)
	def getch():
		try:
			tty.setraw(sys.stdin.fileno())
			ch = sys.stdin.read(1)
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
		return ch

MinPos = 300#200#
MaxPos = 2350#1200#

MinCur = -10
MaxCur = 10

POS_CONTROL = 3
VEL_CONTROL = 1
CUR_CONTROL = 0

# Data Byte Length
LEN_PRO_GOAL_POSITION       = 4
LEN_PRO_PRESENT_POSITION    = 4
LEN_PRO_PRESENT_VELOCITY    = 4
LEN_PRO_PRESENT_CURRENT    = 2
LEN_PRO_GOAL_CURRENT    = 2

LEN_PRO_GOAL_VELOCITY    = 4

MidPos0 = 1327
MidPos1 = 746
#The middle positions of two motors are  [ 1327.   746.]

CHECK_ID = 0
CHECK_CUR_NUM = 6
BAUDRATE = 3000000#4000000#57600#

CONTROLLER = 'ada_imp'#'const_imp'#
TASK = 'track'#'post_con'#

class Ada_con():
	def __init__(self, con_type = 'impe_con', co_mod = 3, re_only = False, dn = 'COM3'):
		self.dm = Dm.Dyna_moto(baudrate = BAUDRATE, devicename = dn, con_mode = co_mod, ro = re_only)

		self.num_moto = self.dm.moto_num

		#Position angle and velocity feedback obtained from the motor
		self.pos_rad = np.zeros(self.num_moto)
		self.vel_rad = np.zeros(self.num_moto)
		
		#Desired position and velocity
		self.pos_des = np.zeros(self.num_moto)
		self.vel_des = np.zeros(self.num_moto)

		#Position and velocity differences
		self.pos_diff = np.zeros(self.dm.moto_num)
		self.vel_diff = np.zeros(self.dm.moto_num)
		self.tra_diff = np.zeros(self.dm.moto_num)
		self.co_diff = np.zeros(self.dm.moto_num)

		#Torque outputs
		self.tau = np.zeros(self.dm.moto_num)

		#Impedance parameters: stiffness, damping, and bias
		self.k = np.zeros(self.dm.moto_num)
		self.d = np.zeros(self.dm.moto_num)
		self.ff = np.zeros(self.dm.moto_num)

		#constant impedance controller
		self.cons_k = 0.04#1.0#0.1#0.05
		self.cons_d = math.sqrt(self.cons_k)#0.001#

		self.cur4tor = np.zeros(self.num_moto)
		self.pre_pos_des = np.zeros(self.num_moto)
		
		self.task = CONTROLLER #'const_imp'#'ada_imp'#
		self.tra_type = TASK #'track'#'post_con'#

		self.max_noi = np.pi/10.0

		self.safe_rad = np.pi/2.0 + self.max_noi

		if self.tra_type == 'track':
			self.go_t = 7.5#15.0#33.0#51.0#5.0#50.0#160.0#15.0#20.0
		else:
			self.go_t = 10.0#20.0#8.0#15.0#20.0#50.0#160.0

		#tracking
		self.max_tar_rad = np.pi/4.0#np.pi/2.0#np.pi/6.0
		self.cir_num = 3#3
		self.cir_fre = self.cir_num*2*np.pi/self.go_t
		self.tra_pos = 0.00

		self.goal_theta = np.pi/2.0#10.0
		
		self.n_t = 0.00
		self.dt = 0.00
		self.pre_t = 0.00

		self.init_pos = 0.00
		self.target_pos = self.goal_theta
		self.t_s = 0

		self.beta = 0.05#1.0#2.0#5.0
		self.a = 35#0.2
		self.b = 5.0
		self.ine = 0.1#0.05#1

		self.tor_out = False

		self.kp = 100
		self.kv = math.sqrt(self.kp)
		self.cur_k = 60

		self.dif_pos_ave = np.zeros(self.dm.moto_num)
		self.dif_vel_ave = np.zeros(self.dm.moto_num)
		self.cur_ave = np.zeros(self.dm.moto_num)

		#variable impedance
		self.pre_dif_pos = np.zeros(self.num_moto)
		self.pre_dif_vel = np.zeros(self.num_moto)
		self.pre_des_pos = np.zeros(self.num_moto)

		self.save_result = True
		if (self.save_result):
			self.open_files()

	def start(self):
		self.start_timer()

		while(abs(self.pos_rad[CHECK_ID])< self.safe_rad and (self.n_t <= self.go_t)):
			self.n_t = self.now_timer()
			self.dt = self.n_t - self.pre_t

			#Get position and velocity feedbacks from the motor
			self.get_states()

			#Generate the desired motor position
			self.gen_des()

			#Impedance contollers
			self.controllers()

			#Send commands to the motor
			self.SendMotoComm()
			
			self.CalFbAve()

			if (self.save_result):
				self.save_data()
		self.stop_motors()

#(start)------------Generate the desired motor position-------------
	def gen_des(self):
		for i in range(self.num_moto):
			if self.tra_type == 'track':# periodic tracking
				self.init_pos = 0.00
				self.target_pos = self.max_tar_rad
			self.pos_des[i] = self.tra_plan(self.n_t,self.init_pos,self.target_pos) # generate the desired positions

			if self.dt > 0.00:# calculate the desired velocity
				self.vel_des[i] = (self.pos_des[i] - self.pre_pos_des[i])/self.dt
			else:
				self.vel_des[i] = self.vel_des[i]
			
			self.pre_pos_des[i] = self.pos_des[i]
			self.cur4tor[i] = self.dm.now_tor[i]
		self.pre_t = copy.copy(self.n_t)

	def tra_plan(self,t, ini_pos, tar_pos):	
		# two desired position generators
		if self.tra_type == 'track':
			return self.pla_tra(t, ini_pos, tar_pos)# periodic tracking
		else:
			return self.pla_postu_con(t, ini_pos, tar_pos)# posture control

	def pla_postu_con(self,t, ini_pos, tar_pos):# posture control
		#keep initial motor angle without respect to t, ini_pos, tar_pos
		
		#T1
		return 0.00

	def pla_tra(self,t, ini_pos, tar_pos):# periodic tracking
		#generate the periodic function math.sin with respect to t, ini_pos, tar_pos
		'''
		ini_pos: initial value
		tar_pos: maximum value
		self.cir_fre: frequency
		'''
		#T2
		return (ini_pos + tar_pos * math.sin(self.cir_fre*t))

#(above)------------Generate the desired motor position---------------

#(start)------------Impedance contollers---------
	def get_pos_diff(self):# angle difference, see Eq.(3)
		for i in range(self.dm.moto_num):
			'''
			self.dm.init_var[i]: initial motor position (i.e., 0 ~ 4095)
			self.dm.now_pos[i]: current motor position (i.e., 0 ~ 4095)
			self.dm.pos2rad[i]: ratio between radius and position

			self.pos_rad[i]: initial motor angle (i.e., -np.pi ~ np.pi)
			self.pos_diff[i]: angle difference
			'''
			#T3
			self.pos_rad[i] = (self.dm.now_pos[i] - self.dm.init_var[i])*self.dm.pos2rad[i]
			self.pos_diff[i] = self.pos_rad[i] - self.pos_des[i]
			

	def get_vel_diff(self):# velocity difference, see Eq.(3)
		for i in range(self.dm.moto_num):
			'''
			self.dm.now_vel[i]: velocity feedback (unit: rad/s)
			self.vel_des[i]: desired velocity

			self.vel_diff[i]: velocity difference
			'''

			#T4
			self.vel_diff[i] = self.dm.now_vel[i] - self.vel_des[i]

	def get_tra_diff(self):# tracking difference, see Eq.(3)
		for i in range(self.dm.moto_num):
			'''
			self.pos_diff[i]: angle difference
			self.vel_diff[i]: velocity difference

			self.tra_diff[i]: tracking error
			'''

			#T5
			self.tra_diff[i] = self.pos_diff[i] + self.beta*self.vel_diff[i]

	def get_coe(self):# adaptation scalar, see Eq.(9)
		for i in range(self.dm.moto_num):
			'''
			self.a and self.b: constants
			self.tra_diff[i]: tracking error

			self.co_diff[i]: adaptation scalar
			'''
			
			#T6
			self.co_diff[i] = self.a/(1.00 + self.b * self.tra_diff[i] * self.tra_diff[i])

	def controllers(self):# two impedance controllers
		if self.task == 'ada_imp':
			self.ada_impe()# adaptive impedance control
		else:
			self.const_impe()# constant impedance control

	def const_impe(self):# constant impedance control
		#need to update self.pos_diff[i] and self.vel_diff[i]
		
		#T7
		self.get_pos_diff()
		self.get_vel_diff()

		for i in range(self.dm.moto_num):
			'''
			self.cons_k: stiffness constant
			self.cons_d: damping constant
			self.k[i]: motor control stiffness parameter
			self.d[i]: motor control damping parameter
			self.ff[i]: control bias
			self.tau[i]: control output to the motor
			'''
			
			#T8
			self.k[i] = self.cons_k
			self.d[i] = self.cons_d
			self.ff[i] = 0.00
			print("The mechanical impedance parameters are: %f and %f" % (self.k[i], self.d[i]))
			self.tau[i] = -(self.cons_k*self.pos_diff[i] + self.cons_d*self.vel_diff[i])-self.ff[i]

			self.Tor2RealCur(i)
			print("At %f, torque, current, and position are: %f and %f, %f" % (self.n_t, self.tau[i], self.dm.con_cur[i], self.pos_rad[i]))

	def ada_impe(self):# adaptive impedance control
		#need to update self.pos_diff[i], self.vel_diff[i], self.tra_diff[i], and self.co_diff[i]

		#T9
		self.get_pos_diff()
		self.get_vel_diff()
		self.get_tra_diff()
		self.get_coe()

		for i in range(self.dm.moto_num):
			'''
			self.k[i]: motor control stiffness parameter
			self.d[i]: motor control damping parameter
			self.ff[i]: control bias
			self.tau[i]: control output to the motor
			'''

			#need online modulate impedance parameters self.ff[i], self.k[i], self.ff[i], see Eq.(8)

			#T10
			self.ff[i] = self.tra_diff[i]/self.co_diff[i]
			self.k[i] = self.ff[i]*self.pos_diff[i]
			self.d[i] = self.ff[i]*self.vel_diff[i]
			self.tau[i] = (-self.ff[i] - self.k[i] * self.pos_diff[i] - self.d[i] * self.vel_diff[i])

			self.dm.con_cur[i] = self.dm.tor2curcom(self.tau[i])
			self.dm.con_cur[i] = self.max_min_cur(self.dm.con_cur[i])
			if self.tor_out:
				self.tau[i] = self.dm.curcom2tor(self.dm.con_cur[i])
				print("Torque is in the limit")

			print("At %f, torque, current, and position are: %f and %f, %f" % (self.n_t, self.tau[i], self.dm.con_cur[i], self.pos_rad[i]))
#(above)------------Impedance contollers-----------

	def stop_motors(self):
		for i in range(self.dm.moto_num):
			print("stop motors at %f and the angle: %f" % (self.n_t, self.pos_rad[CHECK_ID]))

			if self.dm.moto_control == VEL_CONTROL:
				#for i in range(i):
				self.dm.con_vel[i] = 0
			elif self.dm.moto_control == POS_CONTROL:
				self.dm.con_vel[i] = self.dm.now_pos[i]
			else:
				self.dm.con_cur[i] = 0

		self.SendMotoComm()
	def open_files(self):
		plot_dir = './plots/'
		plot_dir = plot_dir + self.tra_type +'/' + self.task +'/'
		os.makedirs(plot_dir, exist_ok=True)
		self.t_f = open(plot_dir+'t.txt','w+')
		if self.task in ('ada_imp', 'const_imp'):#== 'ada_imp':
			self.tau_f = [open(plot_dir+'tau'+str(i)+'.txt', 'w+') for i in range(self.dm.moto_num)]
			self.k_f = [open(plot_dir+'k'+str(i)+'.txt', 'w+') for i in range(self.dm.moto_num)]
			self.d_f = [open(plot_dir+'d'+str(i)+'.txt', 'w+') for i in range(self.dm.moto_num)]
			#if self.task == 'ada_imp':
			self.ff_f = [open(plot_dir+'ff'+str(i)+'.txt', 'w+') for i in range(self.dm.moto_num)]
		self.pos_f = [open(plot_dir+'pos'+str(i)+'.txt', 'w+') for i in range(self.dm.moto_num)]
		self.vel_f = [open(plot_dir+'vel'+str(i)+'.txt', 'w+') for i in range(self.dm.moto_num)]
		self.cur_f = [open(plot_dir+'cur'+str(i)+'.txt', 'w+') for i in range(self.dm.moto_num)]
		self.cur4tor_f = [open(plot_dir+'cur4tor'+str(i)+'.txt', 'w+') for i in range(self.dm.moto_num)]
		self.des_pos_f = [open(plot_dir+'des_pos'+str(i)+'.txt', 'w+') for i in range(self.dm.moto_num)]
		self.des_vel_f = [open(plot_dir+'des_vel'+str(i)+'.txt', 'w+') for i in range(self.dm.moto_num)]
		self.dif_pos_f = [open(plot_dir+'dif_pos'+str(i)+'.txt', 'w+') for i in range(self.dm.moto_num)]
		self.dif_vel_f = [open(plot_dir+'dif_vel'+str(i)+'.txt', 'w+') for i in range(self.dm.moto_num)]

		self.ave_cur = [open(plot_dir+'ave_cur'+str(i)+'.txt', 'w+') for i in range(self.dm.moto_num)]
		self.ave_dif_pos = [open(plot_dir+'ave_dif_pos'+str(i)+'.txt', 'w+') for i in range(self.dm.moto_num)]
		self.ave_dif_vel = [open(plot_dir+'ave_dif_vel'+str(i)+'.txt', 'w+') for i in range(self.dm.moto_num)]
	def save_data(self):
		for i in range(self.dm.moto_num):
			if self.task in ('ada_imp', 'const_imp'):# == 'ada_imp':
				self.tau_f[i].write(str(self.tau[i])+'\n')
				self.k_f[i].write(str(self.k[i])+'\n')
				self.d_f[i].write(str(self.d[i])+'\n')
				#if self.task == 'ada_imp':
				self.ff_f[i].write(str(self.ff[i])+'\n')
			self.pos_f[i].write(str(self.pos_rad[i])+'\n')
			self.vel_f[i].write(str(self.dm.now_vel[i])+'\n')
			self.cur_f[i].write(str(self.dm.now_cur[i])+'\n')
			self.cur4tor_f[i].write(str(self.cur4tor[i])+'\n')
			self.des_pos_f[i].write(str(self.pos_des[i])+'\n')
			self.des_vel_f[i].write(str(self.vel_des[i])+'\n')

			self.dif_pos_f[i].write(str(self.pos_diff[i])+'\n')
			self.dif_vel_f[i].write(str(self.vel_diff[i])+'\n')
		self.t_f.write(str(self.n_t)+'\n')
	def close_files(self):
		for i in range(self.dm.moto_num):
			if self.task in ('ada_imp', 'const_imp'):# == 'ada_imp':
				self.tau_f[i].close()
				self.k_f[i].close()
				self.d_f[i].close()
				#if self.task == 'ada_imp':
				self.ff_f[i].close()
			self.pos_f[i].close()
			self.vel_f[i].close()
			self.cur_f[i].close()
			self.cur4tor_f[i].close()
			self.des_pos_f[i].close()
			self.des_vel_f[i].close()
			self.dif_pos_f[i].close()
			self.dif_vel_f[i].close()
			self.ave_cur[i].write(str(self.cur_ave[i])+'\n')
			self.ave_dif_pos[i].write(str(self.dif_pos_ave[i])+'\n')
			self.ave_dif_vel[i].write(str(self.dif_vel_ave[i])+'\n')
			self.ave_cur[i].close()
			self.ave_dif_pos[i].close()
			self.ave_dif_vel[i].close()
	def tor2vel(self, i):
		self.dm.con_vel[i] = int(((self.dt*self.tau[i]/self.ine) + self.dm.now_vel[i])/self.dm.velrpm)
		#print(self.dm.con_vel[i])
	def tor2pos(self):
		for i in range(self.dm.moto_num):
			self.dm.con_pos[i] = self.pos_des[i] + (self.tau[i] - self.kv * self.vel_diff[i])/self.kp
			print("At %f, torque and positions are: %3f and %3f" % (self.n_t, self.tau[i], self.dm.con_pos[i]), self.pos_des[i])
	def max_min_cur(self, var):
		rvar = 0
		if abs(var) > self.dm.MaxCur[0]:
			self.tor_out = True
			if var < 0:
				rvar = int(self.dm.MinCur[0]/self.cur_k)
				return rvar
			else:
				rvar = int(self.dm.MaxCur[0]/self.cur_k)
				return rvar
		else:
			self.tor_out = False
			return var
	def Tor2RealCur(self, i):
		self.dm.con_cur[i] = self.dm.tor2curcom(self.tau[i])
		self.dm.con_cur[i] = self.max_min_cur(self.dm.con_cur[i])
		if self.tor_out:
			self.tau[i] = self.dm.curcom2tor(self.dm.con_cur[i])
			print("Torque is in the limit")

	def SendMotoComm(self):
		if self.dm.moto_num > 1:
			if self.dm.moto_control == VEL_CONTROL:
				self.dm.syn_con(self.dm.gsw, LEN_PRO_GOAL_VELOCITY)
			elif self.dm.moto_control == POS_CONTROL:
				self.dm.syn_con(self.dm.gsw, LEN_PRO_GOAL_POSITION)
			else:
				self.dm.syn_con(self.dm.gsw, LEN_PRO_GOAL_CURRENT)
		else:
			if self.dm.moto_control == CUR_CONTROL:
				self.dm.sen_mc(self.dm.moto_ids[0], self.dm.con_cur[0])
			elif self.dm.moto_control == VEL_CONTROL:
				self.dm.sen_mc(self.dm.moto_ids[0], self.dm.con_vel[0])
			else:
				self.dm.sen_mc(self.dm.moto_ids[0], self.dm.con_pos[0])
	def CalFbAve(self):
		for i in range(self.dm.moto_num):
			n_pos_d = abs(self.pos_diff[i])#self.pos_diff[i]#
			n_vel_d = abs(self.vel_diff[i])#self.vel_diff[i]#
			n_cur = abs(self.dm.now_cur[i])
			if (self.t_s > 1):
				self.dif_pos_ave[i] = ((self.dif_pos_ave[i]*(self.t_s-1)) + n_pos_d)/self.t_s# + self.pos_diff[i])/self.t_s
				self.dif_vel_ave[i] = ((self.dif_vel_ave[i]*(self.t_s-1)) + n_vel_d)/self.t_s# + self.vel_diff[i])/self.t_s
				self.cur_ave[i] = ((self.cur_ave[i]*(self.t_s-1)) + n_cur)/self.t_s#+ self.dm.now_cur[i])/self.t_s
			else:
				self.dif_pos_ave[i] = n_pos_d#self.pos_diff[i]
				self.dif_vel_ave[i] = n_vel_d#self.vel_diff[i]
				self.cur_ave[i] = n_cur#self.dm.now_cur[i]

	def start_timer(self):
		self.s_t = datetime.now()
	def now_timer(self):
		self.diff_t = datetime.now() - self.s_t
		return (self.diff_t.seconds + self.diff_t.microseconds/1E6)
	def get_states(self):
		self.t_s = self.t_s + 1
		self.dm.get_feedbacks()

	def close(self):
		print("------------close----------")
		if (self.save_result):
			self.close_files()

		if self.dm.moto_num > 1:
			self.dm.pos_gsr.clearParam()
			self.dm.vel_gsr.clearParam()
			self.dm.cur_gsr.clearParam()
		for i in range(self.dm.moto_num):
			self.dm.en_tor[i] = False
		self.dm.tor_on_off()
		self.dm.port_hand.closePort()



if __name__ == '__main__':
	ac = Ada_con(co_mod = 0, re_only = True)
	# commenting the above line, using the follwing line if your USBToSerial port ID is not default (i.e., ttyUSB0)
	# ac = Ada_con(co_mod = 0, re_only = True, dn = '/dev/ttyUSB1') # In this case, USBToSerial port ID is ttyUSB1.
	ac.start()

	ac.close()
