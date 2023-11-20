import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import argparse
import cv2

# Compute the one-dimensional discrete Fourier transform.
def dft_1d(signal):
    
    # signal: 1D array-like object containing the input signal (time-domain).
    # return: 1D array representing the DFT (frequency-domain).
    
    N = len(signal)
    dft = np.zeros(N, dtype=complex)

    for k in range(N):      # Iterating over output frequency bins
        for n in range(N):  # Iterating over input signal samples
            angle = -2j * np.pi * k * n / N
            dft[k] += signal[n] * np.exp(angle)

    return dft

# Compute the two-dimensional discrete Fourier transform.
def dft_2d(image):

    # image: 2D array-like object representing the grayscale image.
    # return: 2D array representing the DFT of the image.

    M, N = image.shape
    dft = np.zeros((M, N), dtype=complex)

    # Apply 1D DFT to each row
    for u in range(M):
        dft[u, :] = dft_1d(image[u, :])

    # Apply 1D DFT to each column of the result
    for v in range(N):
        dft[:, v] = dft_1d(dft[:, v])

    return dft

# Compute the one-dimensional Fast Fourier Transform using the Cooley-Tukey algorithm.
def fft_1d(signal):
    
    # signal: 1D array-like object containing the input signal (time-domain).
    # return: 1D array representing the FFT (frequency-domain).

    N = len(signal)

    # Recursion's base case: when the length of the signal array (N) is 1 or less
    if N <= 1: 
        return signal

    # Cooley-Tukey dividing step, into even and odd (using array slicing... [start:stop:step])
    # Then call recursively on two halves, breaking down the problem into smaller sub-problems
    even = fft_1d(signal[0::2])
    odd = fft_1d(signal[1::2])

    # Combine step, combines the DFTs of the even and odd parts to produce the final DFT of the signal
    
    # For each k (representing the frequency bin), a complex exponential term is calculated: 
    #   np.exp(-2j * np.pi * k / N)
    # This term is multiplied by the corresponding element in the odd part. 
    #   The modulo operation (k % (N//2)) ensures that the index stays within the bounds of the array
    
    T = [np.exp(-2j * np.pi * k / N) * odd[k % (N//2)] for k in range(N)]

    # The final DFT is obtained by alternating additions and subtractions of the even and T (modified odd) parts
    # - For the first half (k from 0 to N/2), elements from even and T are added.
    # - For the second half (k from N/2 to N), elements from even and T are subtracted.

    return [even[k % (N//2)] + T[k] for k in range(N)] + [even[k % (N//2)] - T[k] for k in range(N)]

# Compute the two-dimensional Fast Fourier Transform.
def fft_2d(image):

    # image: 2D array-like object representing the grayscale image.
    # return: 2D array representing the FFT of the image.

    M, N = image.shape
    fft = np.zeros((M, N), dtype=complex)

    # Apply 1D FFT to each row
    for u in range(M):
        fft[u, :] = fft_1d(image[u, :])

    # Apply 1D FFT to each column of the result
    for v in range(N):
        fft[:, v] = fft_1d(fft[:, v])

    return fft


# Implement the FFT and display the frequency domain image
def fast_mode(image):

    # 1 - perform the FFT (break 2d into 1d)
    # 2 - output a 1 by 2 subplot of the original image next to its Fourier transform

    ##################### IDK IF THIS WORKS ################################

    # Compute the 2D FFT using the custom implementation
    f_transform = fft_2d(image)
    magnitude_spectrum = np.log(np.abs(f_transform) + 1)  # Log scaling

    # Plotting the original image and its FFT
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.imshow(image, cmap='gray')
    plt.title("Original Image")

    plt.subplot(1, 2, 2)
    plt.imshow(np.fft.fftshift(magnitude_spectrum), norm=LogNorm(), cmap='gray')
    plt.title("FFT (Log Scaled)")
    plt.colorbar()

    plt.show()

# Implement the denoising logic
def denoise_image(image):

    # 1 - perform the denoising
    #   1.1 - take the FFT of the image  
    #   1.2 - set all the high frequencies to zero 
    #   1.3 - invert to get back the filtered original
    # 2 - output a 1 by 2 subplot of the original image next to its denoised version
    pass

# Implement the compression logic
def compress_image(image):

    # 1 - preform compression 
    #   1.1 - take the FFT of the image
    #   1.2 - setting some Fourier coefficients to zero... choose one of the following
    #       1.2.1 - threshold the coefficients’ magnitude and take only the largest percentile of them
    #       1.2.2 - you can keep all the coefficients of very low frequencies as well as a fraction of the largest coefficients from higher frequencies to also filter the image at the same time
    #   1.3 - inverse transform the modified Fourier coefficients
    # 2 - output a 2 by 3 subplot of the image at 6 different compression levels
    # 3 - print in the command line the number of non zeros that are in each of the 6 images
    pass

# Implement runtime analysis and plotting
def plot_runtime_graphs():

    # print in the command line the means and variances of the runtime of your algorithms versus the problem size
    pass

# Helper: Check if a number is a power of two.
def is_power_of_two(n):
    return (n != 0) and (n & (n - 1) == 0)

# Helper: Find the nearest power of two that is greater than or equal to n.
def nearest_power_of_two(n):
    return 2 ** np.ceil(np.log2(n))

# Helper: Load an image from a file
def load_image(filename):

    # load with opencv
    image = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)

    if image is None:
        raise ValueError("Image could not be loaded. Please check the file path.")

    # If the image you are given does not have a length or width that is a power of 2 you can resize it with cv2
    # Get image dimensions
    height, width = image.shape

    # Check if dimensions are powers of two
    if not is_power_of_two(height) or not is_power_of_two(width):

        # Resize to nearest power of two
        new_height = int(nearest_power_of_two(height))
        new_width = int(nearest_power_of_two(width))
        image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

    return image

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='FFT Image Processing')
    parser.add_argument('-m', '--mode', type=int, choices=[1, 2, 3, 4], default=1, help='Mode of operation')
    parser.add_argument('-i', '--image', type=str, help='Image filename')

    args = parser.parse_args()

    # Load the default image if no image is specified
    image_file = args.image if args.image else 'moonlanding.png'
    image = load_image(image_file)

    # Process the image based on the selected mode
    if args.mode == 1:

        # for fast mode where the image is converted into its FFT form and displayed
        fast_mode(image)

    elif args.mode == 2:

        # for denoising where the image is denoised by applying an FFT, truncating high frequencies and then displayed
        denoise_image(image)

    elif args.mode == 3:

        # for compressing and plot the image
        compress_image(image)

    elif args.mode == 4:

        # for plotting the runtime graphs for the report
        plot_runtime_graphs()
