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
    for m in range(M):
        dft[m, :] = dft_1d(image[m, :])

    # Apply 1D DFT to each column of the result
    for n in range(N):
        dft[:, n] = dft_1d(dft[:, n])

    return dft

def fft_1d(signal):

    # signal: 1D array-like object containing the input signal (time-domain).
    # return: 1D array representing the DFT (frequency-domain).

    N = len(signal)

    # Recursion's base case: when the length of the signal array (N) is 1 or less
    if N <= 1: 
        return signal

    # Cooley-Tukey dividing step, into even and odd (using array slicing... [start:stop:step])
    # Then call recursively on two halves, breaking down the problem into smaller sub-problems
    even = fft_1d(signal[0::2])
    odd = fft_1d(signal[1::2])

    # Prepare an array to hold the combined results
    combined = [0] * N

    for k in range(N // 2):

        # Calculate the complex exponential term for the odd part
        exp_term = np.exp(-2j * np.pi * k / N) * odd[k]

        # Combine the even and odd parts
        combined[k] = even[k] + exp_term
        combined[k + N // 2] = even[k] - exp_term

    return combined


def ifft_1d(signal):

    N = len(signal)
    if N <= 1: 
        return signal

    even = ifft_1d(signal[0::2])
    odd = ifft_1d(signal[1::2])

    combined = [0] * N

    for k in range(N // 2):

        # sign change
        exp_term = np.exp(2j * np.pi * k / N) * odd[k]
        combined[k] = even[k] + exp_term
        combined[k + N // 2] = even[k] - exp_term

    # Normalize by dividing each element by N
    return [x / N for x in combined]


# Compute the two-dimensional Fast Fourier Transform.
def fft_2d(image, mode):

    # image: 2D array-like object representing the grayscale image.
    # return: 2D array representing the FFT of the image.

    # Creates a MxN array of complex numbers, all initialized to 0
    M, N = image.shape
    fft = np.zeros((M, N), dtype=complex)

    if mode == "inverse":

        # Apply 1D FFT to each row
        for m in range(M):
            fft[m, :] = ifft_1d(image[m, :])

        # Apply 1D FFT to each column of the result
        for n in range(N):
            fft[:, n] = ifft_1d(fft[:, n])

    else:

        # Apply 1D FFT to each row
        for m in range(M):
            fft[m, :] = fft_1d(image[m, :])

        # Apply 1D FFT to each column of the result
        for n in range(N):
            fft[:, n] = fft_1d(fft[:, n])

    return fft


# Implement the FFT and display the frequency domain image
def fast_mode(image):

    # 1 - perform the FFT (break 2d into 1d)
    # 2 - output a 1 by 2 subplot of the original image next to its Fourier transform

    # Compute the 2D FFT using the custom implementation
    f_transform = fft_2d(image, "normal")

    # Log scaling
    log_scalled = np.log(np.abs(f_transform) + 1)

    _, ax = plt.subplots(1, 2)
    ax[0].imshow(image, cmap='gray')
    ax[0].set_title("Original Image")

    ax[1].imshow(log_scalled, norm=LogNorm(), cmap='gray')
    ax[1].set_title("FFT (Log Scaled)")

    plt.show()

# Apply a frequency filter to keep only low-frequency components.
# logic found: https://sbme-tutorials.github.io/2021/cv/notes/2_week2.html#:~:text=Discrete%20Fourier%20Transform%20(DFT),-Fourier%20transform%20is&text=Low%20frequency%20components%20are%20found,frequency%20components%20are%20in%20peripherals.
def low_pass_filter(f_transform, keep_fraction):

    # Shift the zero-frequency component to the center of the spectrum
    f_transform_shifted = np.fft.fftshift(f_transform)
    
    M, N = f_transform_shifted.shape

    # Calculate the number of rows and columns to keep
    rows_to_keep = int(M * keep_fraction)
    cols_to_keep = int(N * keep_fraction)

    # Create a mask with a central square/rectangle
    # Initialize the mask to be all zeros
    mask = np.zeros_like(f_transform_shifted, dtype=bool)

    row_start = M // 2 - rows_to_keep // 2
    row_end = row_start + rows_to_keep
    col_start = N // 2 - cols_to_keep // 2
    col_end = col_start + cols_to_keep

    mask[row_start:row_end, col_start:col_end] = True

    # Apply the mask to the Fourier Transform
    filtered_f_transform = np.zeros_like(f_transform_shifted)
    filtered_f_transform[mask] = f_transform_shifted[mask]

    f_ishifted = np.fft.ifftshift(filtered_f_transform)

    return f_ishifted

# Implement the denoising logic
def denoise_image(image):

    # 1 - perform the denoising
    #   1.1 - take the FFT of the image  
    #   1.2 - set all the high frequencies to zero 
    #   1.3 - invert to get back the filtered original
    # 2 - output a 1 by 2 subplot of the original image next to its denoised version

    # Take the fft
    f_transform = fft_2d(image, "normal")
    N, M = f_transform.shape

    f_transform = low_pass_filter(f_transform, 0.2)

    # Count the non-zero frequencies and calculate the fraction
    non_zeros = np.sum(f_transform != 0)
    total_coefficients = N * M
    fraction_non_zeros = non_zeros / total_coefficients

    # Compute the inverse FFT
    denoised_image = fft_2d(f_transform, "inverse").real

    print("Number of non-zero coefficients: " + str(non_zeros))
    print("Fraction of non-zero coefficients: " + str(fraction_non_zeros))

    # output a 1 by 2 subplot of the original image next to its denoised version
    _, ax = plt.subplots(1, 2)
    ax[0].imshow(image, cmap='gray')
    ax[0].set_title("Original Image")
    
    ax[1].imshow(denoised_image, cmap='gray')
    ax[1].set_title("Denoised Image")

    plt.show()


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
