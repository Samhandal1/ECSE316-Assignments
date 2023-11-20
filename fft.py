import numpy as np
import matplotlib.pyplot as plt
import argparse
import cv2

def fast_mode(image):
    """Fast mode - Display FFT of the image."""
    # Implement the FFT and display the frequency domain image

    # 1 - perform the FFT (break 2d into 1d)
    # 2 - output a 1 by 2 subplot of the original image next to its Fourier transform
    pass

def denoise_image(image):
    """Denoise the image using FFT."""
    # Implement the denoising logic

    # 1 - perform the denoising
    #   1.1 - take the FFT of the image  
    #   1.2 - set all the high frequencies to zero 
    #   1.3 - invert to get back the filtered original
    # 2 - output a 1 by 2 subplot of the original image next to its denoised version
    pass

def compress_image(image):
    """Compress the image and plot."""
    # Implement the compression logic

    # 1 - preform compression 
    #   1.1 - take the FFT of the image
    #   1.2 - setting some Fourier coefficients to zero... choose one of the following
    #       1.2.1 - threshold the coefficients’ magnitude and take only the largest percentile of them
    #       1.2.2 - you can keep all the coefficients of very low frequencies as well as a fraction of the largest coefficients from higher frequencies to also filter the image at the same time
    #   1.3 - inverse transform the modified Fourier coefficients
    # 2 - output a 2 by 3 subplot of the image at 6 different compression levels
    # 3 - print in the command line the number of non zeros that are in each of the 6 images
    pass

def plot_runtime_graphs():
    """Plot runtime graphs for the report."""
    # Implement runtime analysis and plotting

    # print in the command line the means and variances of the runtime of your algorithms versus the problem size
    pass

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='FFT Image Processing')
    parser.add_argument('-m', '--mode', type=int, choices=[1, 2, 3, 4], default=1, help='Mode of operation')
    parser.add_argument('-i', '--image', type=str, help='Image filename')

    args = parser.parse_args()

    # Load the default image if no image is specified
    image_file = args.image if args.image else 'moonlanding.png'
    image = cv2.imread(image_file)

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
