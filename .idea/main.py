import subprocess
import tkinter as tk
import util
import cv2
from PIL import Image, ImageTk
import os
import numpy as np
import csv
from datetime import datetime
import pandas as pd





class App:

    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.geometry("1200x520+350+100")

        # Login button
        self.login_button_main_button = util.get_button(
            self.main_window, 'Login', 'Green', self.login)
        self.login_button_main_button.place(x=750, y=300)

        # Register button
        self.register_new_user_button_main_button = util.get_button(
            self.main_window, 'Register New User', 'Grey', self.register_new_user, fg='black')
        self.register_new_user_button_main_button.place(x=750, y=400)

        # Webcam label
        self.webcam_label = util.get_img_label(self.main_window)
        self.webcam_label.place(x=10, y=0, width=700, height=500)

        self.add_webcam(self.webcam_label)

        self.db_dir = './db'
        if not os.path.exists(self.db_dir):
           os.mkdir(self.db_dir)

    def add_webcam(self, label):
        if 'cap' not in self.__dict__:
            # Try 0 or 1 depending on your camera setup
            self.cap = cv2.VideoCapture(0)  
        self._label = label
        self.process_webcam()

    def process_webcam(self):
        ret, frame = self.cap.read()

        if not ret or frame is None:
            print("Failed to capture frame")
            self._label.after(20, self.process_webcam)
            return

        
        self.most_recent_capture_arr = frame
        img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
        self.most_recent_capture_pil = Image.fromarray(img_)
        imagetk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)

        self._label.imagetk = imagetk
        self._label.configure(image=imagetk)

        self._label.after(20, self.process_webcam)

    

    # def login(self):
    #  unknown_img_path ='./.tmp.jpg'

    #  cv2.imwrite(unknown_img_path,self.most_recent_capture_arr)
    #  output = str(subprocess.check_output(['face_recognition',self.db_dir,unknown_img_path]))
    #  name = output.split(',')[1][:-3]
    #  print(name)

    #  if name in ['unknown_person','no_persons_found']:
    #     util.msg_box("Error!","Unkown User: Please Register or Try Again")
    #  else:
    #     util.msg_box('Success!',f"welcome, \n{name}")
    #  os.remove(unknown_img_path)
    def login(self):
      unknown_img_path = './.tmp.jpg'
      cv2.imwrite(unknown_img_path, self.most_recent_capture_arr)
    
      output = str(subprocess.check_output(['face_recognition', self.db_dir, unknown_img_path]))
      name = output.split(',')[1][:-3]
      print(name)
      os.remove(unknown_img_path)

     

      if name in ['unknown_person', 'no_persons_found']:
        util.msg_box("Error!", "Unknown User: Please Register or Try Again")
      else:
        util.msg_box('Success!', f"Welcome, \n{name}")
        self.record_attendance(name)
    


    def record_attendance(self, name):
     attendance_file = 'attendance.csv'
     today = datetime.now().strftime('%Y-%m-%d')

    # Create a blank DataFrame if file doesn't exist
     if not os.path.exists(attendance_file):
        df = pd.DataFrame(columns=['Name', today])
     else:
        df = pd.read_csv(attendance_file)

    # Add today's column if not present
     if today not in df.columns:
        df[today] = "Absent"

    # Check if user exists
     if name in df['Name'].values:
        # Check if already marked today
        if df.loc[df['Name'] == name, today].values[0] == "Present":
            print("Already marked present today.")
            return
        else:
            df.loc[df['Name'] == name, today] = "Present"
     else:
        # Add new user with present today, absent on other days
        new_row = {'Name': name, today: "Present"}
        for col in df.columns:
            if col not in new_row:
                new_row[col] = "Absent"
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

     df.to_csv(attendance_file, index=False)
     print("Attendance recorded.")




    def register_new_user(self):
      self.register_new_user_window = tk.Toplevel(self.main_window)
      self.register_new_user_window.geometry("1200x520+370+120")
      self.accept_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Accept', 'Green', self.accept_register_new_user)
      self.accept_button_register_new_user_window.place(x=750, y=300)
      self.try_again_button_register_new_user = util.get_button(self.register_new_user_window, 'Try Again', 'Red', self.try_again_register_new_user)
      self.try_again_button_register_new_user.place(x=750, y=400)


      self.capture_label = util.get_img_label(self.register_new_user_window)
      self.capture_label.place(x=10, y=0, width=700, height=500)

      self.add_image_to_label(self.capture_label)

      self.entry_text_register_new_user_label = util.get_entry_text(self.register_new_user_window)
      self.entry_text_register_new_user_label.place(x=750,y=150)
      self.text_label_register_new_user = util.get_text_label(self.register_new_user_window,'Please Enter your \nUsername:')
      self.text_label_register_new_user.place(x=750,y=70)

      

    def add_image_to_label(self,label):
     imagetk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
     label.imagetk = imagetk
     label.configure(image=imagetk)

     self.register_new_user_capture = self.most_recent_capture_pil.copy()
    
    def try_again_register_new_user(self):
       self.register_new_user_window.destroy()

    def accept_register_new_user(self):
        name = self.entry_text_register_new_user_label.get(1.0,"end-1c").strip()
        if name == "":
           print("please enter a valid name.")
           return
        img_np = np.array(self.register_new_user_capture)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        save_path = os.path.join(self.db_dir,f"{name}.jpg")

        success = cv2.imwrite(save_path,img_bgr)
        if success:
           util.msg_box('User Registration', 'The User was Registered Successfully')
           self.register_new_user_window.destroy()
        else:
           util.msg_box('Failed !','the user was not registered successfully')

      



    def start(self):
     self.main_window.mainloop()
    
    

if __name__ == "__main__":
    app = App()
    app.start()
