import cv2
import numpy as np
import os

# Set the path to the folder containing the images
folder_path = '/Users/<redacted>/Desktop/philo/Dataset_new2/Augmentation/bad-good/test/good'

# Get the list of image filenames from the specified folder
image_filenames = [os.path.join(folder_path, filename) for filename in os.listdir(folder_path)]

# Define the data augmentation transformations
transformations = {
    'flip_horizontal': lambda img: cv2.flip(img, 1),
    'flip_vertical': lambda img: cv2.flip(img, 0),
    'rotate_90': lambda img: cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE),
    'rotate_180': lambda img: cv2.rotate(img, cv2.ROTATE_180),
    'rotate_270': lambda img: cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE),
    'brightness_increase': lambda img: cv2.convertScaleAbs(img, alpha=1.5, beta=0),
    'brightness_decrease': lambda img: cv2.convertScaleAbs(img, alpha=0.5, beta=0),
    #'contrast_increase': lambda img: cv2.convertScaleAbs(img, alpha=1, beta=50),
    #'contrast_decrease': lambda img: cv2.convertScaleAbs(img, alpha=1, beta=-50),
    #'crop_center': lambda img: cv2.resize(img[img.shape[0]//4:img.shape[0]*3//4, img.shape[1]//4:img.shape[1]*3//4], (img.shape[1],img.shape[0])),
    'sharpen': lambda img: cv2.filter2D(img, -1, np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])),
    #'scale_up': lambda img: cv2.resize(cv2.resize(img, None, fx=1.5, fy=1.5), (img.shape[1],img.shape[0])),
    #'scale_down': lambda img: cv2.resize(cv2.resize(img, None, fx=0.5, fy=0.5), (img.shape[1],img.shape[0])),
    'blur': lambda img: cv2.GaussianBlur(img,(5,5),0),
    'add_noise': lambda img: (img + np.random.normal(0, 10, img.shape)).clip(0, 255).astype(np.uint8)
    #'skew_left': lambda img: cv2.warpAffine(img,np.float32([[1 , -0.5 , 0], [0 , 1 , 0]]),(img.shape[1],img.shape[0])),
    #'skew_right': lambda img: cv2.warpAffine(img,np.float32([[1 , 0.5 , 0], [0 , 1 , 0]]),(img.shape[1],img.shape[0])),
    #'mask_circle': lambda img: cv2.bitwise_and(img,img, mask=cv2.circle(np.zeros_like(img[:,:,0]),(img.shape[1]//2,img.shape[0]//2),min(img.shape[:2])//3,(255),-1)),
}

# Perform data augmentation on each image
for filename in image_filenames:
    print(f'Reading image {filename}...')
    
    # Read the image
    img = cv2.imread(filename)
    
    if img is None:
        print(f'Error reading image {filename}!')
        continue
    
    print(f'Successfully read image {filename}.')

    # Apply each transformation
    for transformation_name, transformation in transformations.items():
        print(f'Applying transformation {transformation_name} to image {filename}...')
        
        # Apply the transformation
        transformed_img = transformation(img)
        
        if transformed_img is None:
            print(f'Error applying transformation {transformation_name} to image {filename}!')
            continue
        
        print(f'Successfully applied transformation {transformation_name} to image {filename}.')

        # Save the transformed image
        base_name, ext = os.path.splitext(filename)
        new_filename = f'{base_name}_{transformation_name}{ext}'
        if not cv2.imwrite(new_filename, transformed_img):
            print(f'Error saving transformed image {new_filename}!')
            continue
        
        print(f'Successfully saved transformed image {new_filename}.')