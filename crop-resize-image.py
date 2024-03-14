import os
import argparse
from PIL import Image

def run(input: str,
        output: str,
        crop_from: str,
        imgsz: int,
        prefix: str,
        suffix: str = 'cropped-resized'
    ):
    """
    Process the input image or folder of images by cropping and resizing them.

    Args:
        input (str): Path to the input image file or folder of images.
        output (str): Path to the output directory where processed images will be saved.
        crop_from (str): Crop position for the images. Can be 'top', 'bottom', 'left',
        'right', or 'center'.
        imgsz (int): Size of the output images in pixels.
        prefix (str): Prefix to be added to the output image filenames.
        suffix (str, optional): Suffix to be added to the output image filenames.
        Defaults to 'cropped-resized'.

    Returns:
        None
    """
    processed = 0

    # check if input is a file
    if os.path.isfile(input):
        input_file = input

        # Check if the file is an image
        if is_image_file(input_file):
            # Get output filename
            output_file = get_output_filename(input_file, output, prefix, suffix)

            # Create the output directory if it doesn't exist
            output_dir = os.path.dirname(output_file)
            os.makedirs(output_dir, exist_ok=True)

            # Process the single image file
            if process_image(input_file, output_file, crop_from, imgsz):
                processed = 1

        else:
            print(f"{input} is not a valid image file.")

    # Check if input is a folder
    elif os.path.isdir(input):
        input_dir = os.path.normpath(input)

        # Process all image files in the folder
        output_dir = get_output_dir(input_dir, output, suffix)

        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        for file in os.listdir(input_dir):
            input_file = os.path.join(input, file)
            if is_image_file(input_file):
                if prefix:
                    file = f"{prefix}-{file}"
                output_file = os.path.join(output_dir, file)
                if process_image(input_file, output_file, crop_from, imgsz):
                    processed += 1
    else:
        print("Input should be a valid image file or a folder.")

    print(f"{processed} image{'s' if processed>1 else ''} processed")

def is_image_file(file_path):
    """
    Check if a file path corresponds to an image file.

    Args:
        file_path (str): The path of the file to check.

    Returns:
        bool: True if the file is an image file, False otherwise.
    """
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    return any(file_path.lower().endswith(ext) for ext in image_extensions)

def process_image(input_file, output_file, crop_from, size):
    """
    Process the input image by cropping and resizing it.

    Args:
        input_file (str): The path to the input image file.
        output_file (str): The path to save the modified image.
        crop_from (tuple): The coordinates to crop the image from (left, upper, right, lower).
        size (int): The desired width of the resized image.

    Returns:
        bool: True if the image was processed and saved successfully, False otherwise.
    """
    try:
        # Load the image
        image = Image.open(input_file)

        # Perform cropping and resizing operations on the image here
        cropped_image = crop_image(image, crop_from)
        resized_image = resize_image(cropped_image, width=size)

        # Save the modified image
        resized_image.save(output_file)

        print(f"Saved {output_file}")
        return True

    except Exception as e:
        print(str(e))
        return False

def get_output_filename(input_file, output, prefix, suffix):
    """
    Constructs the output filename based on the input file, output path, prefix, and suffix.

    Args:
        input_file (str): The path of the input file.

        output (str or None): The path of the output file or folder. If None, the output file
        will be saved in the same directory as the input file.

        prefix (str): The prefix to be added to the filename.

        suffix (str): The suffix to be added to the filename.

    Returns:
        str: The output filename.

    """
    base_name = os.path.basename(input_file)
    name, ext = os.path.splitext(base_name)
    filename = f"{prefix}-{name}" if prefix else name
    filename = f"{filename}-{suffix}{ext}" if suffix else f"{filename}{ext}"
    if output is None:
        output_dir = os.path.dirname(input_file)
        return os.path.join(output_dir, filename)
    # output is a file
    elif os.path.splitext(output)[1]:
        return output
    # output is a folder
    return os.path.join(output, filename)

def get_output_dir(input_dir, output, suffix):
    """
    Get the output directory based on the input directory, output name, and suffix.

    Parameters:
        input_dir (str): The input directory.
        output (str): The output name.
        suffix (str): The suffix to be appended to the output directory.

    Returns:
        str: The output directory.
    """
    if output and not os.path.splitext(output)[1]:
        return output
    else:
        return f"{input_dir}-{suffix}"

def crop_image(image, crop_from):
    """
    Crop the input image based on the specified cropping position.

    Args:
        image (PIL.Image.Image): The input image to be cropped.

        crop_from (str): The position from which to crop the image. Allowed values are 'none'
        , 'left', 'middle', 'right'.

    Returns:
        PIL.Image.Image: The cropped image.
    """
    if crop_from == 'none':
        return image

    # Get the width and height of the original image
    width, height = image.size

    # Calculate the new width and height for cropping
    crop_size = min(width, height)
    new_width, new_height = crop_size, crop_size

    # Calculate the top-left coordinates for cropping
    if crop_from == 'left':
        left = 0
    elif crop_from == 'middle':
        left = (width - new_width) // 2
    elif crop_from == 'right':
        left = width - new_width
    else:
        raise ValueError(f"Invalid crop_from value '{crop_from}'. Allowed values are 'left'" +
                         ", 'middle', 'right'.")

    top = height - new_height
    right = left + new_width
    bottom = height

    # Crop the image based on the specified coordinates
    return image.crop((left, top, right, bottom))

def resize_image(image, width=None, height=None):
    """
    Resize the given image while maintaining the aspect ratio.

    Args:
        image (PIL.Image.Image): The image to be resized.

        width (int, optional): The desired width of the resized image. If not specified, the
        width will be calculated based on the specified height while maintaining the aspect
        ratio. Default is None.

        height (int, optional): The desired height of the resized image. If not specified, the
        height will be calculated based on the specified width while maintaining the aspect
        ratio. Default is None.

    Returns:
        PIL.Image.Image: The resized image.

    Raises:
        ValueError: If both width and height are specified, or if neither width nor height are
        specified.
    """
    # Get the original width and height
    w, h = image.size

    # Calculate the new width and height while maintaining the aspect ratio
    if width is not None and height is None:
        # Resize based on width
        new_width = width
        new_height = int(h * (new_width / w))
    elif width is None and height is not None:
        # Resize based on height
        new_height = height
        new_width = int(w * (new_height / h))
    else:
        raise ValueError("Either width or height should be specified, not both or none.")

    # Resize the image
    return image.resize((new_width, new_height))

def parse_opt():
    """
    Parse command line arguments for image cropping & resizing tool.

    Returns:
        opt (argparse.Namespace): Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description='Image cropping & resizing tool')
    parser.add_argument('--input', type=str, required=True, help='input of image file or folder')
    parser.add_argument('--output', type=str, default=None, help='output of image file or folder ' +
                        '(Optional)')
    parser.add_argument('--crop-from', type=str, default='middle', help='reference point to crop ' +
                        'image into square dimension (i.e. none, left, middle, right)')
    parser.add_argument('--imgsz', type=int, default=640, help='width & height (pixels) of output' +
                        ' image. Default 640')
    parser.add_argument('--prefix', type=str, default=None, help="filename prefix of output image" +
                        ". Default ''")
    opt = parser.parse_args()
    return opt

def main(opt):
    """
    Main function to run the program.

    Args:
        opt: An object containing the program options.

    Returns:
        None
    """
    run(**vars(opt))

if __name__ == '__main__':
    opt = parse_opt()
    main(opt)
