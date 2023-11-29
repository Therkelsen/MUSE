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

#from dynamixel_sdk import *                    # Uses Dynamixel SDK library

#from dynamixel_sdk.port_handler import *

from dynamixel_sdk.port_handler import *
from dynamixel_sdk.packet_handler import *
from scipy import *

import copy
import os
import numpy as np
import time


print("setup done")

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
Con_Mode = ['current control', 'velocity control', 'NY', 'position control', 'extended position control', 'current-based position control']

POS_CONTROL = 3
VEL_CONTROL = 1
CUR_CONTROL = 0
CONTR_ID = POS_CONTROL# 0(current control), 3(position control)

# Control table address
ADDR_PRO_TORQUE_ENABLE      = 64
ADDR_PRO_GOAL_POSITION      = 116
ADDR_PRO_PRESENT_VELOCITY   = 128
ADDR_PRO_PRESENT_POSITION   = 132
ADDR_PRO_PRESENT_CURRENT   = 126
ADDR_PRO_MAX_CURRENT   = 38
ADDR_PRO_GOAL_CURRENT   = 102
ADDR_CON_MODE = 11

ADDR_PRO_GOAL_VELOCITY   = 104

# Data Byte Length
LEN_PRO_GOAL_POSITION       = 4
LEN_PRO_PRESENT_POSITION    = 4
LEN_PRO_PRESENT_VELOCITY    = 4
LEN_PRO_PRESENT_CURRENT    = 2
LEN_PRO_GOAL_CURRENT    = 2

LEN_PRO_GOAL_VELOCITY    = 4

PROTOCOL_VERSION            = 2.0               # See which protocol version is used in the Dynamixel

TORQUE_ENABLE               = 1                 # Value for enabling the torque
TORQUE_DISABLE              = 0                 # Value for disabling the torque

'''
see the performance graph in http://emanual.robotis.com/docs/en/dxl/x/xm430-w350/#control-table-of-eeprom-area
e.g., two points[torque(N.m), current(A)], [0.07,0.12] and [2.45, 1.5].
The relationship between motor torque (tau) and current (C) can be given by A*tau + B = C
A*0.07 + B = 0.12, A*2.45 + B = 1.5
A = (1.5 - 0.12)/(2.45-0.07) = 1.38/2.38
'''
A = 1.38/2.38
B = 1.5 - (2.45*1.38/2.38)#0.0794117647058824

Z = 0.1
UNITCUR = 2.69 * 0.001
RPM = 0.229*2*np.pi/60.0# 0.0239808239224021

BAUDRATE = 3000000#4000000#57600#
class Dyna_moto():
	def __init__(self, baudrate = BAUDRATE, devicename = 'COM3', protocolversion = 2.0, con_mode = POS_CONTROL, ro = False):
		self.bau_rate = baudrate
		self.dev_name = devicename
		self.prot_ver = protocolversion
		self.port_hand = PortHandler(self.dev_name)
		self.pack_hand = PacketHandler(self.prot_ver)
		self.ping_num = 50
		if self.port_hand.openPort():
			print("Succeeded to open the port")
		else:
			print("Failed to open the port")
			print("Press any key to terminate...")
			getch()
			quit()
		if self.port_hand.setBaudRate(self.bau_rate):
			print("Succeeded to change the baudrate")
			print("-------------------------------------")
		else:
			print("Failed to change the baudrate")
			print("Press any key to terminate...")
			getch()
			quit()
		self.moto_ids = self.get_motor_ids()
		print ("The found motor IDs are :", self.moto_ids)
		print("-------------------------------------")
		self.moto_num = len(self.moto_ids)
		if self.moto_num == 0:
			self.click2quit()
		

		if self.moto_num >1:
			self.pos_gsr = GroupSyncRead(self.port_hand, self.pack_hand, ADDR_PRO_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION)
			self.vel_gsr = GroupSyncRead(self.port_hand, self.pack_hand, ADDR_PRO_PRESENT_VELOCITY, LEN_PRO_PRESENT_VELOCITY)
			self.cur_gsr = GroupSyncRead(self.port_hand, self.pack_hand, ADDR_PRO_PRESENT_CURRENT, LEN_PRO_PRESENT_CURRENT)
			for i in range(self.moto_num):
				dxl_addparam_result = self.pos_gsr.addParam(self.moto_ids[i])
				if dxl_addparam_result != True:
					print("[ID:%03d] pos_groupSyncRead addparam failed" % self.moto_ids[i])
					quit()
				dxl_addparam_result = self.vel_gsr.addParam(self.moto_ids[i])
				if dxl_addparam_result != True:
					print("[ID:%03d] vel_groupSyncRead addparam failed" % self.moto_ids[i])
					quit()
				dxl_addparam_result = self.cur_gsr.addParam(self.moto_ids[i])
				if dxl_addparam_result != True:
					print("[ID:%03d] cur_groupSyncRead addparam failed" % self.moto_ids[i])
					quit()
			
			if con_mode == CUR_CONTROL:
				self.gsw = self.get_gsw(ADDR_PRO_GOAL_CURRENT, LEN_PRO_GOAL_CURRENT)
			elif con_mode == VEL_CONTROL:
				self.gsw = self.get_gsw(ADDR_PRO_GOAL_VELOCITY, LEN_PRO_GOAL_VELOCITY)
			else:
				self.gsw = self.get_gsw(ADDR_PRO_GOAL_POSITION, LEN_PRO_GOAL_POSITION)
		self.con_mode = np.zeros(self.moto_num, dtype = int)
		self.MinCur = np.zeros(self.moto_num)
		self.MaxCur = np.zeros(self.moto_num)
		self.MaxPos = np.zeros(self.moto_num)
		self.MinPos = np.zeros(self.moto_num)
		self.pos2rad = np.zeros(self.moto_num)

		self.MaxVel = np.zeros(self.moto_num)
		self.MinVel = np.zeros(self.moto_num)
		self.velrpm = RPM

		self.now_pos = np.zeros(self.moto_num)
		self.now_vel = np.zeros(self.moto_num)
		self.now_cur = np.zeros(self.moto_num)
		self.now_tor = np.zeros(self.moto_num)

		self.only_sense = ro

		self.en_tor = np.ones(self.moto_num, dtype = bool)

		'''
		if(self.only_sense):
			self.en_tor = np.zeros(self.moto_num, dtype = bool)
		else:
			self.en_tor = np.ones(self.moto_num, dtype = bool)
		'''

		self.ad_read = [11, 38, 48, 52,44]
		self.bynum_read = [1, 2, 4, 4, 4]
		#reading addresses and byte numbers of operating mode, current limit, max position limit, and min position limit
		self.paras = np.zeros((5, self.moto_num))

		self.con_cur = np.zeros(self.moto_num, dtype = int)
		self.con_pos = np.zeros(self.moto_num, dtype = int)
		self.con_vel = np.zeros(self.moto_num, dtype = int)

		self.con_cur_n = np.zeros(self.moto_num)

		self.moto_control = con_mode#CONTR_ID


		self.get_motor_paras()


		#print(self.paras)

		self.set_control_mode()
		self.get_motor_paras()

		self.tor_on_off()

		self.get_feedbacks()

		self.init_var = np.zeros(self.moto_num)

		self.init_var = copy.copy(self.now_pos)

		for i in range(self.moto_num):
			print("The initial position: %f" % self.init_var[i])

		self.con_pos = copy.copy(self.now_pos)

		


		#print (self.paras)

		#control parameters
		self.min_che_ang = np.pi*0.5
		self.man_che_ang = np.pi*1.5

		self.init_ang = np.pi
	def tor_on_off(self):
		for i in range(self.moto_num):
			if self.en_tor[i]:
				self.write(self.moto_ids[i], ADDR_PRO_TORQUE_ENABLE, 1, TORQUE_ENABLE)
				print("The motor# %d is torque-on." % self.moto_ids[i])
			else:
				self.write(self.moto_ids[i], ADDR_PRO_TORQUE_ENABLE, 1, TORQUE_DISABLE)
				print("The motor# %d is torque-off." % self.moto_ids[i])
	def get_gsw(self, add_write, len_write):
		return GroupSyncWrite(self.port_hand, self.pack_hand, add_write, len_write)
	def get_feedbacks(self):

		#time.sleep(0.01)
		'''
		self.get_pos()
		self.get_vel()
		self.get_cur_tor()
		'''
		if self.moto_num > 1:
			dxl_comm_result = self.pos_gsr.txRxPacket()
			if dxl_comm_result != COMM_SUCCESS:
				print("pos: %s" % self.pack_hand.getTxRxResult(dxl_comm_result))
			dxl_comm_result = self.vel_gsr.txRxPacket()
			if dxl_comm_result != COMM_SUCCESS:
				print("vel: %s" % self.pack_hand.getTxRxResult(dxl_comm_result))
			dxl_comm_result = self.cur_gsr.txRxPacket()
			if dxl_comm_result != COMM_SUCCESS:
				print("cur: %s" % self.pack_hand.getTxRxResult(dxl_comm_result))

			for i in range(self.moto_num):
				dxl_getdata_result = self.pos_gsr.isAvailable(self.moto_ids[i], ADDR_PRO_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION)
				if dxl_getdata_result != True:
					print("[ID:%03d] pos_groupSyncRead getdata failed" % self.moto_ids[i])
					quit()
				dxl_getdata_result = self.vel_gsr.isAvailable(self.moto_ids[i], ADDR_PRO_PRESENT_VELOCITY, LEN_PRO_PRESENT_VELOCITY)
				if dxl_getdata_result != True:
					print("[ID:%03d] vel_groupSyncRead getdata failed" % self.moto_ids[i])
					quit()
				dxl_getdata_result = self.cur_gsr.isAvailable(self.moto_ids[i], ADDR_PRO_PRESENT_CURRENT, LEN_PRO_PRESENT_CURRENT)
				if dxl_getdata_result != True:
					print("[ID:%03d] cur_groupSyncRead getdata failed" % self.moto_ids[i])
					quit()
				self.now_pos[i] = self.pos_gsr.getData(self.moto_ids[i], ADDR_PRO_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION)
				
				self.now_vel[i] = self.vel_gsr.getData(self.moto_ids[i], ADDR_PRO_PRESENT_VELOCITY, LEN_PRO_PRESENT_VELOCITY)
				self.now_vel[i] = self.byte2num(self.now_vel[i], 4)
				self.now_vel[i] = self.now_vel[i] * RPM

				self.now_cur[i] = self.cur_gsr.getData(self.moto_ids[i], ADDR_PRO_PRESENT_CURRENT, LEN_PRO_PRESENT_CURRENT)
				self.now_cur[i] = self.byte2num(self.now_cur[i], 2)
				self.now_cur[i] = self.now_cur[i] * UNITCUR
				self.now_tor[i] = self.cur2tor(self.now_cur[i])
			if (self.only_sense):
				print("The sensed positions are ", self.now_pos)
				#print("The sensed velocities are ", self.now_vel)
				#print("The sensed currents are ", self.now_cur)
				#print("The sensed torques are ", self.now_tor)
		else:
			self.get_pos()
			self.get_vel()
			self.get_cur_tor()
		
	def get_pos(self):
		for i in range(self.moto_num):
			self.now_pos[i] = self.read(self.moto_ids[i], ADDR_PRO_PRESENT_POSITION, 4)
	def get_vel(self):
		for i in range(self.moto_num):
			vel = self.read(self.moto_ids[i], ADDR_PRO_PRESENT_VELOCITY, 4)
			vel = self.byte2num(vel, 4)
			self.now_vel[i] = vel*RPM
	def get_cur_tor(self):
		for i in range(self.moto_num):
			cur = self.read(self.moto_ids[i], ADDR_PRO_PRESENT_CURRENT, 2)	
			cur = self.byte2num(cur, 2)
			self.now_cur[i] = cur * UNITCUR
			self.now_tor[i] = self.cur2tor(self.now_cur[i])
	def byte2num(self, var, byte_num):
		rvar = 0.00
		if byte_num == 4:
			if var > 0x7fffffff:
				rvar = var - 0xffffffff - 1
			else:
				rvar = var
		elif byte_num == 2:
			if var > 0x7fff:
				rvar = var - 0xffff - 1
			else:
				rvar = var
		else:
			rvar = var
		return rvar
	def set_control_mode(self):
		for i in range(self.moto_num):
			#print(self.con_mode[i], self.moto_control)
			if self.con_mode[i] != self.moto_control:
				self.write(self.moto_ids[i], ADDR_CON_MODE, 1, self.moto_control)
				print("The control mode of the motor %3d is changed into %s " % (self.moto_ids[i], Con_Mode[self.moto_control]))
	def cur2tor(self, var):
		rvar = var/A#(var -B)/A
		return rvar
	def tor2curcom(self, var):
		rvar = 0
		rvar = A*var# + B
		rvar = round(rvar/UNITCUR)

		return rvar
	def curcom2tor(self, var):
		return (var*UNITCUR/A)

	def pos2ang(self, posi, maxposi, minposi):
		return(2*np.pi*(posi-minposi)/(maxposi-minposi))
	def ang2pos(self, angl, maxposi, minposi):
		return (minposi+(maxposi-minposi)*angl/(2*np.pi))
	def get_motor_ids(self):
		motor_ids = []
		for i in range(self.ping_num):
			dxl_model_number, dxl_comm_result, dxl_error = self.pack_hand.ping(self.port_hand, i)
			if dxl_comm_result != COMM_SUCCESS:
				n=0
			elif dxl_error != 0:
				n=0
			else:
				#print("The motor ID:%03d is found. Dynamixel model number : %d" % (i,dxl_model_number))#DXL_ID, dxl_model_number))
				motor_ids.append(i)
		return motor_ids
	def get_motor_paras(self):
		for i in range(len(self.ad_read)):
			for j in range(self.moto_num):
				self.paras[i, j] = self.read(self.moto_ids[j], self.ad_read[i], self.bynum_read[i])
				#print(self.paras[i, j])
		for i in range(self.moto_num):
			self.con_mode[i] = self.paras[0,i]
			self.MinCur[i] = -self.paras[1,i]
			self.MaxCur[i] = self.paras[1,i]
			self.MaxPos[i] = self.paras[2,i]
			self.MinPos[i] = self.paras[3,i]
			self.pos2rad[i] = 2*np.pi/(self.MaxPos[i] - self.MinPos[i])
			self.MaxVel[i] = self.paras[4,i]
			self.MinVel[i] = -self.paras[4,i]
			print("The motor# %d is in the %s mode." % (self.moto_ids[i], Con_Mode[self.con_mode[i]]))
			print("The maximum and minimum positions are: %f and %f" %(self.MaxPos[i], self.MinPos[i]))
			print("The maximum and minimum currents are: %f and %f" %(self.MaxCur[i], self.MinCur[i]))

	def read(self, motor_id, add_read, byte_num):
		assert (byte_num in [1,2,4]), "the reading byte should be one of [1, 2, 4]"
		if (byte_num == 1):
			cl_dxl, cl_dxl_comm_result, cl_dxl_error = self.pack_hand.read1ByteTxRx(self.port_hand, motor_id, add_read)
		elif (byte_num == 2):
			cl_dxl, cl_dxl_comm_result, cl_dxl_error = self.pack_hand.read2ByteTxRx(self.port_hand, motor_id, add_read)
		else:
			cl_dxl, cl_dxl_comm_result, cl_dxl_error = self.pack_hand.read4ByteTxRx(self.port_hand, motor_id, add_read)
		if cl_dxl_comm_result != COMM_SUCCESS:
			print("%s" % self.pack_hand.getTxRxResult(cl_dxl_comm_result))
		elif cl_dxl_error != 0:
			print("%s" % self.pack_hand.getRxPacketError(cl_dxl_error))
		else:
			return cl_dxl
	def syn_write(self, gsw, motor_id, byte_num, goal):
		assert (byte_num in [2,4]), "the reading byte should be one of [2, 4]"
		goal = int(goal)#only accept int
		#print (goal)
		if byte_num == 4:
			goal_var = [DXL_LOBYTE(DXL_LOWORD(goal)), DXL_HIBYTE(DXL_LOWORD(goal)), DXL_LOBYTE(DXL_HIWORD(goal)), DXL_HIBYTE(DXL_HIWORD(goal))]
		else:
			goal_var = [DXL_LOBYTE(goal), DXL_HIBYTE(goal)]
		dxl_addparam_result = gsw.addParam(motor_id, goal_var)
		if dxl_addparam_result != True:
			print("[ID:%03d] groupSyncWrite addparam failed" % motor_id)
			quit()
	def syn_con(self, gsw, byte_num):
		for i in range(self.moto_num):
			if self.con_mode[i] == POS_CONTROL:
				self.syn_write(gsw, self.moto_ids[i], byte_num, self.con_pos[i])
			elif self.con_mode[i] == VEL_CONTROL:
				self.syn_write(gsw, self.moto_ids[i], byte_num, self.con_vel[i])
			else:
				self.con_cur_n[i] = self.con_cur[i] * UNITCUR#20190611
				self.syn_write(gsw, self.moto_ids[i], byte_num, self.con_cur[i])

		# Syncwrite goal position
		dxl_comm_result = gsw.txPacket()
		if dxl_comm_result != COMM_SUCCESS:
			print("%s" % self.pack_hand.getTxRxResult(dxl_comm_result))
		gsw.clearParam()

	def write(self, motor_id, add_write, byte_num, comm):
		assert (byte_num in [1,2,4]), "the writting byte should be one of [1, 2, 4]"
		comm = int(comm)
		if (byte_num == 1):
			dxl_comm_result, dxl_error = self.pack_hand.write1ByteTxRx(self.port_hand, motor_id, add_write, comm)
		elif (byte_num == 2):
			dxl_comm_result, dxl_error = self.pack_hand.write2ByteTxRx(self.port_hand, motor_id, add_write, comm)
		else:
			dxl_comm_result, dxl_error = self.pack_hand.write4ByteTxRx(self.port_hand, motor_id, add_write, comm)
		if dxl_comm_result != COMM_SUCCESS:
			print("%s" % self.pack_hand.getTxRxResult(dxl_comm_result))
		elif dxl_error != 0:
			print("%s" % self.pack_hand.getRxPacketError(dxl_error))
	def sen_mc(self, m_id, c_m):
		if self.moto_control == CUR_CONTROL:
			self.write(m_id, ADDR_PRO_GOAL_CURRENT, LEN_PRO_GOAL_CURRENT, c_m)
		elif self.moto_control == VEL_CONTROL:
			self.write(m_id, ADDR_PRO_GOAL_VELOCITY, LEN_PRO_GOAL_VELOCITY, c_m)
		else:
			self.write(m_id, ADDR_PRO_GOAL_POSITION, LEN_PRO_GOAL_POSITION, c_m)

	def click2quit(self):
		print("Press any key to terminate...")
		getch()
		quit()

