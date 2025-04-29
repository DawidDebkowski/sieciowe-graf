def tranlate_to_binaries(message):
    """
    Translates a message to binary format.
    """
    binary_message = ''.join(format(ord(char), '08b') for char in message)
    return binary_message

def tranlate_to_text(binary_message):
    """
    Translates a binary message to text format.
    """
    binary_values = [binary_message[i:i+8] for i in range(0, len(binary_message), 8)]
    ascii_characters = [chr(int(bv, 2)) for bv in binary_values]
    decoded_message = ''.join(ascii_characters)
    return decoded_message

def add_bit_stuffing(message):
    """
    Adds bit stuffing to a message.
    """
    stuffed_message = ''
    count = 0
    for bit in message:
        if bit == '1':
            count += 1
            stuffed_message += bit
            if count == 5:
                stuffed_message += '0'  # Add a 0 after five consecutive 1s
                count = 0
        else:
            stuffed_message += bit
            count = 0
    return stuffed_message

def remove_bit_stuffing(message):
    """
    Removes bit stuffing from a message.
    """
    unstuffed_message = ''
    count = 0
    i = 0
    while i < len(message):
        if message[i] == '1':
            count += 1
            unstuffed_message += '1'
            if count == 5 and i + 1 < len(message) and message[i + 1] == '0':
                # Skip the stuffed 0 bit after five consecutive 1s
                i += 1
                count = 0
        else:
            unstuffed_message += '0'
            count = 0
        i += 1
    return unstuffed_message

def add_header(message):
    """
    Adds header to a message.
    """
    return '01111110' + message + '01111110'

def remove_header(message):
    """
    Removes the header from a message.
    """
    if message.startswith('01111110') and message.endswith('01111110'):
        return message[8:-8]
    else:
        raise ValueError("Invalid message format: Header not found.")

def seperate_message(message, size):
    """
    Separates a message into chunks of size bits.
    """
    chunks = []
    for i in range(0, len(message), size):
        chunks.append(message[i:i + size])
    return chunks

def detect_frames(message):
    """
    Detects frames in a message using the header as a delimiter.
    """
    header = '01111110'
    frames = []
    if header in message:
        parts = message.split(header)
        for part in parts:
            if part:  # Skip empty parts
                frames.append(part)
    return frames

def crc_remainder(message, polynomial):
    """
    Computes the CRC remainder of a message divided by the polynomial.
    """
    poly_len = len(polynomial)
    if len(message) < poly_len:
        # Pad with zeros if message is shorter than polynomial
        message = message + '0' * (poly_len - len(message))
    remainder = list(message[:poly_len - 1])
    for i in range(poly_len - 1, len(message)):
        remainder.append(message[i])
        if remainder[0] == '1':
            for j in range(poly_len):
                if j < len(remainder):
                    remainder[j] = '0' if remainder[j] == polynomial[j] else '1'
        remainder.pop(0)
    return ''.join(remainder)

def add_crc(message, polynomial='10001000000100001'):
    """
    Adds CRC to a message using the specified polynomial.
    Default polynomial is CRC-16-IBM (0x8005 in reverse bit order).
    """
    # Append zeros to the message equal to polynomial length-1
    padded_message = message + '0' * (len(polynomial) - 1)
    # Compute remainder
    remainder = crc_remainder(padded_message, polynomial)
    # Append the remainder (checksum) to the original message
    return message + remainder

def verify_crc(message, polynomial='10001000000100001'):
    """
    Verifies CRC of a message using the specified polynomial.
    Returns original message without CRC if valid, otherwise raises exception.
    """
    poly_len = len(polynomial)
    if len(message) < poly_len - 1:
        raise ValueError("Message too short to contain CRC")
    # Compute remainder on the entire message (original + CRC)
    remainder = crc_remainder(message, polynomial)
    # If remainder is all zeros, CRC is valid
    if remainder == '0' * (poly_len - 1):
        return message[:-(poly_len - 1)]
    else:
        raise ValueError(f"CRC check failed. Data may be corrupted. Remainder: {remainder}")

def process_message(message, size):
    """
    Processes message by separating it into frames,
    adding CRC, bit stuffing, and adding headers.
    """
    # Clear the contents of the message.txt file before processing
    with open('message.txt', 'w') as file:
        file.truncate(0)
    
    binary_message = tranlate_to_binaries(message)
    print(f"Original Message: {message}")
    print(f"Binary Message: {binary_message}")
    
    frames = seperate_message(binary_message, size)
    for i, frame in enumerate(frames):
        print(f"\nFrame {i+1}: {frame}")
        
        # Add CRC to frame
        frame_with_crc = add_crc(frame)
        print(f"Frame with CRC: {frame_with_crc}")
        
        # Add bit stuffing to avoid flag sequence in the data
        stuffed_message = add_bit_stuffing(frame_with_crc)
        print(f"Stuffed Message: {stuffed_message}")
        
        # Add header flags
        header_message = add_header(stuffed_message)
        print(f"Message with header: {header_message}")
        
        # Save to file
        with open('message.txt', 'a') as file:
            file.write(header_message)
        print(f"Message with header saved in file")

def process_received_message():
    """
    Processes received message by removing headers,
    removing bit stuffing, verifying CRC, and translating to text.
    """
    decoded_message = ''
    error_frames = 0
    
    try:
        with open('message.txt', 'r') as file:
            message = file.read()
            print(f"\nReceived Message: {message}")
            
            # Split message into frames using the flag as delimiter
            raw_frames = message.split('01111110')
            frames = [frame for frame in raw_frames if frame]  # Remove empty strings
            
            print(f"Detected {len(frames)} frames")
            
            for i, frame in enumerate(frames):
                try:
                    print(f"\nProcessing Frame {i+1}: {frame}")
                    
                    # Remove bit stuffing
                    unstuffed_message = remove_bit_stuffing(frame)
                    print(f"Unstuffed Message: {unstuffed_message}")
                    
                    # Verify CRC
                    original_message = verify_crc(unstuffed_message)
                    print(f"Original Message (CRC verified): {original_message}")
                    
                    # Translate binary to text
                    text_chunk = tranlate_to_text(original_message)
                    decoded_message += text_chunk
                    print(f"Decoded chunk: '{text_chunk}'")
                    
                except ValueError as e:
                    print(f"Error processing frame {i+1}: {e}")
                    error_frames += 1
                    # If a frame is corrupted, we might want to request retransmission
                    # For now, we'll just skip it
            
            if error_frames > 0:
                print(f"\nWARNING: {error_frames} frames had errors and were skipped")
            
            print(f"\nFinal decoded message: '{decoded_message}'")
            return decoded_message
            
    except FileNotFoundError:
        print("Error: message.txt file not found")
        return ""

def simulate_transmission_error(message, error_rate=0.001):
    """
    Simulates transmission errors by flipping random bits with probability error_rate.
    Used for testing the CRC error detection.
    """
    import random
    result = list(message)
    for i in range(len(result)):
        if random.random() < error_rate:
            result[i] = '1' if result[i] == '0' else '0'
            print(f"Introduced error at position {i}")
    return ''.join(result)

if __name__ == "__main__":
    # Number of bytes per frame (excluding CRC, headers)
    bytes_in_frames = 4
    bits_in_frame = bytes_in_frames * 8
    
    # Process the message to be sent
    original_message = 'Ide mlody genialny trzymam but w butonierce tym co za mna nie zdarza cichopowiem Adieu!'
    process_message(original_message, bits_in_frame)
    
    # Optional: Simulate transmission errors
    with open('message.txt', 'r') as file:
        content = file.read()
    corrupted_content = simulate_transmission_error(content, error_rate=0.005)
    with open('message.txt', 'w') as file:
        file.write(corrupted_content)
    
    # Process the received message
    received_message = process_received_message()
    
    # Check if the message was received correctly
    if received_message == original_message:
        print("\nSuccess! Message transmitted and received correctly.")
    else:
        print("\nWarning: Received message differs from original message.")
        print(f"Original: '{original_message}'")
        print(f"Received: '{received_message}'")