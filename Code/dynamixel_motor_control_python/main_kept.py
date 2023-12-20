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
import keyboard
import math
import numpy as np
import pandas as pd
import threading
import time

from datetime import datetime
from keras.models import load_model

# Ignore warnings
import warnings
warnings.filterwarnings("ignore")

DXL_MOVING_STATUS_THRESHOLD = 20
import os
if os.name == 'nt':
	import msvcrt

	def getch():
		return msvcrt.getch().decode()
else:
	import sys
	import tty
	import termios
	fd = sys.stdin.fileno()
	old_settings = termios.tcgetattr(fd)

	def getch():
		try:
			tty.setraw(sys.stdin.fileno())
			ch = sys.stdin.read(1)
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
		return ch

MinPos = 300 # 200
MaxPos = 2350 # 1200

MinCur = -10
MaxCur = 10

POS_CONTROL = 3
VEL_CONTROL = 1
CUR_CONTROL = 0

# Data Byte Length
LEN_PRO_GOAL_POSITION = 4
LEN_PRO_PRESENT_POSITION = 4
LEN_PRO_PRESENT_VELOCITY = 4
LEN_PRO_PRESENT_CURRENT = 2
LEN_PRO_GOAL_CURRENT = 2

LEN_PRO_GOAL_VELOCITY = 4

MidPos0 = 1327
MidPos1 = 746
# The middle positions of two motors are  [1327, 746]

CHECK_ID = 0
CHECK_CUR_NUM = 6
BAUDRATE = 3000000 # 4000000 # 57600

CONTROLLER = 'ada_imp' # 'const_imp' # 'ada_imp'
TASK = 'track' # 'post_con' # 'dynamic' # 'track'


class Ada_con():
	def __init__(self, con_type='impe_con', co_mod=3, re_only=False, dn='COM3'):
		self.dm = Dm.Dyna_moto(baudrate=BAUDRATE, devicename=dn, con_mode=co_mod, ro=re_only)

		self.num_moto = self.dm.moto_num

		# Position angle and velocity feedback obtained from the motor
		self.pos_rad = np.zeros(self.num_moto)
		self.vel_rad = np.zeros(self.num_moto)

		# Desired position and velocity
		self.pos_des = np.zeros(self.num_moto)
		self.vel_des = np.zeros(self.num_moto)

		# Position and velocity differences
		self.pos_diff = np.zeros(self.dm.moto_num)
		self.vel_diff = np.zeros(self.dm.moto_num)
		self.tra_diff = np.zeros(self.dm.moto_num)
		self.co_diff = np.zeros(self.dm.moto_num)

		# Torque outputs
		self.tau = np.zeros(self.dm.moto_num)

		# Impedance parameters: stiffness, damping, and bias
		self.k = np.zeros(self.dm.moto_num)
		self.d = np.zeros(self.dm.moto_num)
		self.ff = np.zeros(self.dm.moto_num)

		# Constant impedance controller
		self.cons_k = 0.04 # 1.0 # 0.1 # 0.05
		self.cons_d = math.sqrt(self.cons_k) # 0.001

		self.cur4tor = np.zeros(self.num_moto)
		self.pre_pos_des = np.zeros(self.num_moto)

		self.task = CONTROLLER # 'const_imp' # 'ada_imp'
		self.tra_type = TASK # 'track' # 'post_con'

		self.max_noi = np.pi / 10.0 # Potential change if it limits the range of motion

		self.safe_rad = 0.0 # Potential change if it limits the range of motion np.pi/2.0  + self.max_noi

		# Program time. TASK gets set before program start. default = 'track'
		if self.tra_type == 'track':
			self.go_t = 30 # 15.0 # 33.0 # 51.0 # 5.0 # 50.0 # 160.0 # 15.0 # 20.0
		else:
			self.go_t = 10.0 # 20.0 # 8.0 # 15.0 # 20.0 # 50.0 # 160.0

		# tracking
		self.max_tar_rad = -np.pi / 1.5 # np.pi / 2.0 # np.pi / 6.0 # np.pi / 4.0
		self.min_tar_rad = 0.0

		self.cir_num = 3
		self.cir_fre = self.cir_num * 2 * np.pi / self.go_t
		self.tra_pos = 0.00

		self.goal_theta = np.pi / 2.0 # 10.0

		self.n_t = 0.00
		self.dt = 0.00
		self.pre_t = 0.00

		self.target_pos = self.goal_theta
		self.t_s = 0

		self.beta = 0.05 # 1.0 # 2.0 # 5.0
		self.a = 35 # 0.2
		self.b = 5.0
		self.ine = 0.1 # 0.05 # 1

		self.tor_out = False

		self.kp = 100
		self.kv = math.sqrt(self.kp)
		self.cur_k = 60

		self.dif_pos_ave = np.zeros(self.dm.moto_num)
		self.dif_vel_ave = np.zeros(self.dm.moto_num)
		self.cur_ave = np.zeros(self.dm.moto_num)

		# variable impedance
		self.pre_dif_pos = np.zeros(self.num_moto)
		self.pre_dif_vel = np.zeros(self.num_moto)
		self.pre_des_pos = np.zeros(self.num_moto)

		self.save_result = True
		if (self.save_result):
			self.open_files()

		self.cur_pos = 0.0
		self.max_pos = 0.0

		# Loads the neural network model
		self.model_path = 'Code/GRU_network/first_16_feat_10ts_200ep_no_kin.h5'
		self.model = read_nn_model(self.model_path)

		# Loads csv "data_base"
		self.csv_database_path = 'Code/GRU_network/test_samples.csv'
		self.df_data_base = load_csv_data(self.csv_database_path)

		# Loads means and standard deviations for scaling
		self.mean_path = 'Code/GRU_network/means.csv'
		self.std_path = 'Code/GRU_network/std_devs.csv'

		# Defines the sample length pr prediction
		self.sample_columns = ['Sample', 'JointAngle', 'Mass', 'EIMMagnitude', 'EIMPhase', 'RollingAverageMag',
								'RollingAveragePhase', 'MedianEIMMagnitude', 'MedianEIMPhase',
								'MeanEIMMagnitude', 'MeanEIMPhase', 'StdEIMMagnitude',
								'StdEIMPhase', 'VarEIMMagnitude', 'VarEIMPhase', 'KurtEIMMagnitude',
								'KurtEIMPhase', 'ROCEIMMagnitude', 'ROCEIMPhase']
		self.sample_length = 250
		self.sample_upper_limit = 250
		self.sample_count = 0
		self.sample = pd.DataFrame(columns=self.sample_columns)
		self.sample_normalized = pd.DataFrame(columns=self.sample_columns)
		self.sequence_length = 10
		self.num_features = 16
		self.num_targets = 2
		self.X_seq = np.zeros((1, self.sequence_length, self.num_features))
		self.y_seq = np.zeros((1, self.sequence_length, self.num_targets))

		# Thresholds
		self.threshold_pos_min = self.max_tar_rad
		self.threshold_pos_max = 0.0
		self.delta_target_pos_thresh = 0.0

	def start(self):
		self.start_timer()
		self.get_states()
		self.get_pos_diff()
		self.max_pos = 360.0 * np.pi / 180.0
		print("The maximum position is: %f rad" % self.max_tar_rad)
		self.cur_pos = ((self.dm.init_pos / 4095) * 360.0 * np.pi / 180.0) - 3.938690
		print("The initial position is: %f rad" % self.cur_pos)
		self.min_tar_rad = self.max_tar_rad
		self.safe_rad = ((2566 / 4095) * 360.0 * np.pi / 180.0) - 3.938690

		while True:
			# Check if any key is pressed
			if keyboard.is_pressed(hotkey='q'):
				print("Keyboard interrupt")
				break

			self.sample = self.read_from_database()

			if len(self.sample) <= self.sequence_length:
				print("Not enough samples in database.")
				exit()

			self.sample_normalized = normalize_data(self.sample, self.mean_path, self.std_path)
			self.X_seq, self.y_seq = create_sequences(self.sample_normalized, self.sequence_length)
			self.predictions = predict(self.model, self.X_seq)

			self.predictions_denorm = denormalize_data(self.predictions, self.mean_path, self.std_path)

			pred = self.predictions_denorm['JointAngle'].iloc[-1]
			print("Predicted joint angle:\n %f deg" % -pred)
			ref = 0.0
			print("input to deg_to_rad:" + str(pred))
			ref = self.deg_to_rad(pred)
			print("output from deg_to_rad:" + str(ref))
			ref = ref * (-1)
			print(" %f rad" % ref)
			if (ref - self.cur_pos < self.delta_target_pos_thresh):
				print("Updating reference")
				self.target_pos = ref
			if (ref < self.min_tar_rad):
				print("Reference is too low, clamping to " + str(self.min_tar_rad) + " rad")
				ref = self.min_tar_rad
			elif (ref > self.safe_rad):
				print("Reference is too high, clamping to " + str(self.safe_rad) + " rad")
				ref = self.safe_rad

			self.pos_des[0] = self.tra_plan(self.n_t, self.cur_pos, ref)
			diff = abs(self.pos_des[0] - self.cur_pos)

			while (diff > 0.50):
				if keyboard.is_pressed(hotkey='q'):
					print("Keyboard interrupt")
					break
				self.n_t = self.now_timer()
				self.dt = self.n_t - self.pre_t

				# Get position and velocity feedbacks from the motor
				self.get_states()

				# Generate the desired motor position
				self.gen_des()

				# Impedance controllers
				self.controllers()

				# Send commands to the motor
				self.SendMotoComm()

				# self.CalFbAve()

				# Create a new thread object for each iteration
				my_thread = MyThread()

				# Start the thread
				my_thread.start()

				# Wait for the thread to finish
				my_thread.join()

				print("Main loop continues...")

				self.cur_pos = ((self.dm.now_pos[0] / 4095) * 360.0 * np.pi / 180.0) - 3.938690

				self.pos_des[0] = self.tra_plan(self.n_t, self.cur_pos, ref)

				diff -= abs(self.cur_pos)

				# if (self.cur_pos > self.safe_rad):
				# 	self.stop_motors()
				# 	break

				# if (self.save_result):
				# 	self.save_data()
			self.stop_motors()

# (start)------------Generate the desired motor position-------------
	def gen_des(self):
		for i in range(self.num_moto):
			# if self.tra_type == 'track':		# periodic tracking
			# 	self.cur_pos = 0.00
			# 	self.target_pos = self.target_pos

			if self.dt > 0.00:		# calculate the desired velocity
				self.vel_des[i] = (self.pos_des[i] - self.pre_pos_des[i]) / self.dt
			else:
				self.vel_des[i] = self.vel_des[i]

			self.pre_pos_des[i] = self.pos_des[i]
			self.cur4tor[i] = self.dm.now_tor[i]
		self.pre_t = copy.copy(self.n_t)

	def tra_plan(self, t, ini_pos, tar_pos):
		# two desired position generators
		if self.tra_type == 'track': # 'dynamic' 'track'
			return self.pla_tra(t, ini_pos, tar_pos)# periodic tracking
		else:
			return self.pla_postu_con(t, ini_pos, tar_pos)# posture control

	# posture control
	def pla_postu_con(self, t, ini_pos, tar_pos):
		# keep initial motor angle without respect to t, ini_pos, tar_pos
		# T1
		return 0.00

	# periodic tracking
	def pla_tra(self, t, ini_pos, tar_pos):
		# generate the periodic function math.sin with respect to t, ini_pos, tar_pos
		'''
		ini_pos: initial value
		tar_pos: maximum value
		self.cir_fre: frequency
		'''
		# T2
		# return (ini_pos + tar_pos * math.sin(self.cir_fre*t))
		return (tar_pos - ini_pos)

	def read_from_database(self):
		# Loads csv "data_base"
		sample = pd.DataFrame(columns=self.sample_columns)
		sample[self.sample_columns] = self.df_data_base[self.sample_columns].iloc[self.sample_count:self.sample_upper_limit].copy()
		self.sample_upper_limit += self.sample_length
		self.sample_count += self.sample_length

		return sample

	def deg_to_rad(self, deg):
		return deg * np.pi / 180.0

# (above)------------Generate the desired motor position---------------

# (start)------------Impedance controllers---------
	# angle difference, see Eq.(3)
	def get_pos_diff(self):
		for i in range(self.dm.moto_num):
			'''
			self.dm.init_var[i]: initial motor position (i.e., 0 ~ 4095)
			self.dm.now_pos[i]: current motor position (i.e., 0 ~ 4095)
			self.dm.pos2rad[i]: ratio between radius and position

			self.pos_rad[i]: initial motor angle (i.e., -np.pi ~ np.pi)
			self.pos_diff[i]: angle difference
			'''
			# T3
			self.pos_rad[i] = (self.dm.now_pos[i] - self.dm.init_var[i]) * self.dm.pos2rad[i]
			self.pos_diff[i] = self.pos_rad[i] - self.pos_des[i]

	# velocity difference, see Eq.(3)
	def get_vel_diff(self):
		for i in range(self.dm.moto_num):
			'''
			self.dm.now_vel[i]: velocity feedback (unit: rad/s)
			self.vel_des[i]: desired velocity

			self.vel_diff[i]: velocity difference
			'''

			# T4 self.vel_des[i]
			self.vel_diff[i] = self.dm.now_vel[i] - self.vel_des[i]

	# tracking difference, see Eq.(3)
	def get_tra_diff(self):
		for i in range(self.dm.moto_num):
			'''
			self.pos_diff[i]: angle difference
			self.vel_diff[i]: velocity difference

			self.tra_diff[i]: tracking error
			'''

			# T5
			self.tra_diff[i] = self.pos_diff[i] + self.beta * self.vel_diff[i]

	# adaptation scalar, see Eq.(9)
	def get_coe(self):
		for i in range(self.dm.moto_num):
			'''
			self.a and self.b: constants
			self.tra_diff[i]: tracking error

			self.co_diff[i]: adaptation scalar
			'''

			# T6
			self.co_diff[i] = self.a / (1.00 + self.b * self.tra_diff[i] * self.tra_diff[i])

	# two impedance controllers
	def controllers(self):
		if self.task == 'ada_imp':
			self.ada_impe()# adaptive impedance control
		else:
			self.const_impe()# constant impedance control

	# constant impedance control
	def const_impe(self):
		# need to update self.pos_diff[i] and self.vel_diff[i]
		# T7
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

			# T8
			self.k[i] = self.cons_k
			self.d[i] = self.cons_d
			self.ff[i] = 0.00
			print("The mechanical impedance parameters are: %f and %f" % (self.k[i], self.d[i]))
			self.tau[i] = -(self.cons_k * self.pos_diff[i] + self.cons_d * self.vel_diff[i]) - self.ff[i]

			self.Tor2RealCur(i)
			print("At %f, torque, current, and position are: %f and %f, %f" % (self.n_t, self.tau[i], self.dm.con_cur[i], self.pos_rad[i]))

	# adaptive impedance control
	def ada_impe(self):
		# need to update self.pos_diff[i], self.vel_diff[i], self.tra_diff[i], and self.co_diff[i]
		# T9
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

			# need online modulate impedance parameters self.ff[i], self.k[i], self.ff[i], see Eq.(8)
			# T10
			self.ff[i] = self.tra_diff[i] / self.co_diff[i]
			self.k[i] = self.ff[i] * self.pos_diff[i]
			self.d[i] = self.ff[i] * self.vel_diff[i]
			self.tau[i] = (-self.ff[i] - self.k[i] * self.pos_diff[i] - self.d[i] * self.vel_diff[i])

			self.dm.con_cur[i] = self.dm.tor2curcom(self.tau[i])
			self.dm.con_cur[i] = self.max_min_cur(self.dm.con_cur[i])
			if self.tor_out:
				self.tau[i] = self.dm.curcom2tor(self.dm.con_cur[i])
				print("Torque is in the limit")

			print("At %f, torque, current, and position are: %f and %f, %f" % (self.n_t, self.tau[i], self.dm.con_cur[i], self.pos_rad[i]))

# (above)------------Impedance controllers-----------
	def stop_motors(self):
		for i in range(self.dm.moto_num):
			print("stop motors at %f and the angle: %f" % (self.n_t, self.pos_rad[CHECK_ID]))

			if self.dm.moto_control == VEL_CONTROL:
				# for i in range(i):
				self.dm.con_vel[i] = 0
			elif self.dm.moto_control == POS_CONTROL:
				self.dm.con_vel[i] = self.dm.now_pos[i]
			else:
				self.dm.con_cur[i] = 0

		self.SendMotoComm()

	def open_files(self):
		plot_dir = './plots/'
		plot_dir = plot_dir + self.tra_type + '/' + self.task + '/'
		os.makedirs(plot_dir, exist_ok=True)
		self.t_f = open(plot_dir + 't.txt', 'w+')
		if self.task in ('ada_imp', 'const_imp'): # == 'ada_imp':
			self.tau_f = [open(plot_dir + 'tau' + str(i) + '.txt', 'w+') for i in range(self.dm.moto_num)]
			self.k_f = [open(plot_dir + 'k' + str(i) + '.txt', 'w+') for i in range(self.dm.moto_num)]
			self.d_f = [open(plot_dir + 'd' + str(i) + '.txt', 'w+') for i in range(self.dm.moto_num)]
			# if self.task == 'ada_imp':
			self.ff_f = [open(plot_dir + 'ff' + str(i) + '.txt', 'w+') for i in range(self.dm.moto_num)]
		self.pos_f = [open(plot_dir + 'pos' + str(i) + '.txt', 'w+') for i in range(self.dm.moto_num)]
		self.vel_f = [open(plot_dir + 'vel' + str(i) + '.txt', 'w+') for i in range(self.dm.moto_num)]
		self.cur_f = [open(plot_dir + 'cur' + str(i) + '.txt', 'w+') for i in range(self.dm.moto_num)]
		self.cur4tor_f = [open(plot_dir + 'cur4tor' + str(i) + '.txt', 'w+') for i in range(self.dm.moto_num)]
		self.des_pos_f = [open(plot_dir + 'des_pos' + str(i) + '.txt', 'w+') for i in range(self.dm.moto_num)]
		self.des_vel_f = [open(plot_dir + 'des_vel' + str(i) + '.txt', 'w+') for i in range(self.dm.moto_num)]
		self.dif_pos_f = [open(plot_dir + 'dif_pos' + str(i) + '.txt', 'w+') for i in range(self.dm.moto_num)]
		self.dif_vel_f = [open(plot_dir + 'dif_vel' + str(i) + '.txt', 'w+') for i in range(self.dm.moto_num)]

		self.ave_cur = [open(plot_dir + 'ave_cur' + str(i) + '.txt', 'w+') for i in range(self.dm.moto_num)]
		self.ave_dif_pos = [open(plot_dir + 'ave_dif_pos' + str(i) + '.txt', 'w+') for i in range(self.dm.moto_num)]
		self.ave_dif_vel = [open(plot_dir + 'ave_dif_vel' + str(i) + '.txt', 'w+') for i in range(self.dm.moto_num)]

	def save_data(self):
		for i in range(self.dm.moto_num):
			if self.task in ('ada_imp', 'const_imp'): # == 'ada_imp':
				self.tau_f[i].write(str(self.tau[i]) + '\n')
				self.k_f[i].write(str(self.k[i]) + '\n')
				self.d_f[i].write(str(self.d[i]) + '\n')
				# if self.task == 'ada_imp':
				self.ff_f[i].write(str(self.ff[i]) + '\n')
			self.pos_f[i].write(str(self.pos_rad[i]) + '\n')
			self.vel_f[i].write(str(self.dm.now_vel[i]) + '\n')
			self.cur_f[i].write(str(self.dm.now_cur[i]) + '\n')
			self.cur4tor_f[i].write(str(self.cur4tor[i]) + '\n')
			self.des_pos_f[i].write(str(self.pos_des[i]) + '\n')
			self.des_vel_f[i].write(str(self.vel_des[i]) + '\n')

			self.dif_pos_f[i].write(str(self.pos_diff[i]) + '\n')
			self.dif_vel_f[i].write(str(self.vel_diff[i]) + '\n')
		self.t_f.write(str(self.n_t) + '\n')

	def close_files(self):
		for i in range(self.dm.moto_num):
			if self.task in ('ada_imp', 'const_imp'): # == 'ada_imp':
				self.tau_f[i].close()
				self.k_f[i].close()
				self.d_f[i].close()
				# if self.task == 'ada_imp':
				self.ff_f[i].close()
			self.pos_f[i].close()
			self.vel_f[i].close()
			self.cur_f[i].close()
			self.cur4tor_f[i].close()
			self.des_pos_f[i].close()
			self.des_vel_f[i].close()
			self.dif_pos_f[i].close()
			self.dif_vel_f[i].close()
			self.ave_cur[i].write(str(self.cur_ave[i]) + '\n')
			self.ave_dif_pos[i].write(str(self.dif_pos_ave[i]) + '\n')
			self.ave_dif_vel[i].write(str(self.dif_vel_ave[i]) + '\n')
			self.ave_cur[i].close()
			self.ave_dif_pos[i].close()
			self.ave_dif_vel[i].close()

	def tor2vel(self, i):
		self.dm.con_vel[i] = int(((self.dt * self.tau[i] / self.ine) + self.dm.now_vel[i]) / self.dm.velrpm)
		# print(self.dm.con_vel[i])

	def tor2pos(self):
		for i in range(self.dm.moto_num):
			self.dm.con_pos[i] = self.pos_des[i] + (self.tau[i] - self.kv * self.vel_diff[i]) / self.kp
			print("At %f, torque and positions are: %3f and %3f" % (self.n_t, self.tau[i], self.dm.con_pos[i]), self.pos_des[i])

	def max_min_cur(self, var):
		rvar = 0
		if abs(var) > self.dm.MaxCur[0]:
			self.tor_out = True
			if var < 0:
				rvar = int(self.dm.MinCur[0] / self.cur_k)
				return rvar
			else:
				rvar = int(self.dm.MaxCur[0] / self.cur_k)
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
			n_pos_d = abs(self.pos_diff[i]) # self.pos_diff[i]#
			n_vel_d = abs(self.vel_diff[i]) # self.vel_diff[i]#
			n_cur = abs(self.dm.now_cur[i])
			if (self.t_s > 1):
				self.dif_pos_ave[i] = ((self.dif_pos_ave[i] * (self.t_s - 1)) + n_pos_d) / self.t_s # + self.pos_diff[i])/self.t_s
				self.dif_vel_ave[i] = ((self.dif_vel_ave[i] * (self.t_s - 1)) + n_vel_d) / self.t_s # + self.vel_diff[i])/self.t_s
				self.cur_ave[i] = ((self.cur_ave[i] * (self.t_s - 1)) + n_cur) / self.t_s # + self.dm.now_cur[i])/self.t_s
			else:
				self.dif_pos_ave[i] = n_pos_d # self.pos_diff[i]
				self.dif_vel_ave[i] = n_vel_d # self.vel_diff[i]
				self.cur_ave[i] = n_cur # self.dm.now_cur[i]

	def start_timer(self):
		self.s_t = datetime.now()

	def now_timer(self):
		self.diff_t = datetime.now() - self.s_t	# Calculates the time difference
		return (self.diff_t.seconds + self.diff_t.microseconds / 1E6)

	def get_states(self):
		self.t_s = self.t_s + 1	# Time step counter?
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


# (start)------------Neural network-------------
def read_nn_model(nn_model_path):
	# Load the model with custom_objects to recognize the GRU layer
	loaded_model = load_model(nn_model_path)

	print("Model loaded successfully.")
	print(loaded_model.summary())
	return loaded_model


def load_csv_data(csv_path):
	return pd.read_csv(csv_path, encoding='utf-8')


def create_sequences(dataframe, sequence_length=10):
	X_seq, y_seq = [], []

	df_grouped_test = dataframe.groupby('Sample')

	for groupname, group_data in df_grouped_test:
		group_data_temp = group_data[['EIMMagnitude', 'EIMPhase', 'RollingAverageMag',
									'RollingAveragePhase', 'MedianEIMMagnitude', 'MedianEIMPhase',
									'MeanEIMMagnitude', 'MeanEIMPhase', 'StdEIMMagnitude',
									'StdEIMPhase', 'VarEIMMagnitude', 'VarEIMPhase', 'KurtEIMMagnitude',
									'KurtEIMPhase', 'ROCEIMMagnitude', 'ROCEIMPhase']]

		group_data_x = np.array(group_data_temp)

		group_data_temp = group_data[['JointAngle', 'Mass']]
		group_data_y = np.array(group_data_temp)

		# Create sequences (adjust sequence_length as needed)
		for i in range(len(group_data) - sequence_length + 1):
			X_seq.append(group_data_x[i:i + sequence_length, :])
			y_seq.append(group_data_y[i + sequence_length - 1, :])

	return np.array(X_seq), np.array(y_seq)


def predict(model, X_seq, y_seq=None):
	# Predict on test data
	# Now you can use the new_model for predictions
	predictions_scaled = model.predict(X_seq)

	if (y_seq is not None):
		# Evaluate the model on the test set.
		model.evaluate(X_seq, y_seq)

	# Isolate the needed means and standard deviations for reversing the scale
	return pd.DataFrame(predictions_scaled, columns=['JointAngle', 'Mass'])


def normalize_data(dataframe, mean_path, std_path):
	# Load the mean and standard deviation of the training data
	loaded_means = pd.read_csv(mean_path, index_col=0, squeeze=True)
	loaded_std_devs = pd.read_csv(std_path, index_col=0, squeeze=True)

	sample_column = dataframe['Sample'].values
	df_test = dataframe.drop(['Sample'], axis=1)

	# Normalize the test data
	df_test_normalized = (df_test - loaded_means) / loaded_std_devs

	# Add the sample column again
	df_test_normalized['Sample'] = sample_column

	# Normalize the test data
	return df_test_normalized


def denormalize_data(predictions_normalized, mean_path, std_path):
	# Load the mean and standard deviation of the training data
	loaded_means = pd.read_csv(mean_path, index_col=0, squeeze=True)
	loaded_std_devs = pd.read_csv(std_path, index_col=0, squeeze=True)

	df_mean_pred = loaded_means[['JointAngle', 'Mass']]
	df_std_pred = loaded_std_devs[['JointAngle', 'Mass']]

	# Denormalize the test data
	predictions = predictions_normalized * df_std_pred + df_mean_pred

	return predictions


class MyThread(threading.Thread):
	def run(self):
		print("Thread is starting...")
		# Sleep for 0.3 seconds
		time.sleep(0.3)
		print("Thread is waking up after 0.3 seconds.")


if __name__ == '__main__':
	ac = Ada_con(co_mod=0, re_only=True)

	# # ------------ Test load csv data ------------
	# dir_test = 'Code/GRU_network/test_samples.csv'
	# mean_path = 'Code/GRU_network/means.csv'
	# std_path = 'Code/GRU_network/std_devs.csv'
	# loaded_csv = load_csv_data(dir_test)
	# print('Before normalization', end='\n')
	# print(loaded_csv)

	# # ------------ Test load model ------------
	# model_path = 'Code/GRU_network/first_16_feat_10ts_200ep_no_kin.h5'
	# model = read_nn_model(model_path)

	# # ------------ Test normalize data ------------
	# normalized_data = normalize_data(loaded_csv, mean_path, std_path)
	# print('After normalization', end='\n')
	# print(normalized_data)

	# # ------------ Test create sequences ------------
	# seq_X, seq_y = create_sequences(normalized_data, 10)
	# print('Seq_X: ', seq_X, 'Seq_y', seq_y)

	# # ------------ Test predict ------------
	# predictions = predict(model, seq_X, seq_y)

	# # ------------ Test denormalize data ------------
	# pred_denorm = denormalize_data(predictions, mean_path, std_path)
	# print('Predictions: ', pred_denorm)

	# commenting the above line, using the following line if your USBToSerial port ID is not default (i.e., ttyUSB0)
	# ac = Ada_con(co_mod = 0, re_only = True, dn = '/dev/ttyUSB1') # In this case, USBToSerial port ID is ttyUSB1.
	ac.start()

	ac.close()
