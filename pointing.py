
print("start...")
import numpy
import serial # you may need to install the pySerial :pyserial.sourceforge.net
import struct
import time
import random
import pandas
import re
import threading
from psychopy import core, visual, event, gui, data, iohub, monitors

# your Serial port could be different!
try:
	arduino = serial.Serial('COM3', 9600)
except serial.SerialException:
	arduino = serial.Serial('COM5', 9600)
except serial.SerialException:
	arduino = serial.Serial('COM4', 9600)
except serial.SerialException:
	arduino = serial.Serial('COM1', 9600)
except serial.SerialException:
	arduino = serial.Serial('COM2', 9600)

# let it initialize
mon = monitors.Monitor('default')
time.sleep(2)
winX = 800
winY = 600
io=iohub.launchHubServer()
mouse = io.devices.mouse
mouse.clearEvents()
# create stimulus array
commandSet=[3,4,5,6,7,8]
commandSetArray=numpy.repeat(commandSet,10)
random.shuffle(commandSetArray)
timer = core.Clock()


###########Dialog
info = {'Id':'test', 'Age': 0, 'ExpVersion': 1.4,
        'Group': ['Feedback', 'Non-feedback'], 'Trials': 60}
dictDlg = gui.DlgFromDict(dictionary=info,
        title='TestExperiment', fixed=['ExpVersion'])



if dictDlg.OK:  # or if ok_data is not None
	print(info)
	# Create a window
	win = visual.Window([800,600],  monitor=mon)

	# Create a stimulus for a certain window
	message = visual.TextStim(win, text="Press any key to continue\n")
	# Draw the stimulus to the window.
	message.autoDraw = True
	win.flip()
	# Wait for confirmation
	event.waitKeys()
	# Close window
	win.flip()
	win.close()
	#print(commandSetArray[i])


	trials = info['Trials']
		
	i=1

	if info['Group'] == "Feedback":
		feedbackWin = visual.Window([winX,winY], monitor=mon, color = -1, fullscr=True)

		dataOutput = pandas.DataFrame(columns=['id','age','group','trialIndex','stim','stimemOnset','RT','posX','posY'])
		feedbackWin.flip()

		while i<=trials:
			message = visual.TextStim(feedbackWin, text= "Press Return")
			message.draw()
			feedbackWin.flip()
			key = event.waitKeys(keyList="return", timeStamped=timer)
			if key:
				arduino.write(struct.pack('>B', commandSetArray[i]))
				mouse.clearEvents()
				message = visual.TextStim(feedbackWin, text= ' '.join(["TrialNum: ", str(i), "LedNum: ", str(commandSetArray[i]),"\n", "E Pressed Return"]))
				message.draw()
				feedbackWin.flip()
				
			while True:
				e = mouse.getEvents(event_type=(iohub
                                    .EventConstants
                                    .MOUSE_BUTTON_PRESS))
					
				# If any response was recorded, react to it.
				if e:

					dataOutput.loc[dataOutput.shape[0]]=[info['Id'],info['Age'], info['Group'],
					i,commandSetArray[i], key[0][1], e[0].time, e[0].x_position, e[0].y_position]
					##added for continous output
					dataOutput.to_csv(info['Id']+'.csv', index=False, encoding='utf-8')

					#shut down signal for LED
					arduino.write(struct.pack('>B', 0))
					i=i+1
					break
					
		feedbackWin.close()
				
	elif info['Group'] == "Non-feedback":
		
		nonFeedback = visual.Window([winX,winY], monitor=mon, fullscr=False, color = -1)
		
		message = visual.TextStim(nonFeedback, text= ' '.join(["trial: ", "0", "\n", "Ask P to Press button"]))
		message.draw()
		nonFeedback.flip()

		while arduino.in_waiting:
			print arduino.read()
			
		arduino.write(struct.pack('>B',2)) #grant permission
		while True:
			
			if(arduino.inWaiting()>0):
				tmp = arduino.read()
				if tmp!= '':
					if int(tmp)==2:
						break
		
		message = visual.TextStim(nonFeedback, text= ' '.join(["trial: ", "0", "\n", "P pressed button"]))
		message.draw()
		nonFeedback.flip()
		
		
		while arduino.in_waiting:
			print arduino.read()
			
		arduino.write(struct.pack('>B',2)) #grant permission
		
		message = visual.TextStim(nonFeedback, text= ' '.join(["trial: ", "0", "\n", "Ask P to Press button and keep it pressed until LED appears!" ]))
		message.draw()
		nonFeedback.flip()
		
		while True:
			
			if(arduino.inWaiting()>0):
				tmp = arduino.read()
				if tmp!= '':
					if int(tmp)==2:
						break
		
		message = visual.TextStim(nonFeedback, text= ' '.join(["trial: ", "0", "\n", "Press Return!" ]))
		message.draw()
		nonFeedback.flip()
		
		key = event.waitKeys(keyList="return", timeStamped=timer)
		
		
		dataOutput = pandas.DataFrame(columns=['id','age','group','trialIndex','stim','stimemOnset','RT','posX','posY'])
		
		global timeOfParRelease
							
		while i<=trials:
				
				def waitForRelease():
				
					mouse.clearEvents()
					arduino.write(struct.pack('>B', commandSetArray[i]))
					arduino.write(struct.pack('>B', 1))
					print "Listen to button release..."
					while True:
						if(arduino.inWaiting()>0):  
							tmp = arduino.read()
							if tmp!= '':
								if int(tmp)==1:

									arduino.write(struct.pack('>B', 0)) #LED switched off

									timeOfParRelease = timer.getTime()
									print "P released button"
									break
				
				
				message = visual.TextStim(nonFeedback, text= ' '.join(["trial: ", str(i), "\n", "Press Return again"]))
				message.draw()
				nonFeedback.flip()
				
				key = event.waitKeys(keyList="return", timeStamped=timer)

				try:
					t3 = threading.Thread( target = waitForRelease)
					t3.start()
				except:
					print "Error: unable to start threads"
				
				
				message = visual.TextStim(nonFeedback, text= ' '.join(["trial: ", str(i), "\n", "Stimulus initiated"]))
				message.draw()
				nonFeedback.flip()

				t3.join()
				message = visual.TextStim(nonFeedback, text= ' '.join(["trial: ", str(i), "\n",  "Button released"]))
				message.draw()
				nonFeedback.flip()
				
				while True:
					
					e = mouse.getEvents(event_type=(iohub
                                    .EventConstants
                                    .MOUSE_BUTTON_PRESS))                   
                            
					if e:
						dataOutput.loc[dataOutput.shape[0]]=[info['Id'],info['Age'], info['Group']
						,i,commandSetArray[i], key[0][1], e[0].time, e[0].x_position, e[0].y_position]
						##added for continous output
						dataOutput.to_csv(info['Id']+'.csv', index=False, encoding='utf-8')						
						
						message = visual.TextStim(nonFeedback, text= ' '.join(["trial: ", str(i), "\n", "Screen touched \n Wait for Participant to press button"]))
						message.draw()
						nonFeedback.flip()
						
						i=i+1

						arduino.write(struct.pack('>B', 2))
						break
						
				def waitForButtonPress():
					while True:
						tmp = arduino.read()
					
						if tmp!= '':
							if int(tmp)==2:
								break
						
				try:
					t4 = threading.Thread( target = waitForButtonPress)
					t4.start()
				except:
					print "Error: unable to start threads"
				t4.join()		
						
		nonFeedback.close()
					
						
					
	dataOutput.to_csv(info['Id']+'.csv', index=False, encoding='utf-8')
	
	endWin = visual.Window([800,600],  monitor=mon)
	message = visual.TextStim(endWin, text="Experiment ended \n\nThank the participant for participating!")
	# Draw the stimulus to the window.
	message.draw()
	endWin.flip()
	
	time.sleep(5)
	arduino.close()
	core.quit()




