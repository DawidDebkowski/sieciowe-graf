def tranlate_to_text(binary_message):
    """
    Translates a binary message to text format.
    """
    binary_values = [binary_message[i:i+8] for i in range(0, len(binary_message), 8)]
    ascii_characters = [chr(int(bv, 2)) for bv in binary_values]
    decoded_message = ''.join(ascii_characters)
    return decoded_message

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
            print(f'There are {len(frames)-error_frames} correct frames')

            # print(f"\nFinal decoded message: '{decoded_message}'")
            return decoded_message
            
    except FileNotFoundError:
        print("Error: message.txt file not found")
        return ""
    
if __name__ == "__main__":
    received_message = process_received_message()

    # print(f"Received             : '{received_message}'")