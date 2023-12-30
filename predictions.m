clc
clear
% Specify the directory where the images are stored
img_dir = 'bad'; 

% Get a list of all files in the directory
img_files = dir(fullfile(img_dir, 'Obj7_*flip*.jpg')); 

% Loop over all image files
for idx = 1:length(img_files)
    % Read the image
    img = imread(fullfile(img_dir, img_files(idx).name));
    
    % Flip the image horizontally and vertically
    img_flipped_horizontally = flip(img, 2);
    img_flipped_vertically = flip(img, 1);
    
    % Save the flipped images with new names
    [~, name, ext] = fileparts(img_files(idx).name);
%     new_name_hor = sprintf('%s_flipH%s', name, ext);
%     new_name_ver = sprintf('%s_flipV%s', name, ext);
%     imwrite(img_flipped_horizontally, fullfile(img_dir, new_name_hor));
%     imwrite(img_flipped_vertically, fullfile(img_dir, new_name_ver));
    
    % Add Gaussian noise to the image
%     img_noisy = imnoise(img, 'gaussian');
%     new_name_noisy = sprintf('%s_noisy%s', name, ext);
%     imwrite(img_noisy, fullfile(img_dir, new_name_noisy));
    
    % Rotate the image by 30, 60, and 120 degrees and save
%     for angle = [30, 45, 60, 120, 150, 180, 210, 270] 
    for angle = [30, 180] 
%         Rotate the image
        img_rotated = imrotate(img, angle, 'bilinear', 'crop');
        
        % Create a new file name
        new_name = sprintf('%s_rot%d%s', name, angle, ext);
        
        % Save the rotated image
        imwrite(img_rotated, fullfile(img_dir, new_name));
    end
end
