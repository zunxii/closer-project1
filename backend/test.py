import os
from audio_utils import convert_mp4_to_mp3

def test_conversion():
    # Replace these paths with your actual file paths
    input_file = "video1.mp4"  # Change this to your MP4 file path
    output_file = "output_audio.mp3"       # This will be created in the current directory
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found!")
        print("Please update the input_file path with a valid MP4 file.")
        return
    
    print(f"Converting: {input_file}")
    print(f"Output: {output_file}")
    
    try:
        convert_mp4_to_mp3(input_file, output_file)
        print("✅ Conversion successful!")
        
        # Check if output file was created
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"✅ Output file created: {output_file} ({file_size} bytes)")
        else:
            print("❌ Output file was not created")
            
    except Exception as e:
        print(f"❌ Conversion failed: {e}")

if __name__ == "__main__":
    test_conversion()