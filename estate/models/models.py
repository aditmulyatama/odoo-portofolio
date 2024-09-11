# import os

# # Get the directory path from the user
# directory_path = input("Enter the directory path: ")

# # Validate if the directory exists
# if os.path.exists(directory_path):
#     # Get all file names in the specified directory
#     files = os.listdir(directory_path)

#     # Loop through each file
#     for filename in files:
#         # Check if 'estate_' is in the filename
#         if filename.startswith('estate_'):
#             # Create new filename by removing 'estate_'
#             new_filename = filename.replace('estate_', '', 1)
#             # Rename file to new filename
#             os.rename(os.path.join(directory_path, filename), os.path.join(directory_path, new_filename))
#     print("File names updated successfully!")
# else:
#     print(f"Directory '{directory_path}' does not exist.")
