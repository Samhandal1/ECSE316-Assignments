# ECSE316

## Assignment 1: Network Programming and DNS
Overview: This assignment involves implementing a DNS client using Python sockets. The key learning outcomes include understanding network protocol specifications, designing network applications adhering to specific protocols, and implementing/testing these applications using sockets.

### Tasks:

- DNS Client Development: Create a Python-based DNS client capable of querying for A, MX, and NS records, interpreting A and CNAME record responses, and handling lost query retransmissions.
- Error Handling: Implement graceful error handling for non-conformant responses, uninterpretable fields, or mismatched queries.
- Command Line Interface: Design the client to be command-line operable with options for timeout, maximum retries, port number, and query type.
- Output Specification: Ensure the program outputs a standardized response format, detailing the query, performance, and content of the DNS response.

## Assignment 2: Fast Fourier Transform and Applications
Overview: This assignment focuses on implementing two versions of the Discrete Fourier Transform (DFT) - a brute force approach and a Fast Fourier Transform (FFT) approach using Cooley-Tukey algorithm. Students explore the application of FFT in image denoising and compression.

### Tasks:

- DFT Implementations: Create both a naïve DFT and an FFT algorithm in Python, including their inverse operations.
- 2D Fourier Transforms: Extend the FFT algorithm to handle 2-dimensional cases.
- Image Processing Applications: Utilize FFT for image denoising and compression, involving thresholding of frequency components.
- Performance Analysis: Generate runtime plots to compare the efficiency of the naïve DFT and FFT algorithms, including error bars for confidence intervals.
- Output Formatting: Design the program to output results based on different modes, such as fast mode, denoising, compression, and runtime plotting.
