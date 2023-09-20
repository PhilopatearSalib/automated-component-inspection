%apply on "best" folder
% Get the folder path where the images are stored
folder_path = uigetdir();
bmanual = false;
% Get all the image files in the folder
image_files = dir(fullfile(folder_path, 'ObJ1-bad*'));

% Loop through each image file and crop it
for i = 1:length(image_files)
    % Read the image
    img = imread(fullfile(folder_path, image_files(i).name));
    
    cropped_img = img;

%      if bmanual
%         % Crop the image using imcrop
%         cropped_img = imcrop(img);
%     else
%         win = centerCropWindow2d(size(img),[2500 2500]);
%         cropped_img = imcrop(img,win);

        % Resize the cropped image to 256x256
%     end

    % Resize the cropped image to 256x256
    resized_img = imresize(cropped_img, [512 512]);
    % Get the name for the cropped image from the user
%     name = inputdlg(sprintf('Enter a name for the cropped image %d:', i), 'Name', [1 50]);
    
    % Save the cropped image with the provided name
    imwrite(resized_img, fullfile(folder_path, image_files(i).name));
end


