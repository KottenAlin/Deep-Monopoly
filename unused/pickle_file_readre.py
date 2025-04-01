import pickle
import sys

def read_pickle_file(file_path):
    """
    Read and display the contents of a pickle file.
    
    Args:
        file_path (str): Path to the pickle file to read
    """
    try:
        # Open the file in binary read mode
        with open(file_path, 'rb') as file:
            # Load the data from the pickle file
            data = pickle.load(file)
            
            # Print the data
            print("Pickle file contents:")
            print(data)
            return data
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except pickle.UnpicklingError:
        print(f"Error: File '{file_path}' is not a valid pickle file or is corrupted.")
    except Exception as e:
        print(f"Error: {e}")
    
    return None

if __name__ == "__main__":

        pickle_file_path = "game_history.pkl"
        read_pickle_file(pickle_file_path)
