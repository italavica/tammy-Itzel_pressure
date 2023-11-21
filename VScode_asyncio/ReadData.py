import pandas as pd
import matplotlib.pyplot as plt


# Load the CSV file
file_path = 'FBG_wavelength_shift.csv'
data = pd.read_csv(file_path)

# Splitting the data into three separate dataframes
time_data = data['time']  # Assuming the first column is 'time'
FBG1_data = data['wavelength_shift_1']  # Assuming the second column is 'FBG1'
FBG2_data = data['wavelength_shift_2']  # Assuming the third column is 'FBG2'

# # File paths for the new text files
# time_file = 'time.txt'
# FBG1_file = 'FBG1.txt'
# FBG2_file = 'FBG2.txt'

# # Writing the data to text files
# time_data.to_csv(time_file, index=False, header=False)
# FBG1_data.to_csv(FBG1_file, index=False, header=False)
# FBG2_data.to_csv(FBG2_file, index=False, header=False)


# save part of data
time_part = time_data[500:3500]
FBG2_part = FBG2_data[500:3500]

plt.plot(time_part, FBG2_part)
plt.show()


# # File paths for the new text files
time_file = 'time_part.txt'
# FBG1_file = 'FBG1.txt'
FBG2_file = 'FBG2_part.txt'

# # Writing the data to text files
time_part.to_csv(time_file, index=False, header=False)
FBG2_part.to_csv(FBG2_file, index=False, header=False)