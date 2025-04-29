def tranlate_to_binaries(message):
    """
    Translates a message to binary format.
    """
    binary_message = ''.join(format(ord(char), '08b') for char in message)
    return binary_message

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
    original_message = 'Ide mlody genialny trzymam but w butonierce tym co za mna nie zdarzxa cichopowiem Adieu!'
    process_message(original_message, bits_in_frame)
    
    # Simulate transmission errors
    # with open('message.txt', 'r') as file:
    #     content = file.read()
    # corrupted_content = simulate_transmission_error(content, error_rate=0.005)
    # with open('message.txt', 'w') as file:
    #     file.write(corrupted_content)