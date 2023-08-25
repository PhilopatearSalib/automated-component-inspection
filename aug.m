% Define the paths to the train and val folders
train_path = 'train';
val_path = 'val';

% Read in the images from the train folder
train_files = dir(fullfile(train_path, '*.jpg'));
train_images = cell(length(train_files), 1);
for i = 1:length(train_files)
    train_images{i} = fullfile(train_path, train_files(i).name);
end

% Read in the images from the val folder
val_files = dir(fullfile(val_path, '*.jpg'));
val_images = cell(length(val_files), 1);
for i = 1:length(val_files)
    val_images{i} = fullfile(val_path, val_files(i).name);
end

% Create imageDatastore objects for the train and val sets
train_datastore = imageDatastore(train_images);
val_datastore = imageDatastore(val_images);

% Create augmentedImageDatastore objects for the train and val sets
train_aug_datastore = augmentedImageDatastore([256 256], 'DataAugmentation', train_datastore);
val_aug_datastore = augmentedImageDatastore([256 256], 'DataAugmentation', val_datastore);