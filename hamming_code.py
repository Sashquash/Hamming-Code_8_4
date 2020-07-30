from typing import List, Generator

# hamming code (8,4)
def encode(source: Generator[bytes, None, None]) -> Generator[bytes, None, None]:
    for byte in source:
        # transform bytes into integer so I can work with the numbers
        byte = int.from_bytes(byte, "big")
        
        # seperate the byte into it's parts
        x1 = byte >> 7
        x2 = (byte >> 6) & 1
        x3 = (byte >> 5) & 1
        x4 = (byte >> 4) & 1
        x5 = (byte >> 3) & 1
        x6 = (byte >> 2) & 1
        x7 = (byte >> 1) & 1
        x8 = byte & 1
        
        # to fasten up code; precalculate x1 ^ x2 and x3 ^ x4, so I don't have to calculate them twice in p1, p2, p3, c1
        temp1 = x1 ^ x2
        temp2 = x3 ^ x4
        
        # calculate the bits for detecting and correcting errors later
        p1 = temp1 ^ x3
        p2 = x1 ^ temp2
        p3 = x2 ^ temp2
        
        # c bit is to detect several errors
        c1 = temp1 ^ x4
        
        # prepare and submit, byte = p1 p2 x1 p3 x2 x3 x4 c1
        byte1 = (p1 << 7) + (p2 << 6) + (x1 << 5) + (p3 << 4) + (x2 << 3) + (x3 << 2) + (x4 << 1) + c1
        yield bytes([byte1])
        
        # to fasten up code; precalculate x7 ^ x8 and x5 ^ x6, so I don't have to calculate them twice in p1, p2, p3, c1
        temp1 = x7 ^ x8
        temp2 = x5 ^ x6
        
        # calculate the bits for detecting and correcting errors later
        p1 = temp2 ^ x7
        p2 = x5 ^ temp1
        p3 = x6 ^ temp1
        
        # c bit is to detect several errors
        c1 = temp2 ^ x8
        
        # prepare and submit, byte = p1 p2 x4 p3 x5 x6 x7 c1
        byte2 = (p1 << 7) + (p2 << 6) + (x5 << 5) + (p3 << 4) + (x6 << 3) + (x7 << 2) + (x8 << 1) + c1
        yield bytes([byte2])


def decode(source: Generator[bytes, None, None]) -> Generator[bytes, None, None]:
    # counter - needed to reasamble code
    #  ↳0 = first half of byte; 1 = second half of byte
    counter = 0
    
    # first_half - to save the first 4 bits that arrived when decoding next 8 bits into the 4 bits
    first_half = 0
    
    for byte in source:
        # transform bytes into integer so I can work with the numbers
        byte = int.from_bytes(byte, "big")
        
        # seperate the byte into it's parts
        p1 = byte >> 7
        p2 = (byte >> 6) & 1
        x1 = (byte >> 5) & 1
        p3 = (byte >> 4) & 1
        x2 = (byte >> 3) & 1
        x3 = (byte >> 2) & 1
        x4 = (byte >> 1) & 1
        c1 = byte & 1
        
        # fasten up code; since x3 ^ x4 is used twice precalculate and use once
        temp1 = x3 ^ x4
        
        # reverse for error detection
        s1 = p1 ^ x1 ^ x2 ^ x3
        s2 = p2 ^ x1 ^ temp1
        s3 = p3 ^ x2 ^ temp1
        s = s1 + s2 + s3
        
        # code below represents: c2 = p1 ^ p2 ^ p3 ^ x1 ^ x2 ^ x3 ^ x4;
        # ↳ did replace p1 ^ x1 ^ x2 ^ x3 with s1 since this is already calculated above
        c2 = s1 ^ p2 ^ p3 ^ x4
        
        # check if the check for the entire byte adds up or not
        c = c1 ^ c2
        
        # single bit error detected; correcting it
        if s != 0 and c != 0:
            # here error is position of error
            herer_error =  s1 + (s2 << 1) + (s3 << 2)
            # if and elif correct the error by flipping the bit
            if herer_error == 7:
                x3 = 1 ^ x3
            elif herer_error == 6:
                x4 = 1 ^ x4
            elif herer_error == 5:
                x2 = 1 ^ x2
            elif herer_error == 3:
                x1 = 1 ^ x1
                
        # at this point either error got corrected
        # ↳ OR there are several non corractable errors
        # ↳ OR there is an error in the c bit (which we don't care about)
        # ↳ OR there where no errors in the first place
        if counter == 0:
            # counter 0 -> first 4 bits; calculate first half of the byte and get next byte
            first_half = (x1 << 3) + (x2 << 2) + (x3 << 1) + x4
            counter = 1
            continue
        else:
            # counter 1 -> first 4 bits already gotten; attach 4 bits of byte to first half and yield it
            b = (first_half << 4) + ((x1 << 3) + (x2 << 2) + (x3 << 1) + x4)
            counter = 0
            yield (bytes([b]))
