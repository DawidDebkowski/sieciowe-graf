def tranlate_to_binaries (message):
    """
    Translates a message to binary format.
    """
    binary_message = ''.join(format(ord(char), '08b') for char in message)
    return binary_message

def tranlate_to_text (binary_message):
    """
    Translates a binary message to text format.
    """
    binary_values = [binary_message[i:i+8] for i in range(0, len(binary_message), 8)]
    ascii_characters = [chr(int(bv, 2)) for bv in binary_values]
    decoded_message = ''.join(ascii_characters)
    return decoded_message

def add_bit_stuffing (message):
    """
    Adds bit stuffing to a message.
    """
    stuffed_message = ''
    count = 0
    for bit in message:
        if bit == '1':
            count += 1
            if count == 5:
                stuffed_message += '1' + '0'
                count = 0
            else:
                stuffed_message += bit
        else:
            stuffed_message += bit
            count = 0
    return stuffed_message

def remove_bit_stuffing (message):
    """
    Removes bit stuffing from a message. Assumes that header has been removed.
    """
    unstuffed_message = ''
    count = 0
    for bit in message:
        if bit == '1':
            count += 1
            if count == 5:
                continue
        else:
            count = 0
        unstuffed_message += bit
    return unstuffed_message


def add_header (message):
    return '01111110' + message + '01111110'

def remove_header (message):
    """
    Removes the header from a message.
    """
    if message.startswith('01111110') and message.endswith('01111110'):
        return message[8:-8]
    else:
        raise ValueError("Invalid message format: Header not found.")

def seperate_message (message, size):
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
    frames = message.split(header)
    return frames

# def add_crc (message):
#     """
#     Adds CRC to a message.
#     """
#     # CRC polynomial
#     polynomial = '1101'
#     # Append zeros to the message
#     padded_message = message + '0' * (len(polynomial) - 1)
#     # Perform binary division
#     remainder = binary_division(padded_message, polynomial)
#     # Append the remainder to the original message
#     return message + remainder



def process_message(message, size):
    """
    Processes message by separating it into frames,
    adding bit stuffing, and adding headers.
    """
    # Clear the contents of the message.txt file before processing
    with open('message.txt', 'w') as file:
        file.truncate(0)
    binary_message = tranlate_to_binaries(message)
    # print(f"Original Message: {message}")
    # print(f"Binary Message: {binary_message}")
    frames = seperate_message(binary_message, size)
    for frame in frames:
        # print(f"Frame: {frame}")
        stuffed_message = add_bit_stuffing(frame)
        # print(f"Stuffed Message: {stuffed_message}")
        header_message = add_header(stuffed_message)
        print(f"Header Message: {header_message}")
        with open('message.txt', 'a') as file:
            file.write(header_message)
        print(f"Header Message saved in file")
        print()

def process_received_message():
    """
    Processes received message by removing headers,
    removing bit stuffing, and translating to text.
    """
    decoded_message = ''
    with open('message.txt', 'r') as file:
        message = file.read()
        # seperate into frames
        print(f"Received Message: {message}")
        frames = detect_frames(message)
        for frame in frames:
            removed_header = detect_frames(frame)
            print(f"Removed Message: {removed_header}")
            unstuffed_message = remove_bit_stuffing(removed_header)
            print(f"Unstuffed Message: {unstuffed_message}")
            decoded_message += tranlate_to_text(unstuffed_message)
    print(f"Decoded message: {decoded_message}")

if __name__ == "__main__":
    baits_in_frames = 4
    # Process the message to be sent
    process_message('Ide mlody genialny trzymam but w butonierce tym co za mna nie zdarzxa cichopowiem Adieu!', baits_in_frames*8)
    
    # Process the received message
    process_received_message()