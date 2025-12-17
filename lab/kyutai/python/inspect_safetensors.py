
import sys
import struct
import json

def read_safetensors_header(path):
    with open(path, 'rb') as f:
        # Read header size (8 bytes, little endian unsigned long long)
        header_size_bytes = f.read(8)
        if len(header_size_bytes) != 8:
            print("Error: File too small")
            return
        
        header_size = struct.unpack('<Q', header_size_bytes)[0]
        
        # Read header JSON
        header_json_bytes = f.read(header_size)
        header_data = json.loads(header_json_bytes.decode('utf-8'))
        
        # Print keys (layer names) and shapes
        print(f"Header size: {header_size}")
        print("Tensors:")
        for key, value in header_data.items():
            if key == "__metadata__":
                continue
            print(f"{key}: {value['shape']}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python inspect_safetensors.py <path>")
        sys.exit(1)
    
    read_safetensors_header(sys.argv[1])
