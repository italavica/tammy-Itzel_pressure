import pandas as pd

# Load the data
fbg2_path = 'FBG2_part.txt'
time_path = 'time_part.txt'
fbg2_data = pd.read_csv(fbg2_path, header=None)
time_data = pd.read_csv(time_path, header=None)

# Determine the time step between data points
time_step = time_data.diff().mean().item()

# Calculate the number of steps to shift for a 0.5 second delay
shift_steps = int(0.5 / time_step)

# Shift the time data
shifted_time_data = time_data.shift(-shift_steps)

# Shift the FBG2 data
shifted_fbg2_data = fbg2_data.shift(-shift_steps)

# Truncate the shifted data to match the original length
shifted_time_data = shifted_time_data.iloc[:len(time_data)]
shifted_fbg2_data = shifted_fbg2_data.iloc[:len(fbg2_data)]

# Ensure the last values are not NaN due to the shift
shifted_time_data = shifted_time_data.dropna()
shifted_fbg2_data = shifted_fbg2_data.dropna()

# Save the shifted data to files
shifted_time_data.to_csv('shifted_time_data.txt', index=False, header=False)
shifted_fbg2_data.to_csv('shifted_fbg2_data.txt', index=False, header=False)
